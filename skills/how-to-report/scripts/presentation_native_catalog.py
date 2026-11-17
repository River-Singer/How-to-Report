"""Portable source-native atoms and deterministic native composition.

The catalogue keeps one compressed, structured configuration pack per source.
Objects retain group ancestry; extraction never substitutes a rendered image.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
import os
from pathlib import Path
import posixpath
import re
import shutil
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED, BadZipFile

import presentation_native as n

SCHEMA = "how-to-report.native-catalog.v1"
EMU = 914400
NativeCatalogError = n.NativeRoundtripError


def _json(value):
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode("utf-8")


def _root(config):
    return next(x for x in config["nodes"] if x.get("kind") == "element")


def _elements(node, namespace=None, local=None):
    return [c for c in node.get("children", []) if c.get("kind") == "element"
            and (namespace is None or c.get("ns") == namespace)
            and (local is None or n._local(c) == local)]


def _find(config, namespace, local):
    return next((v for _, v in n._walk(config) if n._is(v, namespace, local)), None)


def _element(tag, ns, attrs=None, children=None, attr_ns=None):
    return {"kind": "element", "tag": tag, "ns": ns, "attrs": attrs or {},
            "attr_ns": attr_ns or {}, "children": children or []}


def _config(part, root):
    return {"schema": n.XML_SCHEMA, "part": part, "version": "1.0", "standalone": True, "nodes": [root]}


def _coalesce_text(config):
    # Removing a sibling element makes its neighboring XML text nodes adjacent;
    # XML parsers return these as one text node on the next read.
    def visit(node):
        if "children" not in node:return
        merged=[]
        for child in node["children"]:
            visit(child)
            if merged and child.get("kind")=="text" and merged[-1].get("kind")=="text":merged[-1]["value"]+=child["value"]
            else:merged.append(child)
        node["children"]=merged
    for node in config["nodes"]:visit(node)


def _matmul(a, b):
    return (a[0]*b[0]+a[2]*b[1], a[1]*b[0]+a[3]*b[1],
            a[0]*b[2]+a[2]*b[3], a[1]*b[2]+a[3]*b[3],
            a[0]*b[4]+a[2]*b[5]+a[4], a[1]*b[4]+a[3]*b[5]+a[5])


def _point(m, x, y):
    return m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5]


def _rotation(transform):
    coords, attrs = transform["coordinates"], transform["attributes"]
    off, ext = coords.get("off", {}), coords.get("ext", {})
    cx, cy = off.get("x", 0)+ext.get("cx", 0)/2, off.get("y", 0)+ext.get("cy", 0)/2
    angle = math.radians(int(attrs.get("rot", "0"))/60000)
    fx = -1 if attrs.get("flipH") in {"1", "true"} else 1
    fy = -1 if attrs.get("flipV") in {"1", "true"} else 1
    a, b, c, d = math.cos(angle)*fx, math.sin(angle)*fx, -math.sin(angle)*fy, math.cos(angle)*fy
    return (a, b, c, d, cx-a*cx-c*cy, cy-b*cx-d*cy)


def _bounds(objects):
    matrices, bounds = {}, {}
    identity = (1, 0, 0, 1, 0, 0)
    for obj in objects:
        path = tuple(obj["binding"])
        ancestors = [p for p in matrices if len(p) < len(path) and path[:len(p)] == p]
        parent = matrices[max(ancestors, key=len)] if ancestors else identity
        t = obj["transform"]
        if not t or not {"off", "ext"} <= set(t["coordinates"]):
            bounds[obj["instance_id"]] = None
            continue
        c = t["coordinates"]
        off, ext = c["off"], c["ext"]
        m = _matmul(parent, _rotation(t))
        corners = [_point(m, off["x"]+x*ext["cx"], off["y"]+y*ext["cy"]) for x,y in ((0,0),(1,0),(1,1),(0,1))]
        xs, ys = zip(*corners)
        bounds[obj["instance_id"]] = [min(xs), min(ys), max(xs)-min(xs), max(ys)-min(ys)]
        if obj["type"] == "grpSp" and {"chOff", "chExt"} <= set(c):
            child, size = c["chOff"], c["chExt"]
            if not size["cx"] or not size["cy"]:
                continue
            sx, sy = ext["cx"]/size["cx"], ext["cy"]/size["cy"]
            matrices[path] = _matmul(m, (sx,0,0,sy,off["x"]-sx*child["x"],off["y"]-sy*child["y"]))
    return bounds


def _asset_id(source_id, number, instance=None):
    prefix = f"native:{source_id}:p{number:04d}"
    return prefix+":page" if instance is None else prefix+":o"+hashlib.sha256(instance.encode()).hexdigest()[:12]


def _page_assets(source, record, slide, size, preview, tree=None):
    objects = slide["objects"]
    boxes = _bounds(objects)
    ids = {o["instance_id"]: _asset_id(source["id"], record["number"], o["instance_id"]) for o in objects}
    page_id = _asset_id(source["id"], record["number"])
    result = []
    for obj in [None, *objects]:
        selected = objects if obj is None else [o for o in objects if o["binding"][:len(obj["binding"])] == obj["binding"]]
        asset_id = page_id if obj is None else ids[obj["instance_id"]]
        parent = None
        if obj is not None:
            ancestors = [o for o in objects if len(o["binding"]) < len(obj["binding"]) and obj["binding"][:len(o["binding"])] == o["binding"]]
            parent = ids[max(ancestors, key=lambda o: len(o["binding"]))["instance_id"]] if ancestors else page_id
        children = []
        for child in selected:
            if child is obj:
                continue
            # Immediate hierarchy follows binding paths, not potentially duplicated fallback IDs.
            parents = [o for o in objects if len(o["binding"]) < len(child["binding"]) and child["binding"][:len(o["binding"])] == o["binding"]]
            immediate = max(parents,key=lambda o:len(o["binding"])) if parents else None
            if immediate is obj:
                children.append(ids[child["instance_id"]])
        bbox = [0,0,*size] if obj is None else boxes[obj["instance_id"]]
        hidden = bool(obj and any(o["hidden"] for o in objects if obj["binding"][:len(o["binding"])]==o["binding"]))
        conditional = bool(obj and obj["conditional_branches"])
        selected_ids = {o["id"] for o in selected}
        disconnected = any(c.get("id") not in selected_ids for o in selected for c in o["connections"])
        slots = [{"id": f"t{i}", "text": run["text"], "object_id": o["id"], "instance_id": o["instance_id"], "binding": run["binding"]}
                 for i, (o,run) in enumerate((o,r) for o in selected if not o["hidden"] for r in o["text_runs"])]
        available = not hidden and not conditional and not disconnected and (obj is None or bbox is not None)
        visual=n._node(tree,obj["binding"]) if obj is not None and tree is not None else _root(tree) if tree is not None else None
        style_flags=[];gradient_count=0;fingerprint=None
        if visual is not None:
            locals_=[n._local(v) for _,v in n._walk(_config("visual",visual))]
            gradient_count=locals_.count("gradFill")
            style_flags=[flag for local,flag in (("gradFill","gradient"),("solidFill","solid"),("custGeom","custom-geometry"),("blipFill","image"),("outerShdw","shadow"),("chart","native-chart")) if local in locals_]
            def stripped(node,top=False):
                if node.get("kind")!="element":return node
                attrs={k:v for k,v in node["attrs"].items() if not(n._local(node)=="cNvPr" and k in {"id","name","descr","title"})}
                children=[] if n._is(node,n.A,"t") else [stripped(c) for c in node["children"]]
                return {"tag":node["tag"],"ns":node["ns"],"attrs":attrs,"children":children}
            fingerprint=n._hash(_json({"source":source["source_sha256"],"structure":stripped(visual)}))
        label=" ".join(s["text"] for s in slots)[:80]
        result.append({"id":asset_id,"name":source["source"]["name"]+f" · {record['number']}" if obj is None else (label if obj["type"]=="grpSp" and label else obj["name"] or obj["type"]),
                       "kind":"page" if obj is None else "group" if obj["type"]=="grpSp" else "atom",
                       "source_id":source["id"],"slide_number":record["number"],"parent_id":parent,"children":children,
                       "object_id":None if obj is None else obj["id"],"instance_id":None if obj is None else obj["instance_id"],
                       "type":"slide" if obj is None else obj["type"],"binding":None if obj is None else obj["binding"],
                       "text_excerpt":" ".join(s["text"] for s in slots)[:300],"hidden":hidden,"conditional":conditional,
                       "visible_default":not hidden and not conditional,"executable":available,
                       "geometry_method":"source-native-preservation; composed placement computed by grid",
                       "bbox_emu":bbox,"preview":{"image":preview,"crop_emu":bbox,"slide_emu":size},
                       "style_flags":style_flags,"gradient_count":gradient_count,"structure_fingerprint":fingerprint,"duplicate_of":None,
                       "fingerprint_scope":"within source; native local geometry/style/relationships; object IDs/names and text values ignored; translations retained",
                       "capabilities":{"text_slots":slots,"native_editable":True,"automatic_reflow":False,"grid_composition":"validated-at-instantiation"},
                       "limitations":(["external connector endpoints"] if disconnected else [])+(["hidden source object"] if hidden else [])+(["conditional compatibility representation"] if conditional else [])+(["inherited geometry requires original page"] if bbox is None else [])})
    return {"slide":{"number":record["number"],"width_emu":size[0],"height_emu":size[1]},"assets":result}


def build_native_catalog(sources, output):
    """Freeze portable compact source packs and per-page atom indices."""
    output = n._new_output(output)
    if not isinstance(sources,list) or not sources:
        raise NativeCatalogError("sources must be a nonempty array")
    source_ids = [s.get("id") for s in sources if isinstance(s,dict)]
    if len(source_ids)!=len(sources) or len(set(source_ids))!=len(source_ids) or any(not isinstance(s,str) or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}",s) for s in source_ids):
        raise NativeCatalogError("source IDs must be unique lowercase path-safe names")
    output.parent.mkdir(parents=True,exist_ok=True)
    catalog={"schema":SCHEMA,"sources":[],"counts":{"page":0,"group":0,"atom":0,"hidden":0,"conditional":0,"duplicate":0,"unique_structure":0}}
    seen={}
    with tempfile.TemporaryDirectory(prefix=".htr-native-catalog-",dir=output.parent) as temporary:
        stage=Path(temporary)/"catalog"; stage.mkdir()
        (stage/"sources").mkdir(); (stage/"assets").mkdir()
        for spec in sources:
            project=Path(spec["project"])
            manifest_path=n._local_file(project,"native-project.json")
            raw_manifest=manifest_path.read_bytes(); manifest=n._json_load(raw_manifest,manifest_path)
            if not isinstance(manifest,dict) or manifest.get("schema")!=n.SCHEMA:
                raise NativeCatalogError("unsupported native source project")
            source={"id":spec["id"],"source":manifest["source"],"source_sha256":manifest["source"]["sha256"],
                    "pack":f"sources/{spec['id']}.zip","pages":[]}
            source_dir=stage/"assets"/spec["id"];source_dir.mkdir()
            parts={p["name"]:p for p in manifest["parts"]}
            if len(parts)!=len(manifest["parts"]):raise NativeCatalogError("duplicate native parts")
            pres=n._read_json(n._local_file(project,parts[manifest["presentation_part"]]["config"]))
            size_node=_find(pres,n.P,"sldSz")
            if size_node is None:raise NativeCatalogError("source has no slide size")
            size=[int(size_node["attrs"][k]) for k in ("cx","cy")]
            with ZipFile(stage/source["pack"],"w",ZIP_DEFLATED,compresslevel=6) as pack:
                pack.writestr("native-project.json",_json(manifest))
                written=set()
                for part in manifest["parts"]:
                    relative=part.get("config") if part["kind"]=="xml" else part["asset"]
                    if relative in written:continue
                    payload=n._local_file(project,relative).read_bytes()
                    if part["kind"]=="xml":
                        data=n._json_load(payload,relative)
                        if not isinstance(data,dict) or data.get("part")!=part["name"] or data.get("schema")!=n.XML_SCHEMA:
                            raise NativeCatalogError("source XML identity mismatch")
                        payload=_json(data)
                    elif n._hash(payload)!=part["sha256"]:raise NativeCatalogError("source asset hash mismatch")
                    pack.writestr(relative,payload); written.add(relative)
                for record in manifest["slides"]:
                    slide=n._read_json(n._local_file(project,record["config"]))
                    pack.writestr(record["config"],_json(slide))
                    preview_dir=spec.get("preview_dir")
                    image=Path(preview_dir)/f"slide-{record['number']:02d}.png" if preview_dir else None
                    preview=str(image.resolve()) if image and image.is_file() else None
                    page=_page_assets(source,record,slide,size,preview,n._read_json(n._local_file(project,parts[record["part"]]["config"])))
                    for asset in page["assets"]:
                        fingerprint=asset["structure_fingerprint"]
                        if fingerprint in seen:asset["duplicate_of"]=seen[fingerprint];catalog["counts"]["duplicate"]+=1
                        elif fingerprint:seen[fingerprint]=asset["id"];catalog["counts"]["unique_structure"]+=1
                    relative=f"assets/{spec['id']}/p{record['number']:04d}.json"
                    (stage/relative).write_bytes(_json(page))
                    source["pages"].append({"number":record["number"],"index":relative,"asset_count":len(page["assets"]),"sha256":n._hash(_json(page))})
                    for asset in page["assets"]:
                        catalog["counts"][asset["kind"]]+=1
                        for key in ("hidden","conditional"):catalog["counts"][key]+=int(asset[key])
            source["pack_sha256"]=_file_hash(stage/source["pack"])
            catalog["sources"].append(source)
            if manifest_path.read_bytes()!=raw_manifest:raise NativeCatalogError("source manifest changed during catalog build")
        (stage/"catalog.json").write_bytes(_json(catalog))
        n._new_output(output);os.rename(stage,output)
    return {"schema":SCHEMA,"catalog":str(output),"source_count":len(sources),"counts":catalog["counts"]}


def _file_hash(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda:stream.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()


def refresh_native_catalog(catalog,output):
    """Enrich indices using existing compact packs, without re-importing sources."""
    root,data=_catalog(catalog);output=n._new_output(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    result={"schema":SCHEMA,"sources":[],"counts":{"page":0,"group":0,"atom":0,"hidden":0,"conditional":0,"duplicate":0,"unique_structure":0}}
    seen={}
    with tempfile.TemporaryDirectory(prefix=".htr-catalog-refresh-",dir=output.parent) as temporary:
        stage=Path(temporary)/"catalog";stage.mkdir();(stage/"sources").mkdir()
        for source in data["sources"]:
            updated=copy.deepcopy(source);updated["pages"]=[]
            (stage/"assets"/source["id"]).mkdir(parents=True)
            pack=_Pack(root,source)
            try:
                shutil.copyfile(n._local_file(root,source["pack"]),stage/source["pack"])
                if _file_hash(stage/source["pack"])!=source["pack_sha256"]:raise NativeCatalogError("source pack changed during refresh")
                pres=pack.tree(pack.manifest["presentation_part"]);size_node=_find(pres,n.P,"sldSz");size=[int(size_node["attrs"][k]) for k in ("cx","cy")]
                for i,record in enumerate(pack.manifest["slides"]):
                    old=_page(root,source["pages"][i]);preview=old["assets"][0]["preview"]["image"]
                    slide=n._json_load(pack.zip.read(record["config"]),record["config"])
                    tree=pack.tree(record["part"])
                    page=_page_assets(source,record,slide,size,preview,tree)
                    for asset in page["assets"]:
                        fingerprint=asset["structure_fingerprint"]
                        if fingerprint in seen:asset["duplicate_of"]=seen[fingerprint];result["counts"]["duplicate"]+=1
                        elif fingerprint:seen[fingerprint]=asset["id"];result["counts"]["unique_structure"]+=1
                        result["counts"][asset["kind"]]+=1
                        for key in ("hidden","conditional"):result["counts"][key]+=int(asset[key])
                    relative=source["pages"][i]["index"];payload=_json(page);(stage/relative).write_bytes(payload)
                    updated["pages"].append({"number":record["number"],"index":relative,"asset_count":len(page["assets"]),"sha256":n._hash(payload)})
                    pack.cache.pop(record["part"],None)
            finally:pack.close()
            result["sources"].append(updated)
        (stage/"catalog.json").write_bytes(_json(result));n._new_output(output);os.rename(stage,output)
    return {"catalog":str(output),"counts":result["counts"],"source_count":len(result["sources"])}


def _catalog(path):
    root=Path(path);root=root.parent if root.name=="catalog.json" else root
    data=n._read_json(n._local_file(root,"catalog.json"))
    if not isinstance(data,dict) or data.get("schema")!=SCHEMA:raise NativeCatalogError("unsupported native catalog")
    return root,data


def _page(root,record):
    payload=n._local_file(root,record["index"]).read_bytes()
    if n._hash(payload)!=record["sha256"]:raise NativeCatalogError("catalog page index hash mismatch")
    return n._json_load(payload,record["index"])


def list_native_assets(catalog, query=None, kind=None, source=None, offset=0, limit=50, include_hidden=False):
    root,data=_catalog(catalog)
    if type(offset)is not int or offset<0 or type(limit)is not int or not 1<=limit<=100:
        raise NativeCatalogError("offset must be nonnegative; limit must be 1..100")
    found=[]
    for src in data["sources"]:
        if source and src["id"]!=source:continue
        for page in src["pages"]:
            for asset in _page(root,page)["assets"]:
                if not include_hidden and not asset["visible_default"]:continue
                if kind and asset["kind"]!=kind:continue
                if query and query.casefold() not in (asset["id"]+" "+asset["name"]+" "+asset["text_excerpt"]).casefold():continue
                found.append(asset)
    found.sort(key=lambda a:(bool(a.get("gradient_count")),bool(a.get("duplicate_of")),not a["executable"]))
    return {"total":len(found),"offset":offset,"limit":limit,"items":found[offset:offset+limit]}


def describe_native_asset(catalog,asset_id):
    root,data=_catalog(catalog)
    match=re.fullmatch(r"native:([a-z0-9-]+):p(\d+):(page|o[0-9a-f]{12})",asset_id or "")
    if not match:raise NativeCatalogError("invalid native asset ID")
    source=next((s for s in data["sources"] if s["id"]==match[1]),None)
    record=next((p for p in source["pages"] if p["number"]==int(match[2])),None) if source else None
    if record is None:raise NativeCatalogError("native asset not found")
    return next((a for a in _page(root,record)["assets"] if a["id"]==asset_id),None) or _missing_asset()


def _missing_asset():
    raise NativeCatalogError("native asset not found")


class _Pack:
    def __init__(self,root,source):
        path=n._local_file(root,source["pack"])
        if _file_hash(path)!=source["pack_sha256"]:raise NativeCatalogError("source pack hash mismatch")
        self.zip=ZipFile(path);self.manifest=n._json_load(self.zip.read("native-project.json"),"manifest")
        self.parts={p["name"]:p for p in self.manifest["parts"]};self.cache={}
    def tree(self,part):
        if part not in self.cache:
            p=self.parts[part]
            if p["kind"]!="xml":raise NativeCatalogError("expected structured XML part")
            self.cache[part]=n._json_load(self.zip.read(p["config"]),part)
        return self.cache[part]
    def rels(self,part):
        name=_rels_name(part)
        return self.tree(name) if name in self.parts else None
    def close(self):self.zip.close()


def _rels_name(part):
    return posixpath.join(posixpath.dirname(part),"_rels",posixpath.basename(part)+".rels")


def _target(owner,target):
    from urllib.parse import unquote,urlsplit
    parsed=urlsplit(target)
    return n._part_path(posixpath.normpath(unquote(parsed.path).lstrip("/") if parsed.path.startswith("/") else posixpath.join(posixpath.dirname(owner),unquote(parsed.path))))


def _retain_shape(tree,asset):
    if asset["kind"]=="page":return tree
    binding=asset["binding"]
    def prune(node,path):
        for i in range(len(node.get("children",[]))-1,-1,-1):
            child=node["children"][i];p=path+[i]
            if child.get("ns")==n.P and n._local(child) in n.SHAPES:
                if not (p[:len(binding)]==binding or binding[:len(p)]==p):
                    node["children"].pop(i);continue
            if child.get("kind")=="element":prune(child,p)
    for i,node in enumerate(tree["nodes"]):prune(node,[i])
    return tree


def _prune_slide_rels(tree,rels):
    if rels is None:return None
    used={v for _,node in n._walk(tree) for k,v in node.get("attrs",{}).items() if node.get("attr_ns",{}).get(k)==n.R}
    root=_root(rels)
    root["children"]=[r for r in root["children"] if not n._is(r,n.REL,"Relationship") or r["attrs"].get("Id") in used or r["attrs"].get("Type")==n.R+"/slideLayout"]
    return rels


def _selected(pack,asset,texts):
    record=pack.manifest["slides"][asset["slide_number"]-1]
    tree=copy.deepcopy(pack.tree(record["part"]))
    slide=n._json_load(pack.zip.read(record["config"]),record["config"])
    n._apply_slide({record["part"]:tree},slide,record)
    slots={s["id"]:s for s in asset["capabilities"]["text_slots"]}
    if not isinstance(texts,dict) or set(texts)-set(slots):raise NativeCatalogError("unknown text slot")
    for key,value in texts.items():
        if not isinstance(value,str) or "\n" in value or "\r" in value:raise NativeCatalogError("text slots accept single-run strings only")
        if len(value)>max(len(slots[key]["text"]),1):raise NativeCatalogError("longer text needs a reflow-capable component")
        n._node(tree,slots[key]["binding"])["children"]=[{"kind":"text","value":value}]
    _retain_shape(tree,asset)
    rels=_prune_slide_rels(tree,copy.deepcopy(pack.rels(record["part"])))
    return record["part"],tree,rels


def _closure(pack,seeds,overrides):
    collected={}; queue=list(seeds)
    while queue:
        part=queue.pop()
        if part in collected:continue
        if part not in pack.parts:raise NativeCatalogError("missing native dependency: "+part)
        p=pack.parts[part]
        if p["kind"]=="xml":collected[part]=copy.deepcopy(overrides.get(part,pack.tree(part)))
        else:
            payload=pack.zip.read(p["asset"])
            if n._hash(payload)!=p["sha256"]:raise NativeCatalogError("native asset checksum mismatch")
            collected[part]=payload
        relname=_rels_name(part)
        if relname in pack.parts:
            rels=copy.deepcopy(overrides.get(relname,pack.tree(relname)));collected[relname]=rels
            for rel in _elements(_root(rels),n.REL,"Relationship"):
                a=rel["attrs"]
                if a.get("TargetMode")!="External":queue.append(_target(part,a["Target"]))
    return collected


def _relation(rid,kind,target,external=False):
    a={"Id":rid,"Type":kind,"Target":target}
    if external:a["TargetMode"]="External"
    return _element("Relationship",n.REL,a)


def _rels_config(part,rows):
    return _config(part,_element("Relationships",n.REL,{"xmlns":n.REL},rows,{"xmlns":"http://www.w3.org/2000/xmlns/"}))


def _single(pack,asset,texts):
    part,slide,rels=_selected(pack,asset,texts)
    presentation=pack.manifest["presentation_part"]
    pres=copy.deepcopy(pack.tree(presentation));presrels=copy.deepcopy(pack.rels(presentation))
    slide_rels=[r for r in _elements(_root(presrels),n.REL,"Relationship") if r["attrs"]["Type"]==n.R+"/slide"]
    keep=next(r for r in slide_rels if _target(presentation,r["attrs"]["Target"])==part)
    rid=keep["attrs"]["Id"]
    _root(presrels)["children"]=[r for r in _root(presrels)["children"] if r not in slide_rels or r is keep]
    ids=_find(pres,n.P,"sldIdLst")
    ids["children"]=[r for r in ids["children"] if r.get("attrs",{}).get("r:id")==rid]
    # Custom shows and sections reference removed slide identities.
    root=_root(pres);root["children"]=[c for c in root["children"] if n._local(c) not in {"custShowLst","extLst"}]
    overrides={presentation:pres,_rels_name(presentation):presrels,part:slide}
    if rels is not None:overrides[_rels_name(part)]=rels
    # A master links back to every layout that it offers. Following that cycle
    # unfiltered drags unrelated layouts/media into a one-atom dependency pack.
    layout_rel=next((r for r in _elements(_root(rels),n.REL,"Relationship") if r["attrs"]["Type"]==n.R+"/slideLayout"),None) if rels else None
    if layout_rel is not None:
        layout_part=_target(part,layout_rel["attrs"]["Target"])
        layout_rels=pack.rels(layout_part)
        master_rel=next((r for r in _elements(_root(layout_rels),n.REL,"Relationship") if r["attrs"]["Type"]==n.R+"/slideMaster"),None) if layout_rels else None
        if master_rel is not None:
            master_part=_target(layout_part,master_rel["attrs"]["Target"])
            master=copy.deepcopy(pack.tree(master_part));master_rels=copy.deepcopy(pack.rels(master_part))
            retained_master_ids=set()
            for r in list(_elements(_root(presrels),n.REL,"Relationship")):
                if r["attrs"]["Type"]!=n.R+"/slideMaster":continue
                if _target(presentation,r["attrs"]["Target"])==master_part:retained_master_ids.add(r["attrs"]["Id"])
                else:_root(presrels)["children"].remove(r)
            masters=_find(pres,n.P,"sldMasterIdLst")
            if masters:masters["children"]=[r for r in masters["children"] if r.get("attrs",{}).get("r:id") in retained_master_ids]
            retained_layout_ids=set()
            if master_rels:
                for r in list(_elements(_root(master_rels),n.REL,"Relationship")):
                    if r["attrs"]["Type"]!=n.R+"/slideLayout":continue
                    if _target(master_part,r["attrs"]["Target"])==layout_part:retained_layout_ids.add(r["attrs"]["Id"])
                    else:_root(master_rels)["children"].remove(r)
                overrides[_rels_name(master_part)]=master_rels
            layouts=_find(master,n.P,"sldLayoutIdLst")
            if layouts:layouts["children"]=[r for r in layouts["children"] if r.get("attrs",{}).get("r:id") in retained_layout_ids]
            overrides[master_part]=master
    entries=_closure(pack,[presentation],overrides)
    entries["_rels/.rels"]=_rels_config("_rels/.rels",[_relation("rId1",n.R+"/officeDocument","/"+presentation)])
    entries["[Content_Types].xml"]=_content_config([(pack,entries)])
    return entries


def _content_config(groups):
    overrides={}
    for pack,entries in groups:
        types=n._content_types({"[Content_Types].xml":pack.tree("[Content_Types].xml")},set(pack.parts))
        for part in entries:
            if part in types:overrides[part]=types[part]
    rows=[_element("Override",n.CT,{"PartName":"/"+name,"ContentType":mime}) for name,mime in sorted(overrides.items()) if name!="[Content_Types].xml"]
    return _config("[Content_Types].xml",_element("Types",n.CT,{"xmlns":n.CT},rows,{"xmlns":"http://www.w3.org/2000/xmlns/"}))


def instantiate_native_assets(catalog,asset_ids,output,columns=None,texts=None):
    """Instantiate source-native atoms; grid placement is calculated by the engine."""
    output=n._new_output(output)
    if not isinstance(asset_ids,list) or not 1<=len(asset_ids)<=16 or any(not isinstance(a,str) for a in asset_ids):raise NativeCatalogError("select 1..16 native assets")
    texts={} if texts is None else texts
    if not isinstance(texts,dict) or set(texts)-set(asset_ids):raise NativeCatalogError("texts must map selected asset IDs to slot values")
    root,data=_catalog(catalog);assets=[describe_native_asset(catalog,a) for a in asset_ids]
    if any(not a["executable"] for a in assets):raise NativeCatalogError("selected source object cannot be extracted independently; use its parent group/page")
    sources={s["id"]:s for s in data["sources"]};packs={}
    try:
        for asset in assets:
            sid=asset["source_id"]
            if sid not in packs:packs[sid]=_Pack(root,sources[sid])
        if len(assets)==1:
            entries=_single(packs[assets[0]["source_id"]],assets[0],texts.get(asset_ids[0],{}));layout=None
        else:entries,layout=_compose(packs,assets,columns,texts)
        trees={k:v for k,v in entries.items() if isinstance(v,dict)}
        for tree in trees.values():_coalesce_text(tree)
        n._validate_trees(trees,set(entries))
        output.parent.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".htr-native-instance-",dir=output.parent) as temp:
            candidate=Path(temp)/"instance.pptx"
            with ZipFile(candidate,"w",ZIP_DEFLATED) as z:
                for name,value in entries.items():
                    try:payload=n._xml_bytes(value) if isinstance(value,dict) else value
                    except NativeCatalogError as exc:raise NativeCatalogError(f"{name}: {exc}") from exc
                    z.writestr(name,payload)
            n._new_output(output);os.rename(candidate,output)
        changed_runs=sum(1 for asset in assets for slot in asset["capabilities"]["text_slots"]
                         if slot["id"] in texts.get(asset["id"],{}) and texts[asset["id"]][slot["id"]]!=slot["text"])
        return {"status":"pass","pptx":str(output),"sha256":_file_hash(output),"asset_ids":asset_ids,"part_count":len(entries),"layout":layout,"render_verification":"not_run","editable_output":"native shapes/text/groups and dependency closure","automatic_text_reflow":False,
                "text_replacement_validation":{"mode":"source-character-count-only" if changed_runs else "not_applicable","changed_run_count":changed_runs,"glyph_fit":"not_measured" if changed_runs else "not_applicable","office_review_required":bool(changed_runs)}}
    except (BadZipFile,KeyError,OSError,TypeError) as exc:raise NativeCatalogError(str(exc)) from exc
    finally:
        for pack in packs.values():pack.close()


def _compose(packs,assets,columns,texts):
    if any(a["kind"]=="page" for a in assets):raise NativeCatalogError("compose native groups/atoms; whole pages use single-page instantiation")
    if columns is None:columns=math.ceil(math.sqrt(len(assets)))
    if type(columns)is not int or not 1<=columns<=len(assets):raise NativeCatalogError("columns must be an integer within the item count")
    first=assets[0];pack=packs[first["source_id"]]
    entries=_single(pack,first,texts.get(first["id"],{}))
    prespart=pack.manifest["presentation_part"]
    slidepart=pack.manifest["slides"][first["slide_number"]-1]["part"]
    slide=entries[slidepart];sp_tree=_find(slide,n.P,"spTree")
    sp_tree["children"]=[c for c in sp_tree["children"] if n._local(c) in {"nvGrpSpPr","grpSpPr"}]
    _root(slide)["children"]=[c for c in _root(slide)["children"] if n._local(c) in {"cSld","clrMapOvr"}]
    # Composition is a new white canvas; source backgrounds and master shapes
    # are not implicitly duplicated behind each independently selected atom.
    _root(slide)["attrs"]["showMasterSp"]="0"
    csld=_find(slide,n.P,"cSld")
    csld["children"]=[c for c in csld["children"] if n._local(c)!="bg"]
    csld["children"].insert(0,_element("p:bg",n.P,children=[_element("p:bgPr",n.P,children=[_element("a:solidFill",n.A,children=[_element("a:srgbClr",n.A,{"val":"FFFFFF"})]),_element("a:effectLst",n.A)])]))
    size=_find(entries[prespart],n.P,"sldSz");width,height=[int(size["attrs"][k]) for k in ("cx","cy")]
    margin=round(min(width,height)*0.045);gap=round(min(width,height)*0.025)
    rows=math.ceil(len(assets)/columns);cw=(width-2*margin-(columns-1)*gap)/columns;ch=(height-2*margin-(rows-1)*gap)/rows
    relname=_rels_name(slidepart)
    if relname not in entries:entries[relname]=_rels_config(relname,[])
    outputrels=_root(entries[relname]);outputrels["children"]=[r for r in outputrels["children"] if r.get("attrs",{}).get("Type")==n.R+"/slideLayout"]
    type_root=_root(entries["[Content_Types].xml"])
    next_id=1000;report=[]
    for index,asset in enumerate(assets):
        sourcepack=packs[asset["source_id"]]
        sourcepart,source_tree,sourcerels=_selected(sourcepack,asset,texts.get(asset["id"],{}))
        source_fonts=_source_text_sizes(sourcepack,sourcepart,source_tree)
        x,y,w,h=asset["bbox_emu"]
        if w<=0 or h<=0:raise NativeCatalogError("zero-area native asset cannot be grid-fitted")
        scale=min(cw/w,ch/h);ow,oh=w*scale,h*scale
        if source_fonts and min(source_fonts)*scale < 9-1e-6:
            raise NativeCatalogError(f"native grid capacity: {asset['id']} would shrink text below 9pt; choose fewer/smaller atoms or a larger layout")
        if source_fonts and asset["source_id"]!=first["source_id"] and _find(sourcepack.tree(sourcepack.manifest["presentation_part"]),n.P,"embeddedFontLst"):
            raise NativeCatalogError("cross-source embedded fonts need a font merge adapter; use source-preserving extraction")
        _materialize_theme(sourcepack,sourcepart,source_tree)
        _scale_composed_text(source_tree,scale)
        _order_drawing_properties(source_tree)
        source_shapes=[copy.deepcopy(c) for c in _find(source_tree,n.P,"spTree")["children"] if n._local(c) not in {"nvGrpSpPr","grpSpPr"}]
        selected_doc=_config("selected",_element("p:sld",n.P,children=source_shapes))
        identity_map={}
        for _,node in n._walk(selected_doc):
            if n._is(node,n.P,"cNvPr"):
                old=node["attrs"]["id"]
                if old not in identity_map:identity_map[old]=str(next_id);next_id+=1
                node["attrs"]["id"]=identity_map[old]
        for _,node in n._walk(selected_doc):
            if n._is(node,n.A,"stCxn") or n._is(node,n.A,"endCxn"):
                old=node["attrs"]["id"]
                if old not in identity_map:raise NativeCatalogError("connection escapes the selected native group")
                node["attrs"]["id"]=identity_map[old]
        prefix=f"ppt/catalog{index}/"
        dependencies={}; new_rels=[];rid_map={}
        if sourcerels:
            for rel in _elements(_root(sourcerels),n.REL,"Relationship"):
                a=rel["attrs"]
                if a["Type"]==n.R+"/slideLayout":continue
                new_id=f"cat{index}_{a['Id']}";rid_map[a["Id"]]=new_id
                if a.get("TargetMode")=="External":new_rels.append(_relation(new_id,a["Type"],a["Target"],True));continue
                target=_target(sourcepart,a["Target"])
                found=_closure(sourcepack,[target],{})
                dependencies.update(found)
                new_rels.append(_relation(new_id,a["Type"],"/"+prefix+target))
        # Parts keep per-asset namespaces, preventing media/chart relationship collisions.
        content_types=n._content_types({"[Content_Types].xml":sourcepack.tree("[Content_Types].xml")},set(sourcepack.parts))
        for name,value in dependencies.items():
            renamed=prefix+name
            if isinstance(value,dict):
                value=copy.deepcopy(value);value["part"]=renamed
                if name.endswith(".rels"):
                    owner=name.replace("/_rels/","/")[:-5]
                    for r in _elements(_root(value),n.REL,"Relationship"):
                        if r["attrs"].get("TargetMode")!="External":r["attrs"]["Target"]="/"+prefix+_target(owner,r["attrs"]["Target"])
            entries[renamed]=value
            type_root["children"].append(_element("Override",n.CT,{"PartName":"/"+renamed,"ContentType":content_types[name]}))
        outputrels["children"].extend(new_rels)
        for _,node in n._walk(selected_doc):
            for key,val in list(node.get("attrs",{}).items()):
                if node.get("attr_ns",{}).get(key)==n.R and val:
                    if val not in rid_map:raise NativeCatalogError("selected object has unresolved relationship")
                    node["attrs"][key]=rid_map[val]
        left=margin+(index%columns)*(cw+gap)+(cw-ow)/2
        top=margin+(index//columns)*(ch+gap)+(ch-oh)/2
        t=_element("a:xfrm",n.A,children=[_element("a:off",n.A,{"x":str(round(left)),"y":str(round(top))}),_element("a:ext",n.A,{"cx":str(round(ow)),"cy":str(round(oh))}),_element("a:chOff",n.A,{"x":str(round(x)),"y":str(round(y))}),_element("a:chExt",n.A,{"cx":str(round(w)),"cy":str(round(h))})])
        attrs={k:v for k,v in _root(source_tree)["attrs"].items() if k=="xmlns" or k.startswith("xmlns:")}
        attrs.setdefault("xmlns:p",n.P);attrs.setdefault("xmlns:a",n.A)
        wrapper=_element("p:grpSp",n.P,attrs,[
            _element("p:nvGrpSpPr",n.P,children=[_element("p:cNvPr",n.P,{"id":str(next_id),"name":asset["id"]}),_element("p:cNvGrpSpPr",n.P),_element("p:nvPr",n.P)]),
            _element("p:grpSpPr",n.P,children=[t]),*source_shapes],{k:"http://www.w3.org/2000/xmlns/" for k in attrs})
        next_id+=1;sp_tree["children"].append(wrapper)
        report.append({"asset_id":asset["id"],"source_bbox_emu":asset["bbox_emu"],"frame_emu":[round(left),round(top),round(ow),round(oh)],"scale":scale,"minimum_text_pt":min(round(v*scale*100)/100 for v in source_fonts) if source_fonts else None})
    return entries,{"algorithm":"uniform-grid-aspect-contain","columns":columns,"rows":rows,"items":report,"theme_policy":"source references materialized; inherited placeholders/complex graphic frames rejected","typography_policy":"native font sizes explicitly scaled and written, minimum 9pt; not the new-report 14pt scale"}


def _order_drawing_properties(tree):
    """Keep OOXML sequence order after cascading properties, not just valid XML.

    Microsoft Open XML SDK schema particles for CT_TextCharacterProperties,
    CT_TextParagraphProperties, CT_ShapeProperties and CT_LineProperties.
    """
    fills="noFill solidFill gradFill blipFill pattFill grpFill"
    char=("ln "+fills+" effectLst effectDag highlight uLnTx uLn uFillTx uFill latin ea cs sym hlinkClick hlinkMouseOver rtl extLst").split()
    para="lnSpc spcBef spcAft buClrTx buClr buSzTx buSzPct buSzPts buFontTx buFont buNone buAutoNum buChar buBlip tabLst defRPr extLst".split()
    shape=("xfrm custGeom prstGeom "+fills+" ln effectLst effectDag scene3d sp3d extLst").split()
    line="noFill solidFill gradFill pattFill prstDash custDash round bevel miter headEnd tailEnd extLst".split()
    body="prstTxWarp noAutofit normAutofit spAutoFit scene3d sp3d flatTx extLst".split()
    for _,node in n._walk(tree):
        local=n._local(node)
        order=char if node.get("ns")==n.A and local in {"rPr","defRPr","endParaRPr"} else para if node.get("ns")==n.A and (local=="pPr" or re.fullmatch(r"lvl[1-9]pPr",local)) else shape if node.get("ns") in {n.A,n.P} and local=="spPr" else line if node.get("ns")==n.A and local in {"ln","uLn"} else body if node.get("ns")==n.A and local=="bodyPr" else None
        if order:
            rank={name:i for i,name in enumerate(order)}
            ordered=iter(sorted(_elements(node),key=lambda c:rank.get(n._local(c),len(rank))))
            node["children"]=[next(ordered) if c.get("kind")=="element" else c for c in node["children"]]


def _scale_composed_text(tree,scale):
    """Group coordinates do not change native Font.Size: write real point sizes."""
    for _,node in n._walk(tree):
        if node.get("ns")!=n.A:continue
        local=n._local(node);attrs=node["attrs"]
        keys=()
        if local in {"rPr","defRPr","endParaRPr"}:keys=("sz","kern","spc")
        elif local in {"spcPts","buSzPts"}:keys=("val",)
        elif local=="bodyPr":
            keys=("lIns","tIns","rIns","bIns","spcCol")
            # Do not let PowerPoint resize an engine-computed text box on open.
            node["children"]=[c for c in node["children"] if n._local(c) not in {"spAutoFit","noAutofit"}]
            node["children"].insert(0,_element("a:noAutofit",n.A))
        elif local=="pPr" or re.fullmatch(r"lvl[1-9]pPr",local):keys=("marL","marR","indent","defTabSz")
        elif local=="tab":keys=("pos",)
        for key in keys:
            if key in attrs:attrs[key]=str(round(int(attrs[key])*scale))


def _merged_properties(*levels):
    """Cascade structured paragraph/run properties without borrowing target defaults."""
    result=None
    fills={"solidFill","gradFill","noFill","pattFill","blipFill"}
    for level in levels:
        if level is None:continue
        if result is None:result=copy.deepcopy(level);continue
        result["attrs"].update(level["attrs"])
        result["attr_ns"].update(level.get("attr_ns",{}))
        for child in _elements(level):
            local=n._local(child)
            result["children"]=[c for c in result["children"] if n._local(c)!=local and not(local in fills and n._local(c) in fills)]
            result["children"].append(copy.deepcopy(child))
    return result


def _source_text_sizes(pack,part,tree):
    """Resolve actual point sizes; native group geometry does not scale fonts."""
    default=_find(pack.tree(pack.manifest["presentation_part"]),n.P,"defaultTextStyle")
    master=None;current=part
    for kind in ("slideLayout","slideMaster"):
        rels=pack.rels(current)
        rel=next((r for r in _elements(_root(rels),n.REL,"Relationship") if r["attrs"]["Type"]==n.R+"/"+kind),None) if rels else None
        if rel is None:break
        current=_target(current,rel["attrs"]["Target"])
        if kind=="slideMaster":master=_find(pack.tree(current),n.P,"otherStyle")
    def level_from(parent,level):
        if parent is None:return None
        return next(iter(_elements(parent,n.A,f"lvl{level+1}pPr")),None)
    sizes=[];objects=n._slide_objects(tree)
    for obj in objects:
        shape=n._node(tree,obj["binding"]);tx=next(iter(_elements(shape,n.P,"txBody")),None)
        if tx is None:continue
        if any(n._is(v,n.A,"normAutofit") for _,v in n._walk(_config("text",tx))):
            raise NativeCatalogError("autofit text needs an explicit font-size adapter before grid composition")
        lists=next(iter(_elements(tx,n.A,"lstStyle")),None)
        for para in _elements(tx,n.A,"p"):
            ppr=next(iter(_elements(para,n.A,"pPr")),None);level=int(ppr["attrs"].get("lvl","0")) if ppr else 0
            inherited=[level_from(parent,level) for parent in (default,master,lists)]
            merged=_merged_properties(*inherited,ppr)
            if merged:
                merged.update(tag="a:pPr",ns=n.A)
                if ppr:para["children"].remove(ppr)
                para["children"].insert(0,merged)
            drs=[next(iter(_elements(p,n.A,"defRPr")),None) if p else None for p in [*inherited,ppr]]
            dr=_merged_properties(*drs)
            default_sz=dr["attrs"].get("sz") if dr else None
            for run in _elements(para):
                if n._local(run) not in {"r","fld"} or not _elements(run,n.A,"t"):continue
                rpr=next(iter(_elements(run,n.A,"rPr")),None)
                material=_merged_properties(dr,rpr)
                if material:
                    material.update(tag="a:rPr",ns=n.A)
                    if rpr:run["children"].remove(rpr)
                    run["children"].insert(0,material);rpr=material
                value=(rpr["attrs"].get("sz") if rpr else None) or default_sz
                if value is None:raise NativeCatalogError("cannot establish native text size; use single source-preserving extraction")
                point=float(value)/100
                if not math.isfinite(point) or point<=0:raise NativeCatalogError("invalid native text size")
                sizes.append(point)
                # Make resolved size explicit for source-style materialization.
                if rpr is None:rpr=_element("a:rPr",n.A);run["children"].insert(0,rpr)
                rpr["attrs"].setdefault("sz",str(value))
    return sizes


def _materialize_theme(pack,part,tree):
    """Resolve supported source style references before entering another theme."""
    if any(n._is(v,n.P,"ph") or n._is(v,n.P,"graphicFrame") for _,v in n._walk(tree)):
        raise NativeCatalogError("placeholder/graphic-frame composition needs a dedicated semantic adapter; single extraction is supported")
    current=part;chain=[]
    for kind in ("slideLayout","slideMaster","theme"):
        rels=pack.rels(current)
        choices=[] if rels is None else [r for r in _elements(_root(rels),n.REL,"Relationship") if r["attrs"]["Type"]==n.R+"/"+kind]
        if not choices:break
        current=_target(current,choices[0]["attrs"]["Target"]);chain.append(current)
    theme=pack.tree(chain[-1]) if chain and _find(pack.tree(chain[-1]),n.A,"clrScheme") else None
    colors={};fonts={};fmt={};required_fonts=set();color_map={"bg1":"lt1","tx1":"dk1","bg2":"lt2","tx2":"dk2"}
    for parent in reversed(chain[:-1]):
        mapping=_find(pack.tree(parent),n.P,"clrMap") or _find(pack.tree(parent),n.A,"overrideClrMapping")
        if mapping:color_map.update(mapping["attrs"])
    mapping=_find(tree,n.A,"overrideClrMapping")
    if mapping:color_map.update(mapping["attrs"])
    if theme:
        scheme=_find(theme,n.A,"clrScheme")
        for item in _elements(scheme):
            color=_elements(item)[0];colors[n._local(item)]=color["attrs"].get("val") if n._local(color)=="srgbClr" else color["attrs"].get("lastClr")
        scheme=_find(theme,n.A,"fontScheme")
        if scheme:
            for item in _elements(scheme):
                key="mj" if n._local(item)=="majorFont" else "mn"
                supplemental={c["attrs"].get("script"):c["attrs"].get("typeface") for c in _elements(item,n.A,"font")}
                for local,code in (("latin","lt"),("ea","ea"),("cs","cs")):
                    children=_elements(item,n.A,local)
                    face=children[0]["attrs"].get("typeface") if children else None
                    fonts[f"+{key}-{code}"]=face or supplemental.get("Hans") if code=="ea" else face
        scheme=_find(theme,n.A,"fmtScheme")
        if scheme:fmt={n._local(c):_elements(c) for c in _elements(scheme)}
    def resolve_colors(node,ph=None):
        for child in node.get("children",[]):resolve_colors(child,ph)
        if n._is(node,n.A,"schemeClr"):
            key=node["attrs"]["val"]
            value=ph if key=="phClr" else colors.get(color_map.get(key,key))
            if not value:raise NativeCatalogError("unresolved source theme color: "+key)
            node.update(tag="a:srgbClr",ns=n.A,attrs={"val":value},attr_ns={})
        if node.get("ns")==n.A and n._local(node) in {"latin","ea","cs"}:
            face=node["attrs"].get("typeface","")
            if face.startswith("+"):
                if not fonts.get(face):
                    # Empty theme ea/cs entries are valid. An unused empty
                    # paragraph/run style must not block icon-only composition.
                    # Active glyph scripts, however, still require resolution.
                    if face not in fonts or id(node) in required_fonts:raise NativeCatalogError("unresolved source theme font: "+face)
                    node["attrs"]["typeface"]=""
                else:node["attrs"]["typeface"]=fonts[face]
    def color_ref(ref):
        if ref is None:return None
        cloned=copy.deepcopy(ref);resolve_colors(cloned)
        c=next((c for c in _elements(cloned) if n._local(c) in {"srgbClr","sysClr"}),None)
        return c
    for obj in n._slide_objects(tree):
        shape=n._node(tree,obj["binding"])
        style=next(iter(_elements(shape,n.P,"style")),None)
        props=next(iter(_elements(shape,n.P,"spPr")),None)
        if style and props:
            for refname,listname,propnames in (("fillRef","fillStyleLst",{"solidFill","gradFill","noFill","blipFill","pattFill","grpFill"}),("lnRef","lnStyleLst",{"ln"}),("effectRef","effectStyleLst",{"effectLst","effectDag"})):
                ref=next(iter(_elements(style,n.A,refname)),None)
                if ref is None:continue
                existing=next((c for c in _elements(props) if n._local(c) in propnames),None)
                if existing is not None and refname!="lnRef":continue
                index=int(ref["attrs"].get("idx","0"))
                if index==0:
                    if refname=="fillRef":props["children"].append(_element("a:noFill",n.A))
                    elif refname=="lnRef":props["children"].append(_element("a:ln",n.A,children=[_element("a:noFill",n.A)]))
                    continue
                items=fmt.get("bgFillStyleLst" if refname=="fillRef" and index>=1001 else listname,[])
                index=index-1001 if index>=1001 else index-1
                if not 0<=index<len(items):raise NativeCatalogError("unresolved theme style matrix")
                value=copy.deepcopy(items[index]);color=color_ref(ref)
                resolve_colors(value,color["attrs"].get("val") if color else None)
                if refname=="effectRef":props["children"].extend(value["children"])
                elif existing is not None:
                    for k,v in value["attrs"].items():existing["attrs"].setdefault(k,v)
                    fillnames={"solidFill","gradFill","noFill","pattFill"}
                    existing_names={n._local(c) for c in _elements(existing)}
                    for child in value["children"]:
                        local=n._local(child)
                        if local in existing_names or (local in fillnames and existing_names&fillnames):continue
                        existing["children"].append(child)
                else:props["children"].append(value)
        # Regular text boxes often omit p:style. They still inherit text defaults
        # and theme fonts; make these explicit before changing their source theme.
        fontref=next(iter(_elements(style,n.A,"fontRef")),None) if style else None
        tx=next(iter(_elements(shape,n.P,"txBody")),None)
        if tx:
            family="mj" if fontref and fontref["attrs"].get("idx")=="major" else "mn"
            for _,node in n._walk(_config("text",tx)):
                if not(n._is(node,n.A,"r") or n._is(node,n.A,"fld")):continue
                text_node=next(iter(_elements(node,n.A,"t")),None)
                content="".join(c.get("value","") for c in text_node["children"]) if text_node else ""
                rpr=next(iter(_elements(node,n.A,"rPr")),None)
                if rpr is None:rpr=_element("a:rPr",n.A);node["children"].insert(0,rpr)
                if "sz" not in rpr["attrs"]:raise NativeCatalogError("inherited text size needs a semantic adapter before composition")
                for local,code in (("latin","lt"),("ea","ea"),("cs","cs")):
                    face=fonts.get(f"+{family}-{code}")
                    if face and not _elements(rpr,n.A,local):rpr["children"].append(_element("a:"+local,n.A,{"typeface":face}))
                for local,required in (("latin",any(ord(c)<256 and c.isalnum() for c in content)),("ea",any("\u2e80"<=c<="\uffef" for c in content)),("cs",any("\u0590"<=c<="\u0fff" for c in content))):
                    candidates=_elements(rpr,n.A,local)
                    if required and not candidates:raise NativeCatalogError("cannot resolve source text font for "+local+"; use source-preserving extraction")
                    if required:required_fonts.update(id(c) for c in candidates)
                if not any(n._local(c) in {"solidFill","gradFill","noFill"} for c in _elements(rpr)):
                    color=color_ref(fontref) if fontref else None
                    if color is None:
                        value=colors.get(color_map.get("tx1","dk1"))
                        if not value:raise NativeCatalogError("cannot resolve source text color; use source-preserving extraction")
                        color=_element("a:srgbClr",n.A,{"val":value})
                    rpr["children"].append(_element("a:solidFill",n.A,children=[color]))
        if style:shape["children"].remove(style)
    for node in tree["nodes"]:resolve_colors(node)
