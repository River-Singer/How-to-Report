"""Select a template and bind declared values; the normal engine computes geometry."""
import argparse,copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--template',required=True);p.add_argument('--values');p.add_argument('--output',required=True);p.add_argument('--palette',default='report-default');a=p.parse_args()
 catalog=json.loads((ROOT/'catalog.json').read_text(encoding='utf8'))
 selected=next((x for x in catalog['templates'] if x['id']==a.template),None)
 if selected is None:raise ValueError('unknown registered local template ID')
 author=json.loads((ROOT/selected['author']).read_text(encoding='utf8'))
 contract=json.loads((ROOT/selected['slots']).read_text(encoding='utf8'))
 values=json.loads(Path(a.values).read_text(encoding='utf8')) if a.values else {}
 if set(values)-{'text','charts','images'}:raise ValueError('only text/charts/images are allowed')
 for fid,value in values.get('text',{}).items():
  if fid not in author['facts'] or not isinstance(value,str):raise ValueError('unknown text slot or non-text value: '+fid)
  author['facts'][fid]['value']=value
 chart_ids={x['id'] for x in contract.get('chart_slots',[])};image_ids={x['id'] for x in contract.get('image_slots',[])}
 if set(values.get('charts',{}))-chart_ids:raise ValueError('unknown chart slot')
 if set(values.get('images',{}))-image_ids:raise ValueError('unknown image slot')
 def visit(n):
  if isinstance(n,dict):
   if n.get('id') in values.get('charts',{}):n['element']['data']=copy.deepcopy(values['charts'][n['id']])
   if n.get('id') in values.get('images',{}):
    original=n['id'];height=n['height'];image=values['images'][original]
    if not isinstance(image,str):raise ValueError('image slot expects a local asset path')
    n.clear();n.update({'id':original,'type':'leaf','height':height,'element':{'type':'image','path':image,'fit':'contain','alt':'User-supplied visual'}})
   for v in n.values():
    if isinstance(v,(dict,list)):visit(v)
  elif isinstance(n,list):
   for v in n:visit(v)
 visit(author['pages'])
 author['project_id']='instance-'+a.template;author['revision']=1;author['brief']['palette_id']=a.palette
 out=Path(a.output).resolve()
 if out.exists():raise FileExistsError('output already exists')
 out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(author,ensure_ascii=False,indent=2),encoding='utf8')
 print(out)
if __name__=='__main__':main()
