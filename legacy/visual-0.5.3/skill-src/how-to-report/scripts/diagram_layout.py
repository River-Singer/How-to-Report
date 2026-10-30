"""Small deterministic graph placement and orthogonal routing; no inferred edges.

Ranks only use explicit directed non-feedback edges. Back edges encountered while
ranking remain in the rendered graph. This is a bounded diagram aid, not a graph
semantics validator or an optimal layout engine.
"""
from __future__ import annotations

import heapq
import math
import unicodedata


def wrap_label(value, columns=10):
    """Wrap at display-cell boundaries without dropping any supplied characters."""
    lines, line, width = [], '', 0
    for char in value:
        cells = 1 if unicodedata.east_asian_width(char) in ('W', 'F') else .55
        if char == '\n' or width + cells > columns:
            lines.append(line)
            line, width = '', 0
        if char != '\n':
            line += char
            width += cells
    if line or not lines:
        lines.append(line)
    return lines


def intersects(a, b, rect, padding=0):
    """Whether an axis-aligned segment enters the open interior of a rectangle."""
    x, y, w, h = rect
    left, top, right, bottom = x-padding, y-padding, x+w+padding, y+h+padding
    if a[0] == b[0]:
        return left < a[0] < right and max(min(a[1], b[1]), top) < min(max(a[1], b[1]), bottom)
    if a[1] == b[1]:
        return top < a[1] < bottom and max(min(a[0], b[0]), left) < min(max(a[0], b[0]), right)
    raise ValueError('diagram routing must remain axis-aligned')


def _ranks(nodes, edges):
    adjacency = {n['id']: [] for n in nodes}
    for e in sorted(edges, key=lambda e: e['id']):
        if e['relation'] not in ('feedback', 'association'):
            adjacency[e['from']].append(e['to'])
    # Remove DFS back edges from the placement DAG only. Never remove an edge
    # from the content or label it feedback when the author did not do so.
    state, dag = {}, {nid: [] for nid in adjacency}
    def visit(nid):
        state[nid] = 1
        for child in sorted(adjacency[nid]):
            if state.get(child) == 1:
                continue
            if not state.get(child):
                visit(child)
            dag[nid].append(child)
        state[nid] = 2
    for nid in sorted(adjacency):
        if not state.get(nid):
            visit(nid)
    incoming = {nid: 0 for nid in dag}
    for children in dag.values():
        for child in children:
            incoming[child] += 1
    rank = dict.fromkeys(dag, 0)
    ready = sorted(nid for nid in dag if not incoming[nid])
    while ready:
        nid = ready.pop(0)
        for child in dag[nid]:
            rank[child] = max(rank[child], rank[nid]+1)
            incoming[child] -= 1
            if not incoming[child]:
                ready.append(child)
                ready.sort()
    # An association-only object sits alongside its connected subject, without
    # adding another step to the directed chain (e.g. a comparison axis).
    directed = {e[k] for e in edges if e['relation'] not in ('association','feedback') for k in ('from','to')}
    for e in sorted(edges, key=lambda e: e['id']):
        if e['relation'] == 'association':
            if e['from'] not in directed and e['to'] in directed:
                rank[e['from']] = rank[e['to']]
            elif e['to'] not in directed and e['from'] in directed:
                rank[e['to']] = rank[e['from']]
    return rank


def _route(start, end, obstacles, extent):
    """Visibility-grid Dijkstra minimizes length plus bends around every node."""
    margin = 20
    xs = {start[0], end[0], 12, extent[0]-12}
    ys = {start[1], end[1], 12, extent[1]-12}
    for x,y,w,h in obstacles:
        xs.update((x-margin, x+w+margin))
        ys.update((y-margin, y+h+margin))
    xs = sorted(x for x in xs if 0 <= x <= extent[0])
    ys = sorted(y for y in ys if 0 <= y <= extent[1])
    points = {(x,y) for x in xs for y in ys if not any(rx < x < rx+w and ry < y < ry+h for rx,ry,w,h in obstacles)}
    first = (start, -1)
    cost, parent = {first: 0}, {}
    queue = [(0, start, -1)]
    target = None
    while queue:
        distance, point, axis = heapq.heappop(queue)
        key = point, axis
        if distance != cost[key]:
            continue
        if point == end:
            target = key
            break
        ix, iy = xs.index(point[0]), ys.index(point[1])
        candidates = []
        if ix: candidates.append(((xs[ix-1],point[1]),0))
        if ix+1 < len(xs): candidates.append(((xs[ix+1],point[1]),0))
        if iy: candidates.append(((point[0],ys[iy-1]),1))
        if iy+1 < len(ys): candidates.append(((point[0],ys[iy+1]),1))
        for neighbor, next_axis in candidates:
            if neighbor not in points or any(intersects(point, neighbor, r, 8) for r in obstacles):
                continue
            extra = abs(point[0]-neighbor[0])+abs(point[1]-neighbor[1])
            new_cost = distance + extra + (28 if axis not in (-1,next_axis) else 0)
            next_key = neighbor, next_axis
            if new_cost < cost.get(next_key, math.inf):
                cost[next_key], parent[next_key] = new_cost, key
                heapq.heappush(queue, (new_cost, neighbor, next_axis))
    if target is None:
        raise ValueError('diagram has no clear route; split the relationship into smaller views')
    path = []
    while target in parent:
        path.append(target[0]); target = parent[target]
    path.append(start); path.reverse()
    compact = []
    for p in path:
        while len(compact) >= 2 and (compact[-2][0] == compact[-1][0] == p[0] or compact[-2][1] == compact[-1][1] == p[1]):
            compact.pop()
        compact.append(p)
    return compact


def layout_diagram(data):
    nodes, edges = data['nodes'], data['edges']
    ranks = _ranks(nodes, edges)
    lanes = data.get('lanes', [])
    vertical = not lanes and data.get('direction', 'vertical' if max(ranks.values()) >= 4 else 'horizontal') == 'vertical'
    width = 260
    height = max(76, max(len(wrap_label(n['label'])) for n in nodes)*25+26)
    edge_lines = {e['id']: wrap_label(e.get('short_label',e['label']), 10) for e in edges}
    label_height = max((len(v)*22+12 for v in edge_lines.values()), default=34)
    gap = max(104, label_height+32) if vertical else 248
    pitch = (height if vertical else width)+gap
    boxes, lane_boxes = {}, []
    if lanes:
        top = 66
        for lane in lanes:
            members = [n for n in nodes if n['lane'] == lane['id']]
            groups = {rank: sorted(n['id'] for n in members if ranks[n['id']]==rank) for rank in set(ranks.values())}
            count = max((len(g) for g in groups.values()), default=1)
            lane_height = max(1,count)*(height+80)+44
            for rank, group in groups.items():
                for i,nid in enumerate(group):
                    boxes[nid] = (190+rank*pitch, top+44+i*(height+80), width,height)
            lane_boxes.append({'id':lane['id'],'label':lane['label'],'y':top,'height':lane_height})
            top += lane_height+20
    else:
        groups = {rank: sorted(nid for nid in ranks if ranks[nid]==rank) for rank in set(ranks.values())}
        cross_pitch = (width if vertical else height)+max(80,label_height+24)
        count = max(len(g) for g in groups.values())
        for rank, group in groups.items():
            for i,nid in enumerate(group):
                cross = 72 + ((count-len(group))/2+i)*cross_pitch
                boxes[nid] = ((cross,72+rank*pitch,width,height) if vertical else (72+rank*pitch,cross,width,height))
    extent = (max(x+w for x,y,w,h in boxes.values())+72, max(y+h for x,y,w,h in boxes.values())+max(90,label_height+40))
    if lane_boxes:
        extent = (extent[0], max(extent[1], max(l['y']+l['height'] for l in lane_boxes)+20))
    routes, labels = {}, {}
    used_labels = []
    def port(rect, side):
        x,y,w,h = rect
        return {'left':(x,y+h/2),'right':(x+w,y+h/2),'top':(x+w/2,y),'bottom':(x+w/2,y+h)}[side]
    def extend(point,side):
        dx,dy={'left':(-20,0),'right':(20,0),'top':(0,-20),'bottom':(0,20)}[side]
        return point[0]+dx, point[1]+dy
    for edge in sorted(edges,key=lambda e:(e['relation']=='feedback',e['id'])):
        source,target = boxes[edge['from']],boxes[edge['to']]
        backwards = ranks[edge['to']] <= ranks[edge['from']]
        if edge['relation']=='feedback' or (backwards and edge['relation']!='association'):
            sides = ('right','right') if vertical else ('bottom','bottom')
        elif ranks[edge['to']] == ranks[edge['from']]:
            sides = ('right','left') if vertical else ('bottom','top')
            if (target[0] if vertical else target[1]) < (source[0] if vertical else source[1]):
                sides = sides[::-1]
        else:
            sides = ('bottom','top') if vertical else ('right','left')
        start,end = port(source,sides[0]),port(target,sides[1])
        path = [start]+_route(extend(start,sides[0]),extend(end,sides[1]),[*boxes.values(),*used_labels],extent)+[end]
        routes[edge['id']] = path
        lines = edge_lines[edge['id']]
        lw = max(40,min(212,max(len(v) for v in lines)*20+12))
        lh = len(lines)*22+12
        segments = sorted(zip(path,path[1:]),key=lambda s:abs(s[0][0]-s[1][0])+abs(s[0][1]-s[1][1]),reverse=True)
        found = None
        for a,b in segments:
            cx,cy=(a[0]+b[0])/2,(a[1]+b[1])/2
            candidates = [(cx-lw/2,cy-lh-8,lw,lh),(cx-lw/2,cy+8,lw,lh)] if a[1]==b[1] else [(cx+10,cy-lh/2,lw,lh),(cx-lw-10,cy-lh/2,lw,lh)]
            for candidate in candidates:
                x,y,w,h=candidate
                if x<8 or y<8: continue
                blocks_path = any(intersects(a,b,candidate,4) for route in routes.values() for a,b in zip(route,route[1:]))
                if not blocks_path and not any(x < bx+bw+6 and x+w+6 > bx and y < by+bh+6 and y+h+6 > by for bx,by,bw,bh in [*boxes.values(),*used_labels]):
                    found=candidate; break
            if found: break
        keyed = found is None
        if keyed:
            # Explicit numbered key below the graph is preferable to a label
            # covering a node. It remains visible and therefore consumes space.
            found=(72,extent[1],lw,lh)
            extent=(extent[0],extent[1]+lh+12)
        a,b=segments[0]
        labels[edge['id']]={'rect':found,'lines':lines,'keyed':keyed,'key_point':((a[0]+b[0])/2,(a[1]+b[1])/2)}
        used_labels.append(found)
        extent=(max(extent[0],found[0]+found[2]+20), max(extent[1],found[1]+found[3]+20))
    return {'nodes':boxes,'edges':routes,'labels':labels,'lanes':lane_boxes,'width':extent[0],'height':extent[1],'direction':'vertical' if vertical else 'horizontal'}
