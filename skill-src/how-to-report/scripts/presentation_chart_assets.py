"""Registered, data-driven chart assets. Geometry is calculated inside the engine.

The FT vocabulary is a discovery taxonomy, not a renderer. Every executable
entry below selects an actual algorithm and validated data contract. Examples
are explicitly synthetic. Geographic or statistical algorithms not implemented
remain discoverable but cannot be instantiated.
"""
from __future__ import annotations

import copy
import json
import math
import statistics

from report_ppt import SKILL_ROOT, TemplateInputError

VOCABULARY = SKILL_ROOT / "assets/design-system/visual-vocabulary.json"
VERSION = "0.1"
CATEGORY = {"diverging-bar", "diverging-stacked-bar", "spine", "surplus-deficit-filled-line",
    "ordered-bar", "ordered-column", "slope", "lollipop", "bump", "line", "column", "area",
    "seismogram", "streamgraph", "bar", "paired-column", "paired-bar", "marimekko", "column-line",
    "radar", "parallel-coordinates", "stacked-column-bar", "pie", "doughnut", "waterfall",
    "proportional-stacked-bar", "population-pyramid",
    "ordered-proportional-symbol", "proportional-symbol", "isotype", "grouped-symbol", "arc", "gridplot"}
XY = {"scatterplot", "connected-scatterplot", "bubble"}
SAMPLES = {"histogram", "boxplot", "violin-plot", "cumulative-curve", "frequency-polygons", "dot-strip-plot", "barcode-plot", "beeswarm"}
RANGES = {"dot-plot", "bullet", "fan-chart", "candlestick"}
MATRIX = {"xy-heatmap", "calendar-heatmap"}
TIMELINE = {"priestley-timeline", "circle-timeline", "vertical-timeline"}
HIERARCHY = {"treemap", "sunburst"}
GRAPH = {"network", "sankey", "chord"}
GEOGRAPHY = {"choropleth", "map-proportional-symbol", "flow-map", "equalised-cartogram", "scaled-cartogram", "dot-density"}
FIELD = {"contour-map", "map-heatmap"}
SETS = {"venn"}
VORONOI = {"voronoi"}
IMPLEMENTED = CATEGORY | XY | SAMPLES | RANGES | MATRIX | TIMELINE | HIERARCHY | GRAPH | GEOGRAPHY | FIELD | SETS | VORONOI
FAMILY_FIELDS = {
    "category": {"categories", "series"}, "xy": {"series"}, "samples": {"series"},
    "ranges": {"categories", "ranges"}, "matrix": {"x_labels", "y_labels", "values"},
    "timeline": {"rows"}, "hierarchy": {"paths", "values"}, "graph": {"nodes", "links"},
    "geography": {"regions", "coordinates"}, "field": {"x", "y", "values", "levels", "coordinates"},
    "sets": {"sets"}, "voronoi": {"sites", "bounds"},
}
COMMON_DATA = {"unit", "period", "scope"}
OPTIONS = {"title", "note", "bins", "symbol_unit", "bandwidth"}
USE = {
    "deviation": "比较相对零点或明确参考值的正负偏差。", "correlation": "观察变量共同变化，不能据此声称因果。",
    "ranking": "比较有序位置，保留同口径和并列关系。", "distribution": "观察真实样本的分布、范围及异常值。",
    "change-over-time": "显示有顺序的时间变化，保持期间与频率一致。", "magnitude": "在共同尺度下比较数量大小。",
    "part-to-whole": "展示同一整体内互斥且完整的组成。", "spatial": "使用真实地理边界、坐标和明确连接键。",
    "flow": "表达有定义的连接或守恒的数量流。",
}


def _id(identifier):
    if not isinstance(identifier, str):
        raise TemplateInputError("chart asset ID must be text")
    return identifier.removeprefix("chart.")


def _family(identifier):
    for name, values in (("category", CATEGORY), ("xy", XY), ("samples", SAMPLES), ("ranges", RANGES),
                         ("matrix", MATRIX), ("timeline", TIMELINE), ("hierarchy", HIERARCHY), ("graph", GRAPH),
                         ("geography", GEOGRAPHY), ("field", FIELD), ("sets", SETS), ("voronoi", VORONOI)):
        if identifier in values:
            return name
    return "unavailable"


def _num(value, where):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise TemplateInputError(f"{where}: finite numeric value required")
    return float(value)


def _list(value, where, lower=1, upper=200):
    if not isinstance(value, list) or not lower <= len(value) <= upper:
        raise TemplateInputError(f"{where}: list size must be {lower}..{upper}")
    return value


def _label(value, where):
    if not isinstance(value, str) or not value.strip() or len(value) > 60:
        raise TemplateInputError(f"{where}: nonempty text of at most 60 characters required")
    return value


def _object(value, allowed, where, required=()):
    if not isinstance(value, dict) or set(value) - allowed or set(required) - set(value):
        raise TemplateInputError(f"{where}: expected fields {sorted(allowed)}; required {sorted(required)}")


def _validate(identifier, data, options):
    family = _family(identifier)
    if family == "unavailable":
        raise TemplateInputError(f"chart.{identifier}: algorithm is not implemented; no placeholder output is generated")
    extras = {"points", "links", "metric_type"} if family == "geography" else ({"series_units"} if identifier == "column-line" else set())
    _object(data, FAMILY_FIELDS[family] | COMMON_DATA | extras, "chart data", FAMILY_FIELDS[family])
    _object(options, _option_fields(identifier), "chart options")
    for key in COMMON_DATA & data.keys():
        _label(data[key], key)
    for key in ("title", "note"):
        if key in options:
            _label(options[key], key)
    for key in ("bins", "symbol_unit", "bandwidth"):
        if key in options and _num(options[key], key) <= 0:
            raise TemplateInputError(f"{key} must be positive")
    if "bins" in options and (type(options["bins"]) is not int or options["bins"] > 30):
        raise TemplateInputError("bins must be an integer from 1 to 30")
    if "show_values" in options and type(options["show_values"]) is not bool:
        raise TemplateInputError("show_values must be boolean")
    if family in {"category", "ranges"}:
        cats = _list(data["categories"], "categories", upper=30)
        for c in cats:
            _label(c, "category")
        if len(set(cats)) != len(cats):
            raise TemplateInputError("category names must be unique")
    if family in {"category", "xy", "samples"}:
        series = _list(data["series"], "series", upper=6)
        for row in series:
            value_key = "points" if family == "xy" else "values"
            _object(row, {"name", value_key}, "series row", {"name", value_key})
            _label(row["name"], "series name")
            values = _list(row[value_key], value_key, upper=200)
            if family == "category" and len(values) != len(cats):
                raise TemplateInputError("series length must equal category count")
            for value in values:
                if family == "xy":
                    point = _list(value, "point", 3 if identifier == "bubble" else 2, 3 if identifier == "bubble" else 2)
                    for n in point:
                        _num(n, "point")
                    if identifier == "bubble" and point[2] <= 0:
                        raise TemplateInputError("bubble size must be positive")
                else:
                    _num(value, "value")
        flat = [v for s in series for v in s.get("values", [])]
        if len({s["name"] for s in series}) != len(series):
            raise TemplateInputError("series names must be unique")
        nonnegative = {"pie", "doughnut", "spine", "population-pyramid", "stacked-column-bar", "proportional-stacked-bar",
                       "marimekko", "proportional-symbol", "ordered-proportional-symbol", "isotype", "grouped-symbol", "arc", "gridplot", "streamgraph", "area", "radar"}
        if identifier in nonnegative and (min(flat) < 0 or sum(flat) <= 0):
            raise TemplateInputError(f"{identifier} needs nonnegative values and a positive total")
        single = {"pie", "doughnut", "waterfall", "isotype", "grouped-symbol", "arc", "gridplot", "proportional-symbol", "ordered-proportional-symbol", "surplus-deficit-filled-line"}
        if identifier in single and len(series) != 1:
            raise TemplateInputError(f"{identifier} needs exactly one series")
        if identifier in {"spine", "population-pyramid", "paired-bar", "paired-column"} and len(series) != 2:
            raise TemplateInputError(f"{identifier} requires two series")
        if identifier == "column-line":
            if len(series) != 2 or len(_list(data.get("series_units"), "series_units", 2, 2)) != 2:
                raise TemplateInputError("column-line requires two series and explicit series_units for both axes")
            for unit in data["series_units"]:
                _label(unit, "series unit")
        if identifier == "slope" and len(cats) not in {2, 3}:
            raise TemplateInputError("slope requires two or three ordered categories")
        if identifier == "radar" and len(cats) < 3:
            raise TemplateInputError("radar requires at least three axes")
        if identifier in {"spine", "marimekko", "proportional-stacked-bar"} and any(sum(s["values"][i] for s in series) <= 0 for i in range(len(cats))):
            raise TemplateInputError("each normalized stack needs a positive total")
        if identifier in {"boxplot", "violin-plot"} and any(len(s["values"]) < 4 for s in series):
            raise TemplateInputError("distribution requires at least four real samples per series")
    elif family == "ranges":
        ranges = _list(data["ranges"], "ranges", upper=30)
        if len(ranges) != len(cats):
            raise TemplateInputError("ranges must match categories")
        for row in ranges:
            required = {"low", "high", "open", "close"} if identifier == "candlestick" else {"low", "high", "value"}
            _object(row, required | {"target"}, "range", required)
            for key, value in row.items():
                _num(value, key)
            if row["low"] > row["high"] or any(not row["low"] <= row[k] <= row["high"] for k in required - {"low", "high"}):
                raise TemplateInputError("range values must lie between low and high")
    elif family == "matrix":
        xs, ys = _list(data["x_labels"], "x_labels", upper=31), _list(data["y_labels"], "y_labels", upper=12)
        for label in xs + ys:
            _label(label, "matrix label")
        if len(_list(data["values"], "matrix rows", upper=12)) != len(ys):
            raise TemplateInputError("matrix row count must match y_labels")
        for row in data["values"]:
            if len(_list(row, "matrix row", upper=31)) != len(xs):
                raise TemplateInputError("matrix column count must match x_labels")
            for value in row:
                _num(value, "matrix value")
        if identifier == "calendar-heatmap" and (len(xs) != 7 or xs != ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            raise TemplateInputError("calendar-heatmap columns must be Mon..Sun, rows are explicit weeks")
    elif family == "timeline":
        for row in _list(data["rows"], "timeline rows", upper=20):
            _object(row, {"label", "start", "end", "value"}, "timeline row", {"label", "start", "end", "value"})
            _label(row["label"], "row label")
            if _num(row["end"], "end") < _num(row["start"], "start") or _num(row["value"], "value") < 0:
                raise TemplateInputError("timeline end must not precede start and value must be nonnegative")
    elif family == "hierarchy":
        paths = _list(data["paths"], "paths", upper=40)
        if len(paths) != len(_list(data["values"], "values", upper=40)):
            raise TemplateInputError("hierarchy paths and values must match")
        for path, value in zip(paths, data["values"]):
            for label in _list(path, "path", upper=4):
                _label(label, "path label")
            if _num(value, "leaf value") <= 0:
                raise TemplateInputError("hierarchy leaf values must be positive")
        if len({tuple(p) for p in paths}) != len(paths) or any(a != b and a == b[:len(a)] for a in paths for b in paths):
            raise TemplateInputError("paths must be unique leaves, never both parent and child")
    elif family == "graph":
        nodes = _list(data["nodes"], "nodes", upper=20)
        for node in nodes:
            _object(node, {"id", "label"}, "node", {"id", "label"})
            _label(node["id"], "node id")
            _label(node["label"], "node label")
        ids = [n["id"] for n in nodes]
        if len(set(ids)) != len(ids):
            raise TemplateInputError("node IDs must be unique")
        for edge in _list(data["links"], "links", upper=80):
            _object(edge, {"source", "target", "value"}, "link", {"source", "target", "value"})
            if edge["source"] not in ids or edge["target"] not in ids or edge["source"] == edge["target"] or _num(edge["value"], "link value") <= 0:
                raise TemplateInputError("links require distinct existing endpoints and positive values")
        if any(not any(e["source"] == node or e["target"] == node for e in data["links"]) for node in ids):
            raise TemplateInputError("each graph node must participate in at least one link")
    elif family in {"geography", "field", "sets", "voronoi"}:
        _validate_special(identifier, data)
    return copy.deepcopy(data), copy.deepcopy(options)


def _option_fields(identifier):
    fields = {"title", "note"}
    if identifier in {"histogram", "frequency-polygons"}: fields.add("bins")
    if identifier == "violin-plot": fields.add("bandwidth")
    if identifier in {"isotype", "grouped-symbol", "arc", "gridplot"}: fields.add("symbol_unit")
    if identifier == "sankey": fields.add("show_values")
    return fields


def _pair(value, where):
    return [_num(v, where) for v in _list(value, where, 2, 2)]


def _validate_special(key, data):
    family = _family(key)
    if family in {"geography", "field"} and data["coordinates"] not in {"planar", "lonlat"}:
        raise TemplateInputError("coordinates must be planar or lonlat; lonlat uses a local equirectangular projection")
    if family == "geography":
        regions = _list(data["regions"], "regions", 0 if key == "dot-density" else 1, 30)
        ids = []
        for region in regions:
            _object(region, {"id", "label", "boundary", "value"}, "region", {"id", "label", "boundary", "value"})
            ids.append(_label(region["id"], "region id")); _label(region["label"], "region label")
            boundary = [_pair(p, "boundary point") for p in _list(region["boundary"], "boundary", 3, 300)]
            if abs(_polygon_area(boundary)) < 1e-12:
                raise TemplateInputError("region polygon must have positive area")
            _validate_polygon(boundary)
            if _num(region["value"], "region value") < 0:
                raise TemplateInputError("geographic values must be nonnegative")
        if len(set(ids)) != len(ids): raise TemplateInputError("region IDs must be unique")
        if key == "choropleth" and data.get("metric_type") not in {"rate", "ratio", "density"}:
            raise TemplateInputError("choropleth requires explicit metric_type rate, ratio or density; raw counts need proportional symbols")
        if key in {"map-proportional-symbol", "scaled-cartogram"} and sum(r["value"] for r in regions) <= 0:
            raise TemplateInputError("proportional geographic charts need positive total values")
        if key == "dot-density":
            for p in _list(data.get("points"), "observed event points", 1, 1000): _pair(p, "point")
        elif "points" in data: raise TemplateInputError("points applies only to dot-density")
        if key == "flow-map":
            for link in _list(data.get("links"), "map links", 1, 80):
                _object(link, {"source", "target", "value"}, "map link", {"source", "target", "value"})
                if link["source"] not in ids or link["target"] not in ids or link["source"] == link["target"] or _num(link["value"], "link value") <= 0:
                    raise TemplateInputError("map links require existing distinct region IDs and positive values")
        elif "links" in data: raise TemplateInputError("links applies only to flow-map")
        if key != "choropleth" and "metric_type" in data: raise TemplateInputError("metric_type applies only to choropleth")
    elif family == "field":
        for axis in ("x", "y"):
            coords = [_num(v, axis) for v in _list(data[axis], axis, 2, 40)]
            if any(a >= b for a,b in zip(coords,coords[1:])):
                raise TemplateInputError("field coordinates must be strictly increasing")
        if len(_list(data["values"], "field rows", 2, 40)) != len(data["y"]): raise TemplateInputError("field rows must match y")
        for row in data["values"]:
            if len(_list(row, "field columns", 2, 40)) != len(data["x"]): raise TemplateInputError("field columns must match x")
            for value in row: _num(value, "field value")
        levels = [_num(v, "level") for v in _list(data["levels"], "contour levels", 1, 10)]
        if levels != sorted(set(levels)): raise TemplateInputError("contour levels must be unique and increasing")
    elif family == "sets":
        sets = _list(data["sets"], "sets", 2, 3)
        for row in sets:
            _object(row, {"label", "members"}, "set", {"label", "members"}); _label(row["label"], "set label")
            members = _list(row["members"], "members", 0, 200)
            for member in members: _label(member, "member")
            if len(set(members)) != len(members): raise TemplateInputError("set members must be unique")
        if len({s["label"] for s in sets}) != len(sets): raise TemplateInputError("set labels must be unique")
    elif family == "voronoi":
        sites = _list(data["sites"], "sites", 2, 30)
        bounds = [_num(v, "bounds") for v in _list(data["bounds"], "bounds", 4, 4)]
        if bounds[0] >= bounds[2] or bounds[1] >= bounds[3]: raise TemplateInputError("bounds must be [xmin,ymin,xmax,ymax]")
        coords = []
        for site in sites:
            _object(site, {"label", "point"}, "site", {"label", "point"}); _label(site["label"], "site label")
            x,y = _pair(site["point"], "site point"); coords.append((x,y))
            if not (bounds[0] <= x <= bounds[2] and bounds[1] <= y <= bounds[3]): raise TemplateInputError("site lies outside bounds")
        if len(set(coords)) != len(coords): raise TemplateInputError("Voronoi sites must be distinct")


def _polygon_area(points):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(points,points[1:]+points[:1]))/2


def _validate_polygon(points):
    polygon=points[:-1] if points[0]==points[-1] else points
    if len({tuple(p) for p in polygon})!=len(polygon):raise TemplateInputError("polygon vertices must be unique apart from an optional closing vertex")
    def orientation(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    edges=list(zip(polygon,polygon[1:]+polygon[:1]))
    for i,(a,b) in enumerate(edges):
        for j,(c,d) in enumerate(edges[i+1:],i+1):
            if j==i+1 or (i==0 and j==len(edges)-1):continue
            if orientation(a,b,c)*orientation(a,b,d)<0 and orientation(c,d,a)*orientation(c,d,b)<0:
                raise TemplateInputError("self-intersecting polygon boundaries are not supported")


def _example(identifier):
    family = _family(identifier)
    if family == "category":
        data = {"categories": ["A", "B", "C", "D"], "series": [{"name": "Observed", "values": [25, 40, 30, 55]}]}
        if identifier in {"paired-bar", "paired-column", "spine", "population-pyramid", "stacked-column-bar", "diverging-stacked-bar", "proportional-stacked-bar", "marimekko", "bump", "streamgraph"}:
            data["series"].append({"name": "Reference", "values": [35, 28, 45, 42]})
        if identifier == "column-line":
            data["series"].append({"name": "Rate", "values": [.2, .3, .4, .35]})
            data["series_units"] = ["units", "ratio"]
        if identifier == "slope":
            data = {"categories": ["Before", "After"], "series": [{"name": "A", "values": [25, 40]}, {"name": "B", "values": [45, 30]}]}
        if identifier in {"diverging-bar", "diverging-stacked-bar", "surplus-deficit-filled-line", "waterfall", "seismogram"}:
            data["series"][0]["values"] = [25, -10, 30, -15]
    elif family == "xy":
        data = {"series": [{"name": "A", "points": [[1, 2], [2, 4], [3, 3], [4, 6], [5, 5]]}]}
        if identifier == "bubble":
            data["series"][0]["points"] = [[1, 2, 10], [2, 4, 20], [3, 3, 35], [4, 6, 15]]
    elif family == "samples":
        data = {"series": [{"name": "A", "values": [2, 3, 3, 5, 6, 8, 8, 9, 10, 12]}, {"name": "B", "values": [4, 4, 6, 7, 8, 9, 10, 14]}]}
    elif family == "ranges":
        data = {"categories": ["A", "B", "C"], "ranges": [{"low": 10, "high": 40, "value": 25, "target": 30}, {"low": 20, "high": 55, "value": 40, "target": 45}, {"low": 30, "high": 70, "value": 50, "target": 55}]}
        if identifier == "candlestick":
            data["ranges"] = [{"low": 10, "high": 40, "open": 20, "close": 30}, {"low": 20, "high": 55, "open": 45, "close": 30}, {"low": 30, "high": 70, "open": 40, "close": 60}]
    elif family == "matrix":
        data = {"x_labels": ["A", "B", "C"], "y_labels": ["Group 1", "Group 2"], "values": [[2, 8, 4], [7, 3, 9]]}
        if identifier == "calendar-heatmap":
            data = {"x_labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "y_labels": ["Week 1", "Week 2"], "values": [[1, 3, 8, 5, 2, 0, 0], [2, 5, 4, 6, 3, 1, 0]]}
    elif family == "timeline":
        data = {"rows": [{"label": "A", "start": 0, "end": 4, "value": 10}, {"label": "B", "start": 2, "end": 8, "value": 20}, {"label": "C", "start": 6, "end": 10, "value": 15}]}
    elif family == "hierarchy":
        data = {"paths": [["North", "A"], ["North", "B"], ["South", "C"], ["South", "D"]], "values": [30, 20, 40, 10]}
    elif family == "graph":
        data = {"nodes": [{"id": c, "label": c} for c in "ABCD"], "links": [{"source": "A", "target": "B", "value": 30}, {"source": "A", "target": "C", "value": 20}, {"source": "B", "target": "D", "value": 30}, {"source": "C", "target": "D", "value": 20}]}
    elif family == "geography":
        data = {"coordinates": "planar", "regions": [{"id":label,"label":label,"boundary":[[x,y],[x+1,y],[x+1,y+1],[x,y+1]],"value":value} for label,x,y,value in [("A",0,0,.2),("B",1,0,.5),("C",0,1,.7),("D",1,1,.9)]]}
        if identifier == "choropleth": data["metric_type"] = "rate"
        if identifier == "flow-map": data["links"] = [{"source":"A","target":"D","value":30},{"source":"B","target":"C","value":10}]
        if identifier == "dot-density": data["points"] = [[.2,.3],[.4,.6],[.7,.3],[1.4,.2],[1.6,1.7]]
    elif family == "field":
        data = {"coordinates":"planar","x":[0,1,2,3],"y":[0,1,2,3],"values":[[1,2,3,2],[2,4,6,3],[3,5,7,4],[2,3,4,2]],"levels":[2.5,4.5,6.5]}
    elif family == "sets":
        data = {"sets":[{"label":"A","members":["1","2","3","4"]},{"label":"B","members":["3","4","5"]},{"label":"C","members":["4","5","6"]}]}
    elif family == "voronoi":
        data = {"bounds":[0,0,10,6],"sites":[{"label":"A","point":[2,2]},{"label":"B","point":[6,1]},{"label":"C","point":[4,5]},{"label":"D","point":[9,4]}]}
    else:
        data = {}
    return {"asset": "chart." + identifier, "data": data, "options": {}}


def _schema(identifier):
    family = _family(identifier)
    label={"type":"string","minLength":1,"maxLength":60,"pattern":r"\S"}
    number={"type":"number"};nonnegative={"type":"number","minimum":0};positive={"type":"number","exclusiveMinimum":0}
    def arr(items,low=1,high=200,unique=False):
        result={"type":"array","items":items,"minItems":low,"maxItems":high}
        if unique:result["uniqueItems"]=True
        return result
    def obj(properties,required=None):
        return {"type":"object","properties":properties,"required":list(properties if required is None else required),"additionalProperties":False}
    pair=arr(number,2,2)
    link=obj({"source":label,"target":label,"value":positive})
    categories=arr(label,1,30,True)
    if family in {"category","samples","xy"}:
        field="points" if family=="xy" else "values"
        item=arr(number,3,3) if identifier=="bubble" else pair if family=="xy" else number
        samples=arr(item,4 if identifier in {"boxplot","violin-plot"} else 1,200)
        single=identifier in {"pie","doughnut","waterfall","isotype","grouped-symbol","arc","gridplot","proportional-symbol","ordered-proportional-symbol","surplus-deficit-filled-line"}
        paired=identifier in {"spine","population-pyramid","paired-bar","paired-column","column-line"}
        properties={"series":arr(obj({"name":label,field:samples}),2 if paired else 1,1 if single else 2 if paired else 6)}
        if family=="category":properties["categories"]=categories
        if identifier=="column-line":properties["series_units"]=arr(label,2,2)
    elif family=="ranges":
        fields={k:number for k in ({"low","high","open","close"} if identifier=="candlestick" else {"low","high","value"})}
        row=obj({**fields,"target":number},fields)
        properties={"categories":categories,"ranges":arr(row,1,30)}
    elif family=="matrix":
        properties={"x_labels":arr(label,1,31),"y_labels":arr(label,1,12),"values":arr(arr(number,1,31),1,12)}
    elif family=="timeline":
        properties={"rows":arr(obj({"label":label,"start":number,"end":number,"value":nonnegative}),1,20)}
    elif family=="hierarchy":
        properties={"paths":arr(arr(label,1,4),1,40,True),"values":arr(positive,1,40)}
    elif family=="graph":
        properties={"nodes":arr(obj({"id":label,"label":label}),1,20),"links":arr(link,1,80)}
    elif family=="geography":
        region=obj({"id":label,"label":label,"boundary":arr(pair,3,300),"value":nonnegative})
        properties={"regions":arr(region,0 if identifier=="dot-density" else 1,30),"coordinates":{"enum":["planar","lonlat"]}}
        if identifier=="dot-density":properties["points"]=arr(pair,1,1000)
        if identifier=="flow-map":properties["links"]=arr(link,1,80)
        if identifier=="choropleth":properties["metric_type"]={"enum":["rate","ratio","density"]}
    elif family=="field":
        properties={"x":arr(number,2,40),"y":arr(number,2,40),"values":arr(arr(number,2,40),2,40),"levels":arr(number,1,10,True),"coordinates":{"enum":["planar","lonlat"]}}
    elif family=="sets":
        properties={"sets":arr(obj({"label":label,"members":arr(label,0,200,True)}),2,3)}
    elif family=="voronoi":
        properties={"sites":arr(obj({"label":label,"point":pair}),2,30),"bounds":arr(number,4,4)}
    else:properties={}
    return {"$schema":"https://json-schema.org/draft/2020-12/schema","title":"Data for chart."+identifier,
            **obj({**properties,**{k:label for k in COMMON_DATA}},properties),"x-engine-family":family,
            "description":"Structural JSON Schema. Engine additionally validates finite values, aligned arrays, semantic counts, graph conservation and measured chart capacity."}


def _avoid(identifier):
    common=["Do not invent missing data or replace unknown values with zero.","Keep units, populations, periods and denominators comparable."]
    family=_family(identifier)
    if family=="samples":common.append("Provide observed samples, not summary averages presented as a distribution.")
    if identifier in {"pie","doughnut","spine","proportional-stacked-bar","treemap","sunburst","marimekko"}:common.append("Parts must be mutually exclusive and belong to the same complete population.")
    if identifier in {"line","slope","bump","column-line","area","streamgraph","seismogram","fan-chart"}:common.append("Order must have an explicit meaning; equal category spacing assumes equal time intervals.")
    if identifier in {"scatterplot","bubble","connected-scatterplot","column-line"}:common.append("Association does not demonstrate causality. A dual axis must not imply equal units or scale.")
    if family in {"geography","field"}:common.append("Do not substitute invented geographic boundaries, random point locations, or unmatched administrative IDs.")
    if identifier=="venn":common.append("Circle areas are schematic, never a quantitative encoding of set sizes.")
    if identifier=="voronoi":common.append("Voronoi area is determined by distance to sites, not the magnitude of category values.")
    if identifier in {"radar","parallel-coordinates"}:common.append("Axes require comparable numeric units; normalize externally and declare that normalization when necessary.")
    if identifier=="sankey":common.append("Intermediate inflow and outflow must balance; cycles and missing flows are rejected.")
    return common


def _limits(identifier):
    family=_family(identifier);limits=[]
    if family=="category":limits.append("Category positions are equally spaced; irregular time intervals require connected-scatterplot with numeric time coordinates.")
    if family in {"geography","field"}:limits.append("Only planar coordinates or regional equirectangular lonlat projection. No antimeridian crossing, polar projection, automatic geocoding, polygon holes or multipolygons.")
    specific={
        "scaled-cartogram":"Noncontiguous polygon-area cartogram; relative area is proportional to value. It is not a contiguous topology-preserving cartogram.",
        "equalised-cartogram":"One equal-size tile per region. Deterministic nearest-free grid assignment approximates relative location; boundaries and adjacency are not preserved.",
        "choropleth":"Requires already-normalized rate, ratio or density values. Engine does not infer denominators.",
        "dot-density":"One point per supplied observed event location; no random population redistribution or synthetic density dots.",
        "map-heatmap":"Sample-centred grid cells with explicit thresholds; midpoint cell boundaries support nonuniform sample spacing. No spatial interpolation.",
        "contour-map":"Marching-squares isolines from a supplied rectangular sample grid. Saddle ambiguity uses centre value; contours do not invent observations.",
        "flow-map":"Straight centroid-to-centroid directed links; widths encode supplied flow. Geographic routes are not inferred.",
        "voronoi":"Unweighted Euclidean Voronoi cells, clipped to supplied bounds. This is not a weighted part-to-whole treemap.",
        "venn":"Two or three finite member sets. Intersections are computed exactly, but circle geometry is schematic.",
        "violin-plot":"Gaussian KDE with Scott/Silverman-style bandwidth based on sample standard deviation; automatic bandwidth is recorded by formula, optional explicit bandwidth. Density support is clipped to observed pooled extrema.",
        "boxplot":"Linear interpolated quartiles; Tukey 1.5-IQR whiskers terminate at observed samples. Outliers stay visible.",
        "histogram":"Equal-width bins across pooled observed samples; automatic bin count ceil(sqrt(n)), capped at20. Multiple distributions overlay translucent count bars.",
        "frequency-polygons":"Equal-width bins from pooled real samples; lines connect bin-centre counts. Same bin edges for every series.",
        "cumulative-curve":"Empirical cumulative distribution (ECDF), not a cumulative monetary or percentage sum.",
        "fan-chart":"One externally supplied interval band and central estimate. Engine does not produce forecasts or infer statistical confidence.",
        "waterfall":"Input values are signed increments; running totals and connectors are computed from zero. Subtotal/total rows are not supported.",
        "chord":"Incident arc allocation and ribbon widths represent supplied link values. Aggregated directional endpoints are recorded, but ribbons have no directional arrowheads.",
        "network":"Deterministic circular node layout; line width encodes link weight. No automatic community discovery or force-directed optimization.",
        "sankey":"Acyclic balanced flow network. Node levels use longest predecessor rank; port offsets and ribbon thickness are computed from conserved quantities.",
        "treemap":"Recursive slice-and-dice rectangles. Not a squarified treemap; very small leaves may have no internal label.",
        "sunburst":"Hierarchical leaf paths determine branch totals and arc spans. Maximum four levels; labels appear only where measured capacity permits.",
        "gridplot":"Whole symbols only. Every category count must be an integer multiple of symbol_unit; at most400 symbols.",
        "isotype":"Repeated editable person glyphs; whole people only, never fractional body parts. At most400 symbols.",
        "arc":"Schematic hemicycle seats from integer counts, max400. Seat colours encode categories; positions do not encode ideological order unless caller orders categories.",
        "grouped-symbol":"Repeated equal-size circles from integer counts, max400. symbol_unit controls the count represented by one circle.",
        "surplus-deficit-filled-line":"Single signed-deviation series with a zero reference. Positive and negative regions are split exactly at interpolated zero crossings.",
        "column-line":"Exactly two series with explicit units. Bars use the left axis and line the right axis; independent scales are always labelled.",
        "bump":"Competition ranks are calculated independently at each category; ties share a rank. Rank1 appears at the top.",
        "spine":"Two complementary nonnegative series, independently normalized to100% per category.",
        "population-pyramid":"Two nonnegative groups on opposing sides of a zero baseline, with shared magnitude scale.",
    }
    if identifier in specific:limits.append(specific[identifier])
    return limits


def chart_assets():
    vocabulary = json.loads(VOCABULARY.read_text(encoding="utf-8"))
    records = []
    for entry in vocabulary["entries"]:
        identifier = entry["id"]
        records.append({"id": "chart." + identifier, "kind": "chart", "label": entry["label"], "display_name":entry["label"],
                        "categories": entry["categories"], "relations": entry["categories"],
                        "executable": identifier in IMPLEMENTED, "status": "executable" if identifier in IMPLEMENTED else "planned",
                        "version": VERSION, "family": _family(identifier), "provenance": {"sources": entry["source"], "license": vocabulary.get("license")},
                        "editable_output": "engine-calculated-native-shapes" if identifier in IMPLEMENTED else "not_implemented",
                        "data_schema":_schema(identifier), "use_cases":[USE.get(c,c) for c in entry["categories"]],
                        "avoid":_avoid(identifier),
                        "preview_refs": [], "validation": {"scope": "algorithm contract; per-artifact Office review separate"}})
    return records


def describe_chart_asset(identifier):
    key = _id(identifier)
    record = next((r for r in chart_assets() if r["id"] == "chart." + key), None)
    if record is None:
        raise TemplateInputError(f"unknown chart asset {identifier!r}")
    limits = ["PPT output is editable shapes; change the data and rebuild to recalculate. It is not an Excel-linked native chart.",
              "Examples are synthetic. This contract does not establish business comparability or causality."]
    if not record["executable"]:
        limits = ["No executable algorithm for this named chart. Selection is rejected until its specialized data and geometry contract is implemented."]
    limits.extend(_limits(key))
    option_schemas={"title":{"type":"string","minLength":1,"maxLength":60},"note":{"type":"string","minLength":1,"maxLength":60},
                    "bins":{"type":"integer","minimum":1,"maximum":30},"symbol_unit":{"type":"number","exclusiveMinimum":0},"bandwidth":{"type":"number","exclusiveMinimum":0},"show_values":{"type":"boolean","default":True}}
    return {**record, "options_schema": {"type": "object", "additionalProperties": False, "properties": {k:option_schemas[k] for k in sorted(_option_fields(key))}},
            "example": _example(key), "use_cases": [USE.get(c, c) for c in record["categories"]],
            "avoid": _avoid(key),
            "limitations": limits, "geometry_policy": "computed", "typography_profile": "report-14pt"}


def instantiate_chart_asset(identifier, data, options=None):
    key = _id(identifier)
    describe_chart_asset(key)
    values, settings = _validate(key, data, {} if options is None else options)
    return {"type": "chart", "asset": "chart." + key, "data": values, "options": settings}


def chart_story(identifier, data=None, options=None):
    from presentation_library import profile_identity
    item = describe_chart_asset(identifier)
    synthetic = data is None
    element = instantiate_chart_asset(identifier, item["example"]["data"] if synthetic else data, options)
    title = (options or {}).get("title", item["label"])
    note = "Synthetic data / algorithm preview" if synthetic else " / ".join(str(data[k]) for k in ("unit", "period", "scope") if k in data)
    if (options or {}).get("note"): note += " / " + options["note"]
    return {"schema_version": "0.1", "project_id": "chart-story-" + _id(identifier), "revision": 1,
            "brief": {"audience": "组件库使用者", "design_profile": profile_identity(), "synthetic": synthetic},
            "sources": [], "facts": {}, "pages": [{"id": "story", "kind": "layout", "layout_version": "0.1", "title": title,
                "layout": {"id": "page", "type": "column", "padding": [48, 32, 48, 30], "gap": 16, "children": [
                    {"id": "title", "type": "leaf", "element": {"type": "text", "role": "title", "text": title}},
                    {"id": "chart", "type": "leaf", "height": 510, "element": element},
                    {"id": "context", "type": "leaf", "element": {"type": "text", "role": "caption", "text": note or "Data supplied by caller"}}]}}]}


class _Canvas:
    def __init__(self, renderer, item):
        from presentation_svg import frame, svg_node
        from presentation_typography import resolve_text_style
        self.node = svg_node("g", {"id": item["id"]})
        self.add = lambda tag, attrs: svg_node(tag, attrs, self.node)
        self.x, self.y, self.w, self.h = frame(item["frame"], item["id"], renderer.canvas)
        self.node.set("data-pptx-bounds", f"{self.x:g} {self.y:g} {self.w:g} {self.h:g}")
        self.style = resolve_text_style(renderer.tokens, "dataCaption")
        self.size = self.style["font_size"]
        if self.size < 12:
            raise TemplateInputError("chart label font must be at least9pt (12SVG px); enlarge the chart instead of shrinking type")
        if self.w < self.size * 16 or self.h < self.size * 8:
            raise TemplateInputError("chart asset container too small for readable labels")
        slots = renderer.tokens["theme"]["slots"]
        self.colors = [slots[f"accent{i}"] for i in range(1, 7)]
        self.palette = renderer.tokens.get("color", {}).get("palette")
        if self.palette:
            self.colors = self.palette["categorical"]
        self.positive = self.palette["roles"]["positive"] if self.palette else self.colors[2]
        self.negative = self.palette["roles"]["negative"] if self.palette else self.colors[4]
        self.text_color = renderer.color(self.style["color"])
        self.left = self.x + max(self.size * 5, self.w * .1)
        self.top = self.y + self.size
        self.right = self.x + self.w - self.size * 2
        self.bottom = self.y + self.h - self.size * 3
        self.width, self.height = self.right - self.left, self.bottom - self.top

    def ramp(self, value, low, high):
        if not self.palette:
            return _ramp(value, low, high)
        from presentation_palette import interpolate_scale
        if low < 0 < high:
            colors = self.palette["diverging"]
            return interpolate_scale(colors[:2], value, low, 0) if value <= 0 else interpolate_scale(colors[1:], value, 0, high)
        return interpolate_scale(self.palette["sequential"], value, low, high)

    def contrast(self, color):
        if not self.palette:
            return _contrast_color(color)
        from presentation_palette import label_ink
        return label_ink(color)

    def text(self, text, x, y, anchor="start", color=None):
        from text_measure import measure_text
        width = measure_text(str(text), size=self.size, family=self.style["font_family"], weight=str(self.style["weight"]))
        left = x-width/2 if anchor=="middle" else (x-width if anchor=="end" else x)
        if left < self.x-.1 or left+width > self.x+self.w+.1 or y-self.size < self.y-.1 or y+self.size*.3 > self.y+self.h+.1:
            raise TemplateInputError(f"chart label {str(text)!r} exceeds its allocated container; shorten labels or enlarge the container")
        node = self.add("text", {"x": x, "y": y, "text-anchor": anchor, "font-size": self.size, "font-family": self.style["font_family"], "fill": color or self.text_color})
        node.text = str(text)

    def line(self, x1, y1, x2, y2, color="#A6A6A6", width=1):
        self.add("line", {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": color, "stroke-width": width})

    def rect(self, x, y, w, h, color):
        if w > 0 and h > 0:
            self.add("rect", {"x": x, "y": y, "width": w, "height": h, "fill": color})

    def circle(self, x, y, radius, color):
        if radius > 0:
            self.add("circle", {"cx": x, "cy": y, "r": radius, "fill": color})

    def path(self, points, color, close=False, fill="none", width=2):
        if points:
            d = "M " + " L ".join(f"{x:g} {y:g}" for x, y in points) + (" Z" if close else "")
            self.add("path", {"d": d, "stroke": color, "stroke-width": width, "fill": fill})

    def legend(self, labels):
        from text_measure import measure_text
        if len(labels) <= 1:
            return
        step = self.width / len(labels)
        for i, label in enumerate(labels):
            if measure_text(label,size=self.size,family=self.style["font_family"],weight=str(self.style["weight"])) > step - self.size * 1.5:
                raise TemplateInputError("legend labels exceed chart capacity")
            x = self.left + i * step
            self.rect(x, self.y + self.h - self.size, self.size * .7, self.size * .7, self.colors[i % 6])
            self.text(label, x + self.size, self.y + self.h - .4 * self.size)

    def axes(self, lo, hi, horizontal=False, descending=False, integer=False):
        self.line(self.left, self.bottom, self.right, self.bottom)
        self.line(self.left, self.top, self.left, self.bottom)
        ticks=list(range(math.ceil(lo),math.floor(hi)+1,max(1,math.ceil((hi-lo)/4)))) if integer else [lo+(hi-lo)*i/4 for i in range(5)]
        for value in ticks:
            fraction=(value-lo)/(hi-lo)
            if horizontal:
                x = self.left + self.width * fraction
                self.line(x, self.top, x, self.bottom, "#E4E8EC")
                self.text(f"{value:.3g}", x, self.bottom + self.size * 1.3, "middle")
            else:
                y = self.top + self.height * fraction if descending else self.bottom - self.height * fraction
                self.line(self.left, y, self.right, y, "#E4E8EC")
                self.text(f"{value:.3g}", self.left - self.size * .5, y + self.size * .3, "end")


def _extent(values, zero=True):
    lo, hi = min(values), max(values)
    if zero:
        lo, hi = min(0, lo), max(0, hi)
    if lo == hi:
        hi = lo + max(1, abs(lo) * .1)
    return lo, hi


def _sector(c, cx, cy, outer, inner, start, end, color):
    # Polygonal vector boundary, with bounded angular sampling; never a raster.
    steps = max(2, math.ceil((end - start) / (math.pi / 60)))
    angles = [start + (end - start) * i / steps for i in range(steps + 1)]
    pts = [(cx + outer * math.cos(a), cy + outer * math.sin(a)) for a in angles]
    pts += [(cx + inner * math.cos(a), cy + inner * math.sin(a)) for a in reversed(angles)] if inner else [(cx, cy)]
    c.path(pts, "#FFFFFF", True, color, 1)


def _category(c, key, data, options):
    cats, series = data["categories"], data["series"]
    values = [s["values"][:] for s in series]
    if key.startswith("ordered-"):
        order = sorted(range(len(cats)), key=lambda i: values[0][i], reverse=True)
        cats, values = [cats[i] for i in order], [[row[i] for i in order] for row in values]
    n, m = len(cats), len(values)
    palette = c.colors
    if key == "column-line":
        _combo(c, data)
        return
    if key in {"pie", "doughnut", "gridplot", "arc", "isotype", "grouped-symbol"}:
        total = sum(values[0])
        if key in {"pie", "doughnut"}:
            radius = min(c.width * .34, c.height * .46)
            cx, cy = c.left + radius, c.top + c.height / 2
            angle = -math.pi / 2
            for i, value in enumerate(values[0]):
                end = angle + math.tau * value / total
                if value:
                    _sector(c, cx, cy, radius, radius * .62 if key == "doughnut" else 0, angle, end, palette[i % 6])
                angle = end
                c.rect(c.left + c.width * .58, c.top + i * c.size * 1.7, c.size * .6, c.size * .6, palette[i % 6])
                c.text(f"{cats[i]}  {value:g} ({value / total:.1%})", c.left + c.width * .58 + c.size, c.top + i * c.size * 1.7 + c.size * .7)
            if n * c.size * 1.7 > c.height:
                raise TemplateInputError("pie legend exceeds chart height")
            return
        unit = options.get("symbol_unit", 1)
        counts = [v / unit for v in values[0]]
        if any(abs(v - round(v)) > 1e-8 for v in counts) or not 1 <= sum(counts) <= 400:
            raise TemplateInputError("symbol charts need integer counts per symbol_unit, total 1..400; never silently round shares")
        sequence = [i for i, value in enumerate(counts) for _ in range(round(value))]
        if key == "arc":
            outer=min(c.width/2,c.height)*.94
            spacing=math.sqrt(math.pi*outer*outer/(2*len(sequence)))*.7
            locations=[];radius=outer-spacing/2
            while radius>spacing/2:
                capacity=max(1,int(math.pi*radius/spacing))
                locations.extend((c.left+c.width/2+radius*math.cos(math.pi+math.pi*(i+.5)/capacity),c.bottom+radius*math.sin(math.pi+math.pi*(i+.5)/capacity)) for i in range(capacity))
                radius-=spacing
            if len(locations)<len(sequence): raise TemplateInputError("hemicycle cannot place symbols at the requested capacity")
            for i,(x,y) in zip(sequence,locations):c.circle(x,y,spacing*.32,palette[i%6])
            c.legend(cats)
            return
        columns = max(1, math.ceil(math.sqrt(len(sequence) * c.width / c.height)))
        rows = math.ceil(len(sequence) / columns)
        pitch = min(c.width / columns, c.height / rows)
        for j, i in enumerate(sequence):
            if key == "isotype":
                x = c.left + (j % columns + .4) * pitch; y = c.top + (j // columns) * pitch
                c.circle(x,y+pitch*.12,pitch*.10,palette[i%6]); c.rect(x-pitch*.13,y+pitch*.25,pitch*.26,pitch*.3,palette[i%6])
                for dx in (-.08,.08): c.line(x+dx*pitch,y+pitch*.52,x+dx*pitch,y+pitch*.8,palette[i%6],pitch*.09)
            elif key == "grouped-symbol":
                c.circle(c.left + (j % columns + .4) * pitch,c.top + (j // columns + .4) * pitch,pitch*.32,palette[i%6])
            else:
                c.rect(c.left + (j % columns) * pitch, c.top + (j // columns) * pitch, pitch * .8, pitch * .8, palette[i % 6])
        c.legend(cats)
        return
    if key in {"proportional-symbol", "ordered-proportional-symbol"}:
        maximum = max(values[0]); step = c.width / n
        for i, value in enumerate(values[0]):
            radius = min(step * .4, c.height * .4) * math.sqrt(value / maximum)
            c.circle(c.left + step * (i + .5), c.top + c.height / 2, radius, palette[i % 6])
            c.text(cats[i], c.left + step * (i + .5), c.bottom + c.size, "middle")
            c.text(f"{value:g}", c.left + step * (i + .5), c.top + c.height / 2 - radius - c.size * .3, "middle")
        return
    if key in {"radar", "parallel-coordinates"}:
        maximum = max(max(v) for v in values) or 1
        if key == "radar":
            radius = min(c.width, c.height) * .4; cx = c.left + c.width / 2; cy = c.top + c.height / 2
            for i, label in enumerate(cats):
                angle = -math.pi / 2 + math.tau * i / n
                c.line(cx, cy, cx + radius * math.cos(angle), cy + radius * math.sin(angle))
                c.text(label, cx + (radius + c.size) * math.cos(angle), cy + (radius + c.size) * math.sin(angle), "middle")
            for j, row in enumerate(values):
                c.path([(cx + radius * row[i] / maximum * math.cos(-math.pi / 2 + math.tau * i / n), cy + radius * row[i] / maximum * math.sin(-math.pi / 2 + math.tau * i / n)) for i in range(n)], palette[j % 6], True)
        else:
            lo, hi = _extent([v for row in values for v in row], False)
            for i, label in enumerate(cats):
                x = c.left + c.width * i / max(1, n - 1); c.line(x, c.top, x, c.bottom); c.text(label, x, c.bottom + c.size, "middle")
            for j, row in enumerate(values):
                c.path([(c.left + c.width * i / max(1, n - 1), c.bottom - c.height * (v - lo) / (hi - lo)) for i, v in enumerate(row)], palette[j % 6])
        c.legend([s["name"] for s in series]); return
    if key == "bump":
        values = [[1 + sum(values[k][i] > values[j][i] for k in range(m)) for i in range(n)] for j in range(m)]
    if key == "spine":
        totals = [sum(row[i] for row in values) for i in range(n)]
        values = [[row[i] / totals[i] * 100 for i in range(n)] for row in values]
    if key == "population-pyramid":
        values[0] = [-v for v in values[0]]
    if key == "waterfall":
        levels = [0]
        for value in values[0]: levels.append(levels[-1] + value)
        lo, hi = _extent(levels); c.axes(lo, hi)
        step = c.width / n
        for i, value in enumerate(values[0]):
            y1 = c.bottom - (levels[i] - lo) / (hi - lo) * c.height; y2 = c.bottom - (levels[i+1] - lo) / (hi - lo) * c.height
            c.rect(c.left + step * (i + .15), min(y1, y2), step * .7, abs(y2 - y1), (c.positive if value >= 0 else c.negative) if c.palette else palette[1 if value >= 0 else 4])
            c.text(cats[i], c.left + step * (i + .5), c.bottom + c.size, "middle")
            if i < n - 1: c.line(c.left + step * (i + .85), y2, c.left + step * (i + 1.15), y2)
        return
    stacked = key in {"stacked-column-bar", "diverging-stacked-bar", "proportional-stacked-bar", "spine", "population-pyramid", "area", "streamgraph", "marimekko"}
    if key == "proportional-stacked-bar":
        totals = [sum(row[i] for row in values) for i in range(n)]
        values = [[row[i] / totals[i] * 100 for i in range(n)] for row in values]
    domain = [v for row in values for v in row]
    if stacked: domain += [sum(max(0, row[i]) for row in values) for i in range(n)] + [sum(min(0, row[i]) for row in values) for i in range(n)]
    lo, hi = _extent(domain)
    if key == "bump":lo,hi=_extent(domain,False)
    if key == "streamgraph":
        hi = max(sum(row[i] for row in values) for i in range(n)) / 2; lo = -hi
    horizontal = key in {"bar", "ordered-bar", "paired-bar", "diverging-bar", "diverging-stacked-bar", "population-pyramid", "spine", "proportional-stacked-bar"}
    lines = key in {"line", "slope", "bump", "area", "surplus-deficit-filled-line", "streamgraph", "frequency-polygons", "seismogram"}
    if key == "marimekko":
        widths = [sum(row[i] for row in values) for i in range(n)]; total = sum(widths); pos = c.left
        for i, width in enumerate(widths):
            w = c.width * width / total; y = c.bottom
            for j, row in enumerate(values):
                h = c.height * row[i] / width; c.rect(pos, y-h, w, h, palette[j % 6]); y -= h
            c.text(cats[i], pos+w/2, c.bottom+c.size, "middle"); pos += w
        c.legend([s["name"] for s in series]); return
    c.axes(lo, hi, horizontal, descending=key=="bump", integer=key=="bump")
    scale = lambda v: (c.left + (v-lo)/(hi-lo)*c.width) if horizontal else (c.top + (v-lo)/(hi-lo)*c.height if key == "bump" else c.bottom - (v-lo)/(hi-lo)*c.height)
    step = (c.height if horizontal else c.width) / n
    if n * c.size * 1.25 > (c.height if horizontal else c.width):
        raise TemplateInputError("category label count exceeds chart capacity")
    for i, label in enumerate(cats):
        if horizontal: c.text(label, c.left-c.size*.5, c.top+step*(i+.5)+c.size*.3, "end")
        else: c.text(label, c.left+step*(i+.5), c.bottom+c.size*1.3, "middle")
    if lines:
        accumulated = [0] * n
        if key == "streamgraph": accumulated = [-sum(row[i] for row in values)/2 for i in range(n)]
        for j, row in enumerate(values):
            coords = [(c.left+step*(i+.5), scale(v+accumulated[i] if stacked else v)) for i, v in enumerate(row)]
            if key == "surplus-deficit-filled-line":
                for i in range(n-1):
                    a,b=coords[i],coords[i+1];va,vb=row[i],row[i+1];zero=scale(0)
                    if va*vb<0:
                        cross=a[0]+(b[0]-a[0])*(-va)/(vb-va)
                        c.path([a,(cross,zero),(a[0],zero)],(c.positive if va>=0 else c.negative),True,(c.positive if va>=0 else c.negative),0)
                        c.path([(cross,zero),b,(b[0],zero)],(c.positive if vb>=0 else c.negative),True,(c.positive if vb>=0 else c.negative),0)
                    else:c.path([a,b,(b[0],zero),(a[0],zero)],(c.positive if va+vb>=0 else c.negative),True,(c.positive if va+vb>=0 else c.negative),0)
                c.path(coords,palette[0])
            elif key in {"area", "streamgraph"}:
                baseline = [(c.left+step*(i+.5), scale(accumulated[i])) for i in reversed(range(n))]
                c.path(coords+baseline, palette[j%6], True, palette[j%6], 1)
            elif key == "seismogram":
                for i, v in enumerate(row): c.line(c.left+step*(i+.5), scale(0), c.left+step*(i+.5), scale(v), palette[j%6], max(1, step*.4))
            else:
                c.path(coords, palette[j%6]);
                for x,y in coords: c.circle(x,y,3,palette[j%6])
            if stacked: accumulated = [accumulated[i]+row[i] for i in range(n)]
    else:
        pos, neg = [0]*n, [0]*n
        for j, row in enumerate(values):
            for i, value in enumerate(row):
                base = (pos[i] if value >= 0 else neg[i]) if stacked else 0
                start,end = scale(base),scale(base+value)
                band = step*.7/(1 if stacked else m); offset = step*.15+(0 if stacked else j*band)
                if key == "lollipop":
                    c.line(c.left+step*(i+.5),scale(0),c.left+step*(i+.5),end,palette[j%6]); c.circle(c.left+step*(i+.5),end,5,palette[j%6])
                elif horizontal: c.rect(min(start,end),c.top+i*step+offset,abs(end-start),band,palette[j%6])
                else: c.rect(c.left+i*step+offset,min(start,end),band,abs(end-start),palette[j%6])
                if value >= 0: pos[i]+=value
                else: neg[i]+=value
    c.legend([s["name"] for s in series])


def _xy(c, key, data):
    series = data["series"]; points = [p for s in series for p in s["points"]]
    xmin,xmax = _extent([p[0] for p in points],False); ymin,ymax = _extent([p[1] for p in points],False)
    pad=min(c.width,c.height)*.08 if key=="bubble" else 4
    xextra=(xmax-xmin)*pad/(c.width-2*pad);yextra=(ymax-ymin)*pad/(c.height-2*pad)
    xmin,xmax=xmin-xextra,xmax+xextra;ymin,ymax=ymin-yextra,ymax+yextra
    strips=key in {"dot-strip-plot","barcode-plot","beeswarm"}
    if strips:c.axes(xmin,xmax,True)
    else:c.axes(ymin,ymax)
    xx=lambda v:c.left+(v-xmin)/(xmax-xmin)*c.width
    yy=lambda v:c.bottom-(v-ymin)/(ymax-ymin)*c.height
    maximum=max((p[2] for p in points if len(p)>2),default=1)
    for j,s in enumerate(series):
        coords=[]; occupied=[]
        for p in s["points"]:
            x,y=xx(p[0]),yy(p[1])
            if key in {"dot-strip-plot","barcode-plot","beeswarm"}:
                y=c.top+(j+.5)*c.height/len(series)
                if key=="beeswarm":
                    for delta in [0]+[v for i in range(1,101) for v in (i*8,-i*8)]:
                        if all((x-a)**2+(y+delta-b)**2>=64 for a,b in occupied):
                            y+=delta; break
                    if not c.top<=y<=c.bottom: raise TemplateInputError("beeswarm requires a larger plot or fewer samples")
                occupied.append((x,y))
            coords.append((x,y))
            if key=="barcode-plot": c.line(x,y-12,x,y+12,c.colors[j%6])
            else: c.circle(x,y, min(c.width,c.height)*.08*math.sqrt(p[2]/maximum) if key=="bubble" else 4,c.colors[j%6])
        if key=="connected-scatterplot": c.path(coords,c.colors[j%6])
    if not strips:
        for i in range(5): c.text(f"{xmin+(xmax-xmin)*i/4:.3g}",c.left+c.width*i/4,c.bottom+c.size*1.3,"middle")
    c.legend([s["name"] for s in series])


def _quantile(values,q):
    values=sorted(values); x=(len(values)-1)*q; i=int(x)
    return values[i]+(values[min(i+1,len(values)-1)]-values[i])*(x-i)


def _samples(c,key,data,options):
    series=data["series"]; all_values=[v for s in series for v in s["values"]]; lo,hi=_extent(all_values,False)
    if key in {"dot-strip-plot","barcode-plot","beeswarm"}:
        _xy(c,key,{"series":[{"name":s["name"],"points":[[v,0] for v in s["values"]]} for s in series]})
        return
    if key in {"boxplot","violin-plot"}:
        c.axes(lo,hi)
        for j,s in enumerate(series):
            values=s["values"]; x=c.left+c.width*(j+.5)/len(series); half=c.width/len(series)*.3
            yy=lambda v:c.bottom-(v-lo)/(hi-lo)*c.height
            if key=="boxplot":
                q1,med,q3=[_quantile(values,q) for q in (.25,.5,.75)]; low=max(min(values),q1-1.5*(q3-q1)); high=min(max(values),q3+1.5*(q3-q1))
                low=min(v for v in values if v>=low); high=max(v for v in values if v<=high)
                c.line(x,yy(low),x,yy(high)); c.rect(x-half,yy(q3),2*half,yy(q1)-yy(q3),c.colors[j%6]); c.line(x-half,yy(med),x+half,yy(med),"#FFFFFF",2)
                for v in values:
                    if v<low or v>high:c.circle(x,yy(v),3,c.colors[j%6])
            else:
                sd=statistics.stdev(values) if len(set(values))>1 else (hi-lo)/10
                bandwidth=options.get("bandwidth",max(sd*1.06*len(values)**(-.2),(hi-lo)/100))
                grid=[lo+(hi-lo)*i/60 for i in range(61)]; density=[sum(math.exp(-.5*((v-sample)/bandwidth)**2) for sample in values) for v in grid]; peak=max(density)
                pts=[(x+half*d/peak,yy(v)) for v,d in zip(grid,density)]+[(x-half*d/peak,yy(v)) for v,d in reversed(list(zip(grid,density)))]; c.path(pts,c.colors[j%6],True,c.colors[j%6])
            c.text(s["name"],x,c.bottom+c.size*1.3,"middle")
        return
    if key=="cumulative-curve":
        c.axes(0,1)
        for j,s in enumerate(series):
            values=sorted(s["values"]); pts=[(c.left, c.bottom)]
            for i,v in enumerate(values):
                x=c.left+(v-lo)/(hi-lo)*c.width; pts.extend([(x,c.bottom-c.height*i/len(values)),(x,c.bottom-c.height*(i+1)/len(values))])
            c.path(pts,c.colors[j%6])
        for i in range(5):c.text(f"{lo+(hi-lo)*i/4:.3g}",c.left+c.width*i/4,c.bottom+c.size*1.3,"middle")
        c.legend([s["name"] for s in series]);return
    bins=options.get("bins",max(2,min(20,math.ceil(math.sqrt(len(all_values)))))); counts=[]
    for s in series:
        row=[0]*bins
        for v in s["values"]:row[min(bins-1,int((v-lo)/(hi-lo)*bins))]+=1
        counts.append({"name":s["name"],"values":row})
    if key=="frequency-polygons":
        _category(c,"line",{"categories":[f"{lo+(hi-lo)*(i+.5)/bins:.2g}" for i in range(bins)],"series":counts},{})
    else:
        maximum=max(max(s["values"]) for s in counts) or 1;c.axes(0,maximum,integer=True);band=c.width/bins
        for j,row in enumerate(counts):
            for i,count in enumerate(row["values"]):
                # Shared bins, touching rectangles; series use translucent overlays.
                h=count/maximum*c.height
                node=c.add("rect",{"x":c.left+i*band,"y":c.bottom-h,"width":band,"height":h,"fill":c.colors[j%6],"stroke":"#FFFFFF","stroke-width":.5,"fill-opacity":1 if len(counts)==1 else .5})
        for i in range(5):c.text(f"{lo+(hi-lo)*i/4:.3g}",c.left+c.width*i/4,c.bottom+c.size*1.3,"middle")
        c.legend([s["name"] for s in series])


def _ranges(c,key,data):
    rows=data["ranges"]; lo,hi=_extent([v for r in rows for v in r.values()]); horizontal=key in {"dot-plot","bullet"}; c.axes(lo,hi,horizontal)
    xx=lambda v:c.left+(v-lo)/(hi-lo)*c.width; yy=lambda v:c.bottom-(v-lo)/(hi-lo)*c.height
    if key=="fan-chart":
        step=c.width/max(1,len(rows)-1)
        fan_x=lambda i:c.left+c.width/2 if len(rows)==1 else c.left+i*step
        pts=[(fan_x(i),yy(r["high"])) for i,r in enumerate(rows)]+[(fan_x(i),yy(r["low"])) for i,r in reversed(list(enumerate(rows)))]; c.path(pts,c.colors[3],True,c.colors[3]); c.path([(fan_x(i),yy(r["value"])) for i,r in enumerate(rows)],c.colors[1])
    for i,(label,r) in enumerate(zip(data["categories"],rows)):
        x=c.left+c.width*(i+.5)/len(rows); y=c.top+c.height*(i+.5)/len(rows)
        if key=="dot-plot":c.line(xx(r["low"]),y,xx(r["high"]),y,c.colors[3],5);c.circle(xx(r["value"]),y,5,c.colors[1])
        elif key=="bullet":
            c.rect(xx(r["low"]),y-15,xx(r["high"])-xx(r["low"]),30,c.colors[3]);c.rect(xx(min(0,r["value"])),y-6,abs(xx(r["value"])-xx(0)),12,c.colors[1])
            if "target" in r:c.line(xx(r["target"]),y-20,xx(r["target"]),y+20,c.colors[0],3)
        elif key=="candlestick":
            color=c.positive if r["close"]>=r["open"] else c.negative;c.line(x,yy(r["low"]),x,yy(r["high"]),color,2);c.rect(x-c.width/len(rows)*.15,min(yy(r["open"]),yy(r["close"])),c.width/len(rows)*.3,max(1,abs(yy(r["open"])-yy(r["close"]))),color)
        if horizontal:c.text(label,c.left-c.size*.5,y+c.size*.3,"end")
        else:c.text(label,fan_x(i) if key=="fan-chart" else x,c.bottom+c.size*1.3,"middle")


def _matrix(c,data):
    rows,cols=len(data["y_labels"]),len(data["x_labels"]); lo,hi=_extent([v for row in data["values"] for v in row],False)
    if c.width/cols<c.size*1.5 or c.height/rows<c.size*1.5:raise TemplateInputError("heatmap labels exceed available capacity")
    for j,row in enumerate(data["values"]):
        for i,v in enumerate(row):
            t=(v-lo)/(hi-lo);rgb=[round(a+(b-a)*t) for a,b in zip((238,244,250),(7,86,184))];color=c.ramp(v,lo,hi) if c.palette else "#"+"".join(f"{n:02X}" for n in rgb);x=c.left+i*c.width/cols;y=c.top+j*c.height/rows
            c.rect(x,y,c.width/cols-2,c.height/rows-2,color);c.text(f"{v:g}",x+c.width/cols/2,y+c.height/rows/2+c.size*.3,"middle",c.contrast(color) if c.palette else ("#FFFFFF" if t>.55 else c.text_color))
        c.text(data["y_labels"][j],c.left-c.size*.5,c.top+(j+.5)*c.height/rows,"end")
    for i,label in enumerate(data["x_labels"]):c.text(label,c.left+(i+.5)*c.width/cols,c.bottom+c.size*1.3,"middle")


def _timeline(c,key,data):
    rows=data["rows"];lo,hi=_extent([v for r in rows for v in (r["start"],r["end"])],False);maximum=max(r["value"] for r in rows) or 1
    for i,r in enumerate(rows):
        if key=="vertical-timeline":
            x=c.left+c.width*(i+.5)/len(rows);y1=c.top+(r["start"]-lo)/(hi-lo)*c.height;y2=c.top+(r["end"]-lo)/(hi-lo)*c.height;c.line(x,y1,x,y2,c.colors[i%6],10);c.text(r["label"],x,c.bottom+c.size,"middle")
        else:
            y=c.top+c.height*(i+.5)/len(rows);x1=c.left+(r["start"]-lo)/(hi-lo)*c.width;x2=c.left+(r["end"]-lo)/(hi-lo)*c.width
            c.line(x1,y,x2,y,c.colors[i%6],18 if key=="priestley-timeline" else 2)
            if key=="circle-timeline":c.circle((x1+x2)/2,y,min(25,c.height/len(rows)*.35)*math.sqrt(r["value"]/maximum),c.colors[i%6])
            c.text(r["label"],c.left-c.size*.5,y+c.size*.3,"end")
    for i in range(5):
        if key=="vertical-timeline":c.text(f"{lo+(hi-lo)*i/4:.3g}",c.left-c.size*.5,c.top+c.height*i/4+c.size*.3,"end")
        else:c.text(f"{lo+(hi-lo)*i/4:.3g}",c.left+c.width*i/4,c.bottom+c.size*1.3,"middle")


def _hierarchy(c,key,data):
    root={"children":{},"value":0}
    for path,value in zip(data["paths"],data["values"]):
        node=root;node["value"]+=value
        for label in path:
            node=node["children"].setdefault(label,{"children":{},"value":0});node["value"]+=value
    if key=="treemap":
        def draw(node,x,y,w,h,depth=0):
            cursor=0
            for i,(label,child) in enumerate(node["children"].items()):
                share=child["value"]/node["value"]
                a,b,d,e=(x+cursor*w,y,w*share,h) if w>=h else (x,y+cursor*h,w,h*share)
                if child["children"]:draw(child,a,b,d,e,depth+1)
                else:
                    c.rect(a,b,max(0,d-2),max(0,e-2),c.colors[(i+depth)%6])
                    if d>len(label)*c.size*.65 and e>c.size*2:c.text(label,a+d/2,b+e/2,"middle",c.contrast(c.colors[(i+depth)%6]))
                cursor+=share
        draw(root,c.left,c.top,c.width,c.height)
    else:
        levels=max(map(len,data["paths"]));radius=min(c.width,c.height)*.45;cx=c.left+c.width/2;cy=c.top+c.height/2
        def draw(node,start,end,depth):
            cursor=start
            for i,(label,child) in enumerate(node["children"].items()):
                nxt=cursor+(end-start)*child["value"]/node["value"]
                _sector(c,cx,cy,radius*(depth+1)/levels,radius*depth/levels,cursor,nxt,c.colors[(i+depth)%6])
                middle=(cursor+nxt)/2;rr=radius*(depth+.5)/levels
                if rr*(nxt-cursor)>len(label)*c.size*.7 and radius/levels>c.size*1.5:
                    c.text(label,cx+rr*math.cos(middle),cy+rr*math.sin(middle),"middle",c.contrast(c.colors[(i+depth)%6]))
                if child["children"]:draw(child,cursor,nxt,depth+1)
                cursor=nxt
        draw(root,-math.pi/2,math.pi*1.5,0)


def _graph(c,key,data,options):
    nodes,links=data["nodes"],data["links"];ids=[n["id"] for n in nodes];incoming={i:0. for i in ids};outgoing={i:0. for i in ids}
    for e in links:incoming[e["target"]]+=e["value"];outgoing[e["source"]]+=e["value"]
    if key=="chord":
        radius=min(c.width,c.height)*.38;cx=c.left+c.width/2;cy=c.top+c.height/2;gap=.05
        total=sum(incoming[i]+outgoing[i] for i in ids);angle=-math.pi/2;spans={};cursors={}
        for j,node in enumerate(nodes):
            i=node["id"];span=(math.tau-gap*len(ids))*(incoming[i]+outgoing[i])/total
            spans[i]=(angle,angle+span);cursors[i]=angle
            _sector(c,cx,cy,radius+9,radius,angle,angle+span,c.colors[j%6])
            middle=angle+span/2;c.text(node["label"],cx+(radius+c.size*2)*math.cos(middle),cy+(radius+c.size*2)*math.sin(middle),"middle")
            angle+=span+gap
        for e in links:
            slices=[]
            for node in (e["source"],e["target"]):
                start=cursors[node];end=start+(spans[node][1]-spans[node][0])*e["value"]/(incoming[node]+outgoing[node]);cursors[node]=end
                steps=max(2,math.ceil((end-start)/.05));slices.append([(cx+radius*math.cos(start+(end-start)*i/steps),cy+radius*math.sin(start+(end-start)*i/steps)) for i in range(steps+1)])
            a,b=slices
            path="M "+" L ".join(f"{x:g} {y:g}" for x,y in a)+f" Q {cx:g} {cy:g} {b[0][0]:g} {b[0][1]:g} L "+" L ".join(f"{x:g} {y:g}" for x,y in b[1:])+f" Q {cx:g} {cy:g} {a[0][0]:g} {a[0][1]:g} Z"
            c.add("path",{"d":path,"fill":c.colors[ids.index(e["source"])%6],"fill-opacity":.55})
        return
    if key=="sankey":
        degrees={i:sum(e["target"]==i for e in links) for i in ids};ranks={i:0 for i in ids};queue=[i for i in ids if not degrees[i]];seen=[]
        while queue:
            i=queue.pop(0);seen.append(i)
            for e in links:
                if e["source"]==i:
                    target=e["target"];ranks[target]=max(ranks[target],ranks[i]+1);degrees[target]-=1
                    if degrees[target]==0:queue.append(target)
        if len(seen)!=len(ids):raise TemplateInputError("sankey supports acyclic flows only")
        for i in ids:
            if incoming[i] and outgoing[i] and abs(incoming[i]-outgoing[i])>1e-8*max(incoming[i],outgoing[i]):raise TemplateInputError("sankey intermediate nodes must conserve flow")
        levels={r:[i for i in ids if ranks[i]==r] for r in set(ranks.values())}
        if any(c.height-20*(len(v)-1)<=0 for v in levels.values()):
            raise TemplateInputError("sankey has too many nodes at one level for the available height; enlarge or split the chart")
        units=min((c.height-20*(len(v)-1))/sum(max(incoming[i],outgoing[i]) for i in v) for v in levels.values());positions={}
        for rank,items in levels.items():
            y=c.top
            for i in items:positions[i]=(c.left+rank/max(1,max(ranks.values()))*(c.width-15),y);y+=max(incoming[i],outgoing[i])*units+20
        ins={i:0. for i in ids};outs={i:0. for i in ids}
        for e in links:
            a,b=e["source"],e["target"];x1,y1=positions[a];x2,y2=positions[b];w=e["value"]*units;y1+=outs[a];y2+=ins[b];outs[a]+=w;ins[b]+=w;mid=(x1+x2)/2
            d=f"M {x1+15} {y1} C {mid} {y1} {mid} {y2} {x2} {y2} L {x2} {y2+w} C {mid} {y2+w} {mid} {y1+w} {x1+15} {y1+w} Z"
            c.add("path",{"d":d,"fill":c.colors[3]})
            if options.get("show_values",True):c.text(f"{e['value']:g}",mid,(y1+y2+w)/2,"middle")
        for node in nodes:
            value=max(incoming[node["id"]],outgoing[node["id"]]);x,y=positions[node["id"]];h=value*units;c.rect(x,y,15,h,c.colors[1])
            label=f"{node['label']} ({value:g})" if options.get("show_values",True) else node["label"]
            final=ranks[node["id"]]==max(ranks.values());c.text(label,x-5 if final else x+20,y+c.size,"end" if final else "start")
        return
    radius=min(c.width,c.height)*.38;cx=c.left+c.width/2;cy=c.top+c.height/2;positions={i:(cx+radius*math.cos(math.tau*j/len(ids)-math.pi/2),cy+radius*math.sin(math.tau*j/len(ids)-math.pi/2)) for j,i in enumerate(ids)}
    maximum=max(e["value"] for e in links)
    for e in links:
        a,b=positions[e["source"]],positions[e["target"]];width=1+8*e["value"]/maximum
        if key=="chord":c.add("path",{"d":f"M {a[0]} {a[1]} Q {cx} {cy} {b[0]} {b[1]}","fill":"none","stroke":c.colors[3],"stroke-width":width})
        else:c.line(*a,*b,c.colors[3],width)
    for i,node in enumerate(nodes):
        x,y=positions[node["id"]];c.circle(x,y,9,c.colors[i%6]);c.text(node["label"],x,y-c.size,"middle")


def render_chart_asset(renderer,item):
    key=_id(item.get("asset"));data,options=_validate(key,item.get("data"),item.get("options",{}))
    extras=set(item)-{"id","type","asset","data","options","frame","metadata","source_ref","content_ref","relation_ref","role","opacity"}
    if extras:raise TemplateInputError(f"chart asset does not accept raw style or geometry fields: {sorted(extras)}")
    c=_Canvas(renderer,item);family=_family(key)
    if family=="category":_category(c,key,data,options)
    elif family=="xy":_xy(c,key,data)
    elif family=="samples":_samples(c,key,data,options)
    elif family=="ranges":_ranges(c,key,data)
    elif family=="matrix":_matrix(c,data)
    elif family=="timeline":_timeline(c,key,data)
    elif family=="hierarchy":_hierarchy(c,key,data)
    elif family=="graph":_graph(c,key,data,options)
    elif family=="geography":_geography(c,key,data)
    elif family=="field":_field(c,key,data)
    elif family=="sets":_sets(c,data)
    elif family=="voronoi":_voronoi(c,data)
    return c.node


def _combo(c, data):
    bars, line = data["series"]
    lo, hi = _extent(bars["values"]); llo, lhi = _extent(line["values"])
    # A separate, explicitly labelled scale is part of the contract, never hidden.
    c.right -= c.size * 3; c.width = c.right - c.left
    c.axes(lo,hi); c.line(c.right,c.top,c.right,c.bottom)
    c.text(data["series_units"][0],c.left,c.top)
    c.text(data["series_units"][1],c.right,c.top,"end")
    for i in range(5): c.text(f"{llo+(lhi-llo)*i/4:.3g}",c.right+c.size*.4,c.bottom-c.height*i/4+c.size*.3)
    step=c.width/len(data["categories"]); coords=[]
    yy=lambda v:c.bottom-c.height*(v-lo)/(hi-lo)
    for i,(label,value,rate) in enumerate(zip(data["categories"],bars["values"],line["values"])):
        x=c.left+step*(i+.5); y=yy(value)
        c.rect(x-step*.3,min(yy(0),y),step*.6,abs(yy(0)-y),c.colors[1])
        coords.append((x,c.bottom-c.height*(rate-llo)/(lhi-llo)))
        c.text(label,x,c.bottom+c.size*1.3,"middle")
    c.path(coords,c.colors[2],width=3)
    for x,y in coords:c.circle(x,y,4,c.colors[2])
    # Legend colours correspond to the two marks rather than the default slots.
    for i,(row,color) in enumerate(zip(data["series"],[c.colors[1],c.colors[2]])):
        x=c.left+i*c.width/2;c.rect(x,c.y+c.h-c.size,c.size*.7,c.size*.7,color);c.text(row["name"],x+c.size,c.y+c.h-.4*c.size)


def _projector(c, points, coordinates="planar"):
    if coordinates == "lonlat":
        if any(not -180<=x<=180 or not -85<=y<=85 for x,y in points):
            raise TemplateInputError("lonlat input requires longitude [-180,180], latitude [-85,85]")
        if max(p[0] for p in points)-min(p[0] for p in points)>180:
            raise TemplateInputError("antimeridian crossing requires a dedicated projection; this asset supports regional maps only")
        factor=math.cos(math.radians(sum(p[1] for p in points)/len(points)))
    else:factor=1
    xs=[p[0]*factor for p in points];ys=[p[1] for p in points];xmin,xmax=_extent(xs,False);ymin,ymax=_extent(ys,False)
    scale=min(c.width/(xmax-xmin),c.height/(ymax-ymin));ox=c.left+(c.width-(xmax-xmin)*scale)/2;oy=c.top+(c.height-(ymax-ymin)*scale)/2
    return lambda p:(ox+(p[0]*factor-xmin)*scale,oy+(ymax-p[1])*scale)


def _centroid(points):
    area=_polygon_area(points)
    return tuple(sum((a[j]+b[j])*(a[0]*b[1]-b[0]*a[1]) for a,b in zip(points,points[1:]+points[:1]))/(6*area) for j in (0,1))


def _ramp(value, lo, hi):
    t=(value-lo)/(hi-lo) if hi>lo else .5
    return "#"+"".join(f"{round(a+(b-a)*t):02X}" for a,b in zip((225,235,245),(7,86,184)))


def _contrast_color(color):
    r,g,b=(int(color[i:i+2],16) for i in (1,3,5))
    return "#333333" if .2126*r+.7152*g+.0722*b>155 else "#FFFFFF"


def _geography(c,key,data):
    regions=data["regions"]; points=[p for r in regions for p in r["boundary"]]+data.get("points",[])
    project=_projector(c,points,data["coordinates"])
    polygons={r["id"]:[project(p) for p in r["boundary"]] for r in regions}
    centers={i:_centroid(p) for i,p in polygons.items()}
    values=[r["value"] for r in regions];lo,hi=_extent(values,False) if values else (0,1)
    if key=="equalised-cartogram":
        # Equal-size tiles preserve approximate relative position; each tile is one region.
        pitch=min(c.width,c.height)/max(2,math.ceil(math.sqrt(len(regions))));used=set()
        for i,r in enumerate(sorted(regions,key=lambda r:(centers[r["id"]][1],centers[r["id"]][0]))):
            cx,cy=centers[r["id"]];cols=max(1,int(c.width/pitch));rows=max(1,int(c.height/pitch))
            cells=[(x,y) for x in range(cols) for y in range(rows) if (x,y) not in used]
            if not cells:raise TemplateInputError("equalised cartogram needs a larger plot")
            x,y=min(cells,key=lambda p:((c.left+(p[0]+.5)*pitch-cx)**2+(c.top+(p[1]+.5)*pitch-cy)**2,p))
            used.add((x,y));c.rect(c.left+x*pitch,c.top+y*pitch,pitch-3,pitch-3,c.colors[i%6]);c.text(r["label"],c.left+(x+.5)*pitch,c.top+(y+.5)*pitch,"middle",c.contrast(c.colors[i%6]))
        return
    if key=="scaled-cartogram":
        # Noncontiguous cartogram: polygon area, not radius, encodes the value.
        # A common scale prevents touching/overlapping polygons after centroid scaling.
        max_scale=min(abs(_polygon_area(polygons[r["id"]]))/r["value"] for r in regions if r["value"]>0)*.72
        for r in regions:
            p=polygons[r["id"]];cx,cy=centers[r["id"]];factor=math.sqrt(r["value"]*max_scale/abs(_polygon_area(p)))
            polygons[r["id"]]=[(cx+(x-cx)*factor,cy+(y-cy)*factor) for x,y in p]
        for _ in range(60):
            boxes=[(min(x for x,y in p),min(y for x,y in p),max(x for x,y in p),max(y for x,y in p)) for p in polygons.values()]
            overlaps=any(min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6 for i,a in enumerate(boxes) for b in boxes[i+1:])
            if not overlaps:break
            polygons={i:[(centers[i][0]+(x-centers[i][0])*.85,centers[i][1]+(y-centers[i][1])*.85) for x,y in p] for i,p in polygons.items()}
        else:raise TemplateInputError("cartogram region centroids coincide; cannot place nonoverlapping scaled polygons")
    for i,r in enumerate(regions):
        color=c.ramp(r["value"],lo,hi) if key=="choropleth" else (c.colors[i%6] if key=="scaled-cartogram" else "#EEF4FA")
        c.path(polygons[r["id"]],"#A6A6A6",True,color,1)
        x,y=centers[r["id"]]
        if key=="map-proportional-symbol":c.circle(x,y,min(c.width,c.height)*.12*math.sqrt(r["value"]/max(values)),c.colors[1])
        c.text(r["label"],x,y-c.size*.4,"middle",c.text_color)
    if key=="dot-density":
        for p in data["points"]:c.circle(*project(p),3,c.colors[1])
    if key=="flow-map":
        maximum=max(e["value"] for e in data["links"])
        for e in data["links"]:
            a,b=centers[e["source"]],centers[e["target"]];width=1+9*e["value"]/maximum
            c.line(*a,*b,c.colors[1],width)
            dx,dy=b[0]-a[0],b[1]-a[1];norm=math.hypot(dx,dy)
            if norm<=1e-9:raise TemplateInputError("flow-map endpoints have coincident centroids; supply distinct regional geometries")
            ux,uy=dx/norm,dy/norm
            c.path([b,(b[0]-12*ux+5*uy,b[1]-12*uy-5*ux),(b[0]-12*ux-5*uy,b[1]-12*uy+5*ux)],c.colors[1],True,c.colors[1])
    if key=="choropleth":
        for i in range(5):
            value=lo+(hi-lo)*i/4;x=c.left+i*c.width/5;c.rect(x,c.y+c.h-c.size,c.size*.7,c.size*.7,c.ramp(value,lo,hi));c.text(f"{value:.3g}",x+c.size,c.y+c.h-.4*c.size)


def _field(c,key,data):
    xs,ys,values,levels=data["x"],data["y"],data["values"],data["levels"]
    project=_projector(c,[(xs[0],ys[0]),(xs[-1],ys[-1])],data["coordinates"])
    if key=="map-heatmap":
        bin_colors = [c.ramp(i, 0, len(levels)) for i in range(len(levels)+1)]
        if c.palette:
            low = min(min(v for row in values for v in row), levels[0])
            high = max(max(v for row in values for v in row), levels[-1])
            representatives = [(low+levels[0])/2]+[(a+b)/2 for a,b in zip(levels,levels[1:])]+[(levels[-1]+high)/2]
            bin_colors = [c.ramp(v, low, high) for v in representatives]
        # Sample-centred cells; midpoint boundaries preserve irregular spatial spacing.
        xb=[xs[0]]+[(a+b)/2 for a,b in zip(xs,xs[1:])]+[xs[-1]]
        yb=[ys[0]]+[(a+b)/2 for a,b in zip(ys,ys[1:])]+[ys[-1]]
        for j,row in enumerate(values):
            for i,value in enumerate(row):
                a=project((xb[i],yb[j+1]));b=project((xb[i+1],yb[j]));bin_index=sum(value>v for v in levels)
                c.rect(a[0],a[1],b[0]-a[0],b[1]-a[1],bin_colors[bin_index])
    else:
        # Marching squares with the centre-value decider for ambiguous saddles.
        for level in levels:
            color=c.ramp(level,levels[0],levels[-1])
            for j in range(len(ys)-1):
                for i in range(len(xs)-1):
                    ps=[(xs[i],ys[j]),(xs[i+1],ys[j]),(xs[i+1],ys[j+1]),(xs[i],ys[j+1])];vs=[values[j][i],values[j][i+1],values[j+1][i+1],values[j+1][i]];hits=[]
                    for k in range(4):
                        q=(k+1)%4
                        if (vs[k]>level)!=(vs[q]>level):
                            t=(level-vs[k])/(vs[q]-vs[k]);hits.append((k,project((ps[k][0]+t*(ps[q][0]-ps[k][0]),ps[k][1]+t*(ps[q][1]-ps[k][1])))))
                    if len(hits)==2:c.line(*hits[0][1],*hits[1][1],color,2)
                    elif len(hits)==4:
                        use_offset=(sum(vs)/4>level)==(vs[0]>level);ordered=hits[1:]+hits[:1] if use_offset else hits
                        for a,b in (ordered[:2],ordered[2:]):c.line(*a[1],*b[1],color,2)
    if key=="map-heatmap":
        # Every cell colour describes a threshold interval, including tails.
        # Use the same bin-index colour scale in the legend as in the plot.
        labels=[f"≤{levels[0]:g}"]+[f"({a:g}, {b:g}]" for a,b in zip(levels,levels[1:])]+[f">{levels[-1]:g}"]
        for i,label in enumerate(labels):
            x=c.left+i*c.width/len(labels)
            c.rect(x,c.y+c.h-c.size,c.size*.7,c.size*.7,bin_colors[i])
            c.text(label,x+c.size,c.y+c.h-.4*c.size)
    else:
        for i,value in enumerate(levels):
            x=c.left+i*c.width/len(levels);c.rect(x,c.y+c.h-c.size,c.size*.7,c.size*.7,c.ramp(value,levels[0],levels[-1]));c.text(f"{value:g}",x+c.size,c.y+c.h-.4*c.size)


def _clip_halfplane(poly,a,b,threshold):
    result=[]
    for p,q in zip(poly,poly[1:]+poly[:1]):
        pv=a*p[0]+b*p[1]-threshold;qv=a*q[0]+b*q[1]-threshold
        if pv<=1e-10:result.append(p)
        if (pv<=0)!=(qv<=0):
            t=pv/(pv-qv);result.append((p[0]+t*(q[0]-p[0]),p[1]+t*(q[1]-p[1])))
    return result


def _voronoi_cells(data):
    x1,y1,x2,y2=data["bounds"];cells=[]
    for site in data["sites"]:
        poly=[(x1,y1),(x2,y1),(x2,y2),(x1,y2)];sx,sy=site["point"]
        for other in data["sites"]:
            if other is site:continue
            ox,oy=other["point"];poly=_clip_halfplane(poly,2*(ox-sx),2*(oy-sy),ox*ox+oy*oy-sx*sx-sy*sy)
        cells.append(poly)
    return cells


def _voronoi(c,data):
    x1,y1,x2,y2=data["bounds"];project=_projector(c,[(x1,y1),(x2,y2)])
    for i,(site,poly) in enumerate(zip(data["sites"],_voronoi_cells(data))):
        c.path([project(p) for p in poly],"#FFFFFF",True,c.colors[i%6],2)
        x,y=project(site["point"]);contrast=c.contrast(c.colors[i%6]);c.circle(x,y,3,contrast);c.text(site["label"],x,y-c.size*.3,"middle",contrast)


def _sets(c,data):
    sets=data["sets"];n=len(sets);cx=c.left+c.width/2;cy=c.top+c.height/2;r=min(c.width*.22,c.height*.33)
    centers=[(cx-r*.55,cy),(cx+r*.55,cy)] if n==2 else [(cx-r*.55,cy-r*.25),(cx+r*.55,cy-r*.25),(cx,cy+r*.65)]
    for i,(s,(x,y)) in enumerate(zip(sets,centers)):
        c.add("circle",{"cx":x,"cy":y,"r":r,"fill":c.colors[i],"fill-opacity":.18,"stroke":c.colors[i],"stroke-width":2})
        c.text(s["label"],x,y-r-c.size*.4,"middle")
    members=set(v for s in sets for v in s["members"]);counts={i:0 for i in range(1,2**n)}
    for value in members:counts[sum(2**i for i,s in enumerate(sets) if value in s["members"])]+=1
    spots={1:(cx-r*.95,cy),2:(cx+r*.95,cy),3:(cx,cy)} if n==2 else {1:(cx-r*.95,cy-r*.35),2:(cx+r*.95,cy-r*.35),3:(cx,cy-r*.55),4:(cx,cy+r*.95),5:(cx-r*.5,cy+r*.4),6:(cx+r*.5,cy+r*.4),7:(cx,cy+r*.15)}
    for mask,(x,y) in spots.items():c.text(str(counts[mask]),x,y+c.size*.3,"middle")
    c.text("Schematic area; labels show exact set counts",c.left,c.y+c.h-c.size*.3)
