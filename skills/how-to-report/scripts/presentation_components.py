"""Bounded offline media, tables and explicit relations. No user HTML or code."""
from __future__ import annotations

import base64
import hashlib
from html import escape
import json
from pathlib import Path
import re
import stat


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fields(obj, required, optional=()):
    require(isinstance(obj, dict) and set(required) <= obj.keys() and obj.keys() <= set(required) | set(optional), "component fields invalid")


def label(value):
    require(isinstance(value, str) and 0 < len(value.strip()) <= 4000 and not any(ord(c) < 32 and c not in '\n\r\t' for c in value), "component text invalid")


def reference(values):
    require(isinstance(values, list), "component refs must be a list")
    identities = set()
    for r in values:
        fields(r, ('id', 'revision'), ('locator',))
        label(r['id'])
        require(type(r['revision']) is int and r['revision'] > 0, "invalid reference revision")
        if 'locator' in r:
            label(r['locator'])
        key = (r['id'], r['revision'], r.get('locator'))
        require(key not in identities, "duplicate component reference")
        identities.add(key)


def identity(value, seen):
    require(isinstance(value, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', value) and value not in seen, "invalid/duplicate component ID")
    seen.add(value)


def file_spec(value):
    fields(value, ('path', 'sha256'))
    label(value['path'])
    path = Path(value['path'])
    require(not path.is_absolute() and not path.drive and '\\' not in value['path'] and ':' not in value['path'] and all(x not in ('..', '.') for x in path.parts), "media must use a relative child path")
    require(isinstance(value['sha256'], str) and re.fullmatch('[a-f0-9]{64}', value['sha256']), "media sha256 required")


def validate_component(element, seen):
    kind = element['type']
    data = element[kind]
    if kind == 'media':
        fields(data, ('kind', 'file', 'alt'), ('poster', 'annotations'))
        require(data['kind'] in ('image', 'video'), "unsupported media kind")
        file_spec(data['file']); label(data['alt'])
        if data['kind'] == 'video':
            require('poster' in data, "video requires a local poster for reading/printing")
        if 'poster' in data:
            file_spec(data['poster'])
        items = data.get('annotations', [])
        require(isinstance(items, list) and len(items) <= 8 and (not items or data['kind'] == 'image'), "annotations require image; maximum 8")
        for item in items:
            fields(item, ('id', 'label', 'x', 'y', 'width', 'height', 'refs'))
            identity(item['id'], seen); label(item['label']); reference(item['refs'])
            require(all(type(item[k]) in (int, float) and 0 <= item[k] <= 100 for k in ('x','y','width','height')), "annotation coordinates must be percentages")
            require(item['width'] > 0 and item['height'] > 0 and item['x']+item['width'] <= 100 and item['y']+item['height'] <= 100, "annotation outside image")
    elif kind == 'table':
        fields(data, ('columns', 'rows'))
        require(isinstance(data['columns'], list) and 1 <= len(data['columns']) <= 6, "table needs 1–6 columns")
        for column in data['columns']:
            label(column)
        require(len(set(data['columns'])) == len(data['columns']), "duplicate table columns")
        require(isinstance(data['rows'], list) and 1 <= len(data['rows']) <= 10, "table needs 1–10 rows; paginate larger tables")
        for row in data['rows']:
            fields(row, ('id', 'cells', 'refs')); identity(row['id'], seen); reference(row['refs'])
            require(isinstance(row['cells'], list) and len(row['cells']) == len(data['columns']), "table cells must match columns")
            for cell in row['cells']:
                if cell is not None:
                    label(cell)
    else:
        fields(data, ('kind', 'nodes', 'edges'), ('lanes',))
        require(data['kind'] in ('relation', 'swimlane'), "diagram kind invalid")
        require(isinstance(data['nodes'], list) and 1 <= len(data['nodes']) <= 8, "diagram needs 1–8 nodes")
        require(isinstance(data['edges'], list) and len(data['edges']) <= 8, "diagram supports at most 8 explicit edges")
        lanes = data.get('lanes', [])
        require(isinstance(lanes, list) and len(lanes) <= 4, "at most 4 lanes")
        if data['kind'] == 'swimlane':
            require(len(lanes) > 0, "swimlane needs lanes")
        else:
            require(not lanes, "lanes only belong to swimlane")
        for lane in lanes:
            fields(lane, ('id', 'label')); identity(lane['id'], seen); label(lane['label'])
            require(len(lane['label']) <= 16, "lane label too long; use a traceable short name")
        lane_ids = {x['id'] for x in lanes}
        for node in data['nodes']:
            fields(node, ('id', 'label', 'refs'), ('lane',))
            identity(node['id'], seen); label(node['label']); reference(node['refs'])
            require(len(node['label']) <= (24 if lanes else 36), "node label too long; use a traceable short name")
            require((isinstance(node.get('lane'), str) and node['lane'] in lane_ids) if lanes else ('lane' not in node), "node lane missing/invalid")
        for lane in lanes:
            require(sum(n.get('lane') == lane['id'] for n in data['nodes']) <= 4, 'at most 4 nodes per lane; split the diagram')
        node_ids = {x['id'] for x in data['nodes']}
        for edge in data['edges']:
            fields(edge, ('id', 'from', 'to', 'relation', 'label', 'refs'))
            identity(edge['id'], seen); label(edge['label']); reference(edge['refs'])
            require(isinstance(edge['from'], str) and isinstance(edge['to'], str) and edge['from'] in node_ids and edge['to'] in node_ids and edge['from'] != edge['to'], "edge endpoint invalid")
            require(edge['relation'] in ('sequence','dependency','data-flow','causal','association','feedback'), "edge relation must be explicit")


def prepare_media(plan, base):
    """Read and hash declared local resources before any output is created."""
    payload, resources = {}, {}
    total = 0
    base = base.resolve()
    for page in plan['pages']:
        for element in page['elements']:
            if element.get('type') != 'media':
                continue
            media = element['media']
            for key in ('file', 'poster'):
                if key not in media:
                    continue
                spec = media[key]
                candidate = base / spec['path']
                for part in (candidate, *candidate.parents):
                    if part.exists() or part.is_symlink():
                        info = part.lstat()
                        require(not stat.S_ISLNK(info.st_mode) and not getattr(info, 'st_file_attributes', 0) & 0x400, "media link/reparse unsupported")
                path = candidate.resolve()
                require(path.is_relative_to(base) and path.is_file(), "media missing or outside plan directory")
                require(path.stat().st_size <= 40 * 1024 * 1024, "media exceeds 40 MiB")
                raw = path.read_bytes()
                total += len(raw)
                require(total <= 80 * 1024 * 1024, "total media exceeds 80 MiB")
                sha = hashlib.sha256(raw).hexdigest()
                require(sha == spec['sha256'], "media hash mismatch")
                extension = path.suffix.lower()
                mimes = {'.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.mp4':'video/mp4','.webm':'video/webm'}
                require(extension in mimes, "only PNG/JPEG/WebP/MP4/WebM supported")
                mime = mimes[extension]
                require((key == 'poster' or media['kind'] == 'image') == mime.startswith('image/'), "media kind mismatch")
                valid = (extension == '.png' and raw.startswith(b'\x89PNG\r\n\x1a\n') or extension in ('.jpg','.jpeg') and raw.startswith(b'\xff\xd8\xff') or extension == '.webp' and raw[:4] == b'RIFF' and raw[8:12] == b'WEBP' or extension == '.mp4' and raw[4:8] == b'ftyp' or extension == '.webm' and raw[:4] == b'\x1aE\xdf\xa3')
                require(valid, "media header does not match type")
                name = 'media/' + sha + extension
                payload[name] = raw
                resources[(element['id'], key)] = {'url':'data:' + mime + ';base64,' + base64.b64encode(raw).decode('ascii'), 'sha256':sha, 'snapshot':name, 'source_path':spec['path'], 'mime':mime}
    return payload, resources


def render_component(element, language, resources):
    kind = element['type']; data = element[kind]; eid = element['id']; mapping = []
    t = lambda value: escape(str(value), quote=True)
    missing = '未提供' if language == 'zh-CN' else 'Unavailable'
    def attrs(item):
        selector = '#datum-' + item['id']
        mapping.append({'element_id':eid,'datum_id':item['id'],'selector':selector,'refs':item['refs'],'displayed':item})
        return f'id="datum-{item["id"]}" data-datum-id="{item["id"]}" data-refs="{t(json.dumps(item["refs"],ensure_ascii=False))}"'
    def provenance(values):
        return '; '.join(t(r['id'])+'@'+str(r['revision'])+(' · '+t(r['locator']) if 'locator' in r else '') for r in values) or missing
    if kind == 'table':
        heads = ''.join('<th scope="col">'+t(x)+'</th>' for x in data['columns'])
        rows = ''.join('<tr '+attrs(row)+'>'+''.join('<td>'+t(cell if cell is not None else missing)+'</td>' for cell in row['cells'])+'<td class="cell-sources">'+provenance(row['refs'])+'</td></tr>' for row in data['rows'])
        return '<div class="structured-table"><table><thead><tr>'+heads+'<th>来源 / Source</th></tr></thead><tbody>'+rows+'</tbody></table></div>', mapping
    if kind == 'media':
        resource = resources.get((eid, 'file'))
        require(resource is not None, "media must be preflighted from a plan file")
        if data['kind'] == 'image':
            graphic = '<img src="'+resource['url']+'" alt="'+t(data['alt'])+'">'
            overlays, notes = [], []
            for index, annotation in enumerate(data.get('annotations', [])):
                overlays.append(f'<span class="image-annotation" style="left:{annotation["x"]}%;top:{annotation["y"]}%;width:{annotation["width"]}%;height:{annotation["height"]}%" aria-hidden="true">{index+1}</span>')
                notes.append('<li '+attrs(annotation)+'>'+str(index+1)+'. '+t(annotation['label'])+' <small>'+provenance(annotation['refs'])+'</small></li>')
            graphic = '<div class="image-frame">'+graphic+''.join(overlays)+'</div><ul class="annotation-notes">'+''.join(notes)+'</ul>'
        else:
            poster = resources[(eid,'poster')]['url']
            graphic = '<video controls preload="metadata" poster="'+poster+'" aria-label="'+t(data['alt'])+'"><source src="'+resource['url']+'" type="'+resource['mime']+'"></video><img class="video-print-poster" src="'+poster+'" alt="'+t(data['alt'])+'">'
        mapping.append({'element_id':eid,'selector':'#element-'+eid+' .media-content','refs':element['refs'],'displayed':{'alt':data['alt'],'resources':[{k:v for k,v in r.items() if k!='url'} for (rid,_),r in resources.items() if rid==eid], 'annotations':data.get('annotations',[])}})
        return '<figure class="media-content">'+graphic+'<figcaption>'+t(data['alt'])+'</figcaption></figure>', mapping
    nodes = data['nodes']; lanes = data.get('lanes', [])
    positions = {}
    if lanes:
        for li,lane in enumerate(lanes):
            members = [n for n in nodes if n['lane'] == lane['id']]
            for ni,node in enumerate(members):
                positions[node['id']] = (190+(ni+.5)*740/max(1,len(members)), 35+li*100)
    else:
        for ni,node in enumerate(nodes):
            positions[node['id']] = (130+(ni%4)*245, 45+(ni//4)*140)
    # Nodes extend 56 units below their anchor (76px box starting at y-20).
    # Include the actual final box/lane and breathing room for strokes/markers.
    height = max(max(y+56 for _,y in positions.values()), len(lanes)*100) + 24
    marker_id = 'direction-' + eid
    vectors=[f'<defs><marker id="{marker_id}" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8,4 L0,8 Z" fill="#64869c"/></marker></defs>']
    for li,lane in enumerate(lanes):
        chunks=[lane['label'][i:i+8] for i in range(0,len(lane['label']),8)]
        texts=''.join(f'<tspan x="12" dy="{20 if i else 0}">{t(s)}</tspan>' for i,s in enumerate(chunks))
        vectors.append(f'<rect x="0" y="{li*100}" width="1000" height="96" fill="#eff6fa"/><text x="12" y="{li*100+38}" font-size="16">{texts}</text>')
    for i,edge in enumerate(data['edges']):
        x1,y1=positions[edge['from']]; x2,y2=positions[edge['to']]
        dx,dy=x2-x1,y2-y1
        half_width=80 if lanes else 105
        edge_fraction=min(half_width/abs(dx) if dx else float('inf'), 38/abs(dy) if dy else float('inf'))
        arrow='' if edge['relation']=='association' else f' marker-end="url(#{marker_id})"'
        vectors.append(f'<line x1="{x1+dx*edge_fraction}" y1="{y1+18+dy*edge_fraction}" x2="{x2-dx*edge_fraction}" y2="{y2+18-dy*edge_fraction}" stroke="#64869c" stroke-width="2"{arrow}/><text x="{(x1+x2)/2}" y="{(y1+y2)/2+12}" font-size="14">{i+1}</text>')
    for node in nodes:
        x,y=positions[node['id']]
        wrap = 8 if lanes else 12
        width = 160 if lanes else 210
        chunks=[node['label'][i:i+wrap] for i in range(0,len(node['label']),wrap)]
        texts=''.join(f'<tspan x="{x}" dy="{18 if i else 0}">{t(s)}</tspan>' for i,s in enumerate(chunks))
        vectors.append(f'<g {attrs(node)}><rect x="{x-width/2}" y="{y-20}" width="{width}" height="76" rx="8" fill="#e1f1fb" stroke="#86bbd9"/><text text-anchor="middle" x="{x}" y="{y}" font-size="16">{texts}</text></g>')
    names={n['id']:n['label'] for n in nodes}
    edges=''.join('<li '+attrs(edge)+'>'+str(i+1)+'. '+t(names[edge['from']])+(' — ' if edge['relation']=='association' else ' → ')+t(names[edge['to']])+' · '+t(edge['relation'])+'：'+t(edge['label'])+' <small>'+provenance(edge['refs'])+'</small></li>' for i,edge in enumerate(data['edges']))
    node_text='; '.join(t(node['label'])+' ['+provenance(node['refs'])+']' for node in nodes)
    return f'<div class="diagram-content"><svg viewBox="0 0 1000 {height}" role="img" aria-label="{t(element["title"])}">{"".join(vectors)}</svg><p class="diagram-nodes">{node_text}</p><ol class="relation-key">{edges}</ol></div>',mapping
