"use strict";
(() => {
  const data = window.STORYBOOK_INDEX;
  window.STORYBOOK_CHUNKS = {};
  const $ = id => document.getElementById(id);
  const labels = {"native-page":"源页面", "native-group":"原生组合", "native-atom":"原子对象", icon:"独立图标", chart:"数据图表",template:"参数模板",component:"语义组件",recipe:"组合样式",palette:"全局色卡",primitive:"底层图元",profile:"文字规范"};
  const modes = {"source-anchor":"保留源几何","source-parameter":"源结构固定锚点",computed:"引擎计算",registered:"已注册",planned:"待实现"};
  const categories = {deviation:"偏差",correlation:"相关性",ranking:"排名",distribution:"分布","change-over-time":"时间变化",magnitude:"量级","part-to-whole":"整体与部分",spatial:"空间",flow:"流向"};
  let kind = "", page = 0, current = null, currentMode = "", currentPaletteDefault = null, activePalette = "", detailEpoch = 0;
  const selection = new Set(), loaded = new Map(), requests = new Map();
  const lookup = new Map(data.items.map(x=>[x.id,x]));
  const presentationRoles = new Set(data.items.map(x=>x.presentation_role?.toLocaleLowerCase()).filter(Boolean));
  const displayOrder = new Map(["component", "recipe", "chart", "palette", "profile", "template", "icon", "native-page", "native-group", "native-atom", "primitive"].map((kind, index)=>[kind,index]));
  const browseItems = data.items.map((record,index)=>({record,index})).sort((a,b)=>(displayOrder.get(a.record.kind)??100)-(displayOrder.get(b.record.kind)??100)||a.index-b.index).map(item=>item.record);
  const native = r=>r.kind.startsWith("native-");
  const append = (parent, tag, text, className) => {const e=document.createElement(tag); if(text!=null)e.textContent=text;if(className)e.className=className;parent.append(e);return e;};
  const badge = (parent,text,warn=false)=>append(parent,"span",text,"badge"+(warn?" warning":""));
  const palettePanel = append($("preview-scope").parentNode,"section",null,"palette-details");
  $("preview-scope").after(palettePanel);
  const profilePanel = append($("preview-scope").parentNode,"section",null,"profile-details");palettePanel.after(profilePanel);
  const previewPages = append($("detail-preview").parentNode,"div",null,"preview-pages");$("detail-preview").after(previewPages);
  const roleLabels = {primary:"主色",secondary:"辅色",tertiary:"第三色",accent:"强调",body:"正文",muted:"注释",surface:"背景",surfaceMuted:"浅背景",border:"边框",success:"成功",warning:"警示",danger:"风险",positive:"正向",negative:"负向",neutral:"中性"};
  function swatch(parent,color,label){
    const item=append(parent,"span",null,"swatch");const chip=append(item,"span",null,"swatch-chip");
    if(/^#[0-9a-f]{6}$/i.test(color))chip.style.backgroundColor=color;
    chip.setAttribute("aria-hidden","true");item.title=(label?label+" ":"")+color;if(label)append(item,"span",label);return item;
  }
  function renderPaletteDetails(record){
    palettePanel.replaceChildren();palettePanel.hidden=record.kind!=="palette";if(palettePanel.hidden)return;
    append(palettePanel,"h3","预览配色："+record.label);
    const choice=append(palettePanel,"p",null,"palette-choice");choice.id="palette-choice-status";
    const use=append(palettePanel,"button","应用此配色");use.onclick=()=>{$("palette").value=record.palette_id;changePalette();};
    append(palettePanel,"h3","色彩角色与对比度");
    append(palettePanel,"p","颜色名称是本项目的语义分工。对比度用于判断文字与底色是否可读；浅色注释不能承担关键结论。","muted");
    const table=append(palettePanel,"table",null,"palette-table"),head=append(table,"thead"),hr=append(head,"tr");
    for(const label of ["角色 / 色值","白底文字","色底正文"] )append(hr,"th",label);
    const body=append(table,"tbody");for(const [role,color] of Object.entries(record.roles||{})){
      const row=append(body,"tr"),cell=append(row,"td");swatch(cell,color,roleLabels[role]||role);append(cell,"code",color);
      const ratio=record.contrast?.[role];append(row,"td",ratio?ratio.on_white+":1":"—");append(row,"td",ratio?ratio.body_text+":1":"—");
    }
    for(const [key,label] of [["categorical","分类色"],["sequential","顺序色节点"],["diverging","发散色节点"]]){
      append(palettePanel,"h3",label);const row=append(palettePanel,"div",null,"swatches");for(const color of record[key]||[])swatch(row,color,color);
    }
    append(palettePanel,"h3","配色来源");
    append(palettePanel,"p",record.provenance?.sources?.length?"参考来源颜色后由项目分配PPT语义角色，不是来源网站的官方PPT主题。":"沿用项目现有报告配色。","muted");
    for(const url of record.provenance?.sources||[]){if(typeof url!=="string"||!/^https?:\/\//i.test(url))continue;const link=append(palettePanel,"a",url);link.href=url;link.target="_blank";link.rel="noopener noreferrer";}
  }
  function describeValue(value){return typeof value==="string"?value:JSON.stringify(value);}
  const informationLabels={declared_families:"已声明字体",effective_script_mapping:"实际中西文字体映射",fallback:"字体回退边界",embedding:"字体嵌入",weight_mapping:"字重映射",field:"工程绑定字段",value:"注册规范身份",scope:"适用范围",palette_field:"配色绑定字段",run_fields:"局部文字字段",supported:"已支持",unsupported:"尚未支持",paragraph_semantics:"段落与换行规则",validation:"校验方式"};
  function information(parent,value){
    if(Array.isArray(value)){const list=append(parent,"ul");for(const item of value)append(list,"li",describeValue(item));}
    else if(value&&typeof value==="object"){const list=append(parent,"dl");for(const [key,item] of Object.entries(value)){append(list,"dt",informationLabels[key]||key);const entry=append(list,"dd");if(Array.isArray(item))information(entry,item);else entry.textContent=describeValue(item);}}
    else if(value!=null)append(parent,"p",String(value));
  }
  function renderProfileDetails(record){
    profilePanel.replaceChildren();profilePanel.hidden=record.kind!=="profile";if(profilePanel.hidden)return;
    append(profilePanel,"h3","中西文字体与全局绑定");information(profilePanel,record.font_policy);information(profilePanel,record.global_binding);
    append(profilePanel,"h3","角色字号、颜色与字重");const wrap=append(profilePanel,"div",null,"table-scroll"),table=append(wrap,"table",null,"palette-table"),head=append(table,"thead"),hr=append(head,"tr");
    for(const label of ["角色","字号","字体 / 字重","默认颜色"])append(hr,"th",label);
    const body=append(table,"tbody");const number=v=>typeof v==="number"?Number(v.toFixed(2)):v;
    for(const [role,style] of Object.entries(record.roles||{})){const row=append(body,"tr");append(row,"td",role);append(row,"td",number(style.font_size_pt)+" pt / "+number(style.font_size_px)+" px");append(row,"td",style.font_family+" / "+style.weight);const color=append(row,"td");swatch(color,style.color_hex,style.color_role);append(color,"code",style.color_hex);}
    append(profilePanel,"h3","行距、段距与对齐");const spacingWrap=append(profilePanel,"div",null,"table-scroll"),spacing=append(spacingWrap,"table",null,"palette-table"),spacingHead=append(append(spacing,"thead"),"tr");
    for(const label of ["角色","行高 / 段间距","内边距pt（左上右下）","对齐"])append(spacingHead,"th",label);
    const rows=append(spacing,"tbody");for(const [role,style] of Object.entries(record.roles||{})){const row=append(rows,"tr");append(row,"td",role);append(row,"td",number(style.line_height_multiplier)+"倍 · "+number(style.line_height_pt)+"pt / "+number(style.paragraph_gap_pt)+"pt");append(row,"td",(style.insets_pt||[]).map(number).join(" / "));append(row,"td",style.align+" / "+style.vertical_anchor);}
    append(profilePanel,"h3","富文本实际支持");information(profilePanel,record.rich_text);
    append(profilePanel,"h3","可声明字段");information(profilePanel,record.supported_fields);
  }
  function selectedRequest(value,restore=false){return window.STORYBOOK_REQUESTS.applyPalette(value,currentMode,$("palette").value,currentPaletteDefault,restore);}
  function cacheRequest(){requests.set(current.id,{text:$("request").value,base:currentPaletteDefault,palette:$("palette").value});}
  function updatePaletteStatus(){
    const selected=(data.palettes||[]).find(p=>p.palette_id===$("palette").value);$("palette-swatches").replaceChildren();
    if(selected)for(const role of ["primary","secondary","tertiary","accent"])swatch($("palette-swatches"),selected.roles[role],roleLabels[role]);
    $("palette-status").textContent=(selected?"生成请求将使用「"+selected.label+"」。":"保留各请求原有配色。")+"原生保真资产保持源颜色；当前预览不会自动重算。";
    const choice=$("palette-choice-status");if(choice)choice.textContent="当前请求采用："+(selected?.label||current?.label||"原有配色")+"。应用本色卡将同步全局选项及生成请求。";
  }
  function changePalette(){
    const previous=activePalette;activePalette=$("palette").value;updatePaletteStatus();if(!currentMode)return;
    try{const request=JSON.parse($("request").value);if(!previous&&activePalette)currentPaletteDefault=currentMode==="chart"?request.palette_id:request.brief?.palette_id;$("request").value=JSON.stringify(selectedRequest(request,!activePalette&&!!previous),null,2);cacheRequest();$("request-status").textContent=currentMode==="native"?"原生保真请求保持源颜色，不添加配色参数。":"配色ID已同步到请求。运行引擎命令后才会生成新配色的结果。";}
    catch(error){$("request-status").textContent="配色已选择，当前JSON需修正后才能同步："+error.message;}
  }
  function preview(record){
    const div=document.createElement("div");div.className="preview";
    const p=record.preview;
    if(!p || !p.image){append(div,"span",record.executable?"查看输入规格与调用方式":"已收录 · 生成能力待实现","placeholder");return div;}
    if(p.crop_emu && p.slide_emu){
      const svg=document.createElementNS("http://www.w3.org/2000/svg","svg");svg.setAttribute("viewBox",p.crop_emu.join(" "));svg.setAttribute("role","img");svg.setAttribute("aria-label",record.label||record.id);
      const img=document.createElementNS(svg.namespaceURI,"image");img.setAttribute("href",p.image);img.setAttribute("width",p.slide_emu[0]);img.setAttribute("height",p.slide_emu[1]);img.setAttribute("preserveAspectRatio","none");svg.append(img);div.append(svg);
    }else{const img=append(div,"img");img.src=p.image;img.alt=record.label||record.id;img.loading="lazy";}
    return div;
  }
  async function detail(record){
    if(!loaded.has(record.chunk))loaded.set(record.chunk,new Promise((resolve,reject)=>{const s=document.createElement("script");s.src="data/"+record.chunk+".js";s.onload=()=>resolve(window.STORYBOOK_CHUNKS[record.chunk]);s.onerror=()=>reject(new Error("详情文件无法读取，请保留完整Storybook目录"));document.head.append(s);}));
    return (await loaded.get(record.chunk)).find(x=>x.id===record.id);
  }
  function matches(r){
    const query=$("search").value.trim().toLocaleLowerCase(),q=query.split(/\s+/).filter(Boolean);
    const text=[r.id,r.label,r.purpose,r.source_name,r.presentation_role,r.selection_guidance,...(r.categories||[]),...(r.relations||[])].join(" ").toLocaleLowerCase();
    const queryMatch=presentationRoles.has(query)?r.presentation_role?.toLocaleLowerCase()===query:q.every(t=>text.includes(t));
    return (!kind||r.kind===kind) && (!$("source").value||r.source_id===$("source").value) && (!$("category").value||(r.categories||r.relations||[]).includes($("category").value)) && (!$("executable").checked||r.executable===true) && ($("hidden").checked||(!r.hidden&&!r.conditional&&r.visible_default!==false)) && queryMatch;
  }
  function updateSelection(){ $("selection-count").textContent=`已选 ${selection.size} 个原生资产`;$("download-selection").disabled=!selection.size;$("clear-selection").disabled=!selection.size; }
  function render(){
    const filtered=browseItems.filter(matches),pages=Math.max(1,Math.ceil(filtered.length/data.page_size));page=Math.min(page,pages-1);
    $("heading").textContent=kind?(labels[kind]||kind):"所有组件";$("results").textContent=`找到 ${filtered.length.toLocaleString()} 项 · 每页 ${data.page_size} 项 · 预览与实际可变范围分别说明`;
    $("cards").replaceChildren();
    for(const r of filtered.slice(page*data.page_size,(page+1)*data.page_size)){
      const card=append($("cards"),"article",null,"card");card.append(preview(r));const body=append(card,"div",null,"card-content");
      const badges=append(body,"div",null,"badges");badge(badges,labels[r.kind]||r.kind);badge(badges,modes[r.mode]||r.mode||"查看合同",!r.executable);
      append(body,"h2",r.label||r.id);append(body,"p",r.purpose||r.id);if(native(r))append(body,"p",`${r.source_id} · 第 ${r.slide_number} 页 · 源区域预览`);
      const actions=append(body,"div",null,"card-actions");const button=append(actions,"button","查看详情");button.onclick=()=>show(r);
      if(native(r)&&r.executable){const label=append(actions,"label");const c=append(label,"input");c.type="checkbox";c.checked=selection.has(r.id);label.append(" 选取");c.onchange=()=>{c.checked?selection.add(r.id):selection.delete(r.id);updateSelection();};}
    }
    if(!filtered.length)append($("cards"),"div","没有符合条件的组件。可调整类型、来源或查看待实现条目。","empty");
    $("page-info").textContent=`${page+1} / ${pages}`;$("previous").disabled=page===0;$("next").disabled=page+1===pages;updateSelection();
  }
  function quote(text){return '"'+String(text).replace(/"/g,'\\"')+'"';}
  function command(mode){
    const cli=`python ${quote(data.cli)}`;
    if(mode==="native")return `${cli} catalog-build --catalog ${quote(data.catalog||"CATALOG")} --request request.json --pptx result.pptx`;
    if(mode==="chart")return `${cli} chart-build --request request.json --output chart-project --pptx chart.pptx`;
    if(mode==="author")return `${cli} build --input request.json --output ppt-project --geometry-policy computed --pptx report.pptx`+(current?.invocation?.asset_root?` --assets ${quote(current.invocation.asset_root)}`:"");
    if(mode==="recipe")return `${cli} compose --input request.json --output author.json\n${cli} build --input author.json --output ppt-project --geometry-policy computed --pptx report.pptx`;
    return `${cli} library ${quote(current.id)}`;
  }
  function setRequest(value,mode,note){currentMode=mode;currentPaletteDefault=mode==="chart"?value?.palette_id:value?.brief?.palette_id;$("request").value=JSON.stringify(selectedRequest(value),null,2);$("request-note").textContent=note+(mode==="native"?" 全局配色不修改原生资产。":" 全局配色仅进入生成请求，静态预览保持当前已生成的颜色。");$("command").textContent=command(mode);$("download-request").disabled=!mode;$("copy-request").disabled=!mode;}
  async function show(summary){
    const epoch=++detailEpoch;$("request-status").textContent="";
    try{const r=await detail(summary);if(epoch!==detailEpoch)return;current=r;
      $("detail-title").textContent=r.label||r.name||r.id;$("detail-kind").textContent=labels[r.kind]||r.kind;$("detail-id").textContent=r.id;
      $("detail-preview").replaceChildren(preview(r));$("preview-scope").textContent=(r.preview_scope||"无预览记录")+(r.style_scope?"。样式："+r.style_scope:"");$("detail-purpose").textContent=r.purpose||(r.use_cases||[]).join("；")||r.text_excerpt||"查看参数规格与使用边界";
      renderPaletteDetails(r);
      renderProfileDetails(r);previewPages.replaceChildren();for(const [i,p] of (r.preview_pages||[]).entries()){const button=append(previewPages,"button",p.title||"图样 "+(i+1),"quiet");button.onclick=()=>{$("detail-preview").replaceChildren(preview({...r,preview:p}));};}
      $("detail-badges").replaceChildren();badge($("detail-badges"),r.executable?"有调用入口":"待实现",!r.executable);badge($("detail-badges"),modes[r.mode]||r.mode||"注册合同");
      $("limitations").replaceChildren();let limits=r.limitations||[];if(typeof limits==="string")limits=[limits];if(r.avoid)limits=limits.concat(r.avoid);if(native(r))limits=limits.concat(["原稿样式保留；文字修改仅限当前资产声明的范围，长文本与新增节点须另走受支持组件。"]);for(const l of limits)append($("limitations"),"li",typeof l==="string"?l:JSON.stringify(l));
      $("relations").replaceChildren();for(const id of [r.parent_id,...(r.children||[])].filter(Boolean).slice(0,80)){if(lookup.has(id)){const b=append($("relations"),"button",id===r.parent_id?"查看父级":lookup.get(id).label||id,"quiet");b.onclick=()=>show(lookup.get(id));}}
      $("contract").textContent=JSON.stringify(r,null,2);
      if(native(r)&&r.executable){const texts={};for(const slot of r.capabilities?.text_slots||[])texts[slot.id]=slot.text;const request={asset_ids:[r.id],texts:{}};if(Object.keys(texts).length)request.texts[r.id]=texts;setRequest(request,"native","编辑已声明的文本槽位后下载请求。多资产通过页面上的选取框加入组合，位置由engine计算。");}
      else if(r.kind==="chart"&&r.executable)setRequest(r.example,"chart","可修改示例中的数据及允许选项。下载并运行命令后，由engine重新计算图形与布局；当前图片是示例预览。");
      else if(r.invocation)setRequest(r.invocation.request,r.invocation.mode,"可编辑示例内容、事实与受支持的约束；布局和几何由engine计算。按下方命令生成，当前图片为已生成的示例。");
      else setRequest(r.usage||r.example||r.contract||{},"",r.kind==="primitive"?"底层图元仅供引擎实现与受约束容器使用，不作为AI手填坐标的新稿入口。":"查看合同并通过支持该组件的计算布局或组合样式调用。");
      if(requests.has(r.id)&&currentMode){const cached=requests.get(r.id);currentPaletteDefault=cached.base;$("request").value=JSON.stringify(selectedRequest(JSON.parse(cached.text),!$("palette").value&&!!cached.palette),null,2);}
      updatePaletteStatus();
      if(!$("detail").open)$("detail").showModal();
    }catch(error){$("results").textContent=error.message;}
  }
  function download(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value,null,2)+"\n"],{type:"application/json;charset=utf-8"}));const a=document.createElement("a");a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  $("download-request").onclick=()=>{try{const value=selectedRequest(JSON.parse($("request").value));$("request").value=JSON.stringify(value,null,2);download(value,"request.json");cacheRequest();$("request-status").textContent="请求已下载。请用下方命令交给engine生成。";}catch(e){$("request-status").textContent="参数JSON无效："+e.message;}};
  $("copy-request").onclick=async()=>{try{$("request").value=JSON.stringify(selectedRequest(JSON.parse($("request").value)),null,2);if(navigator.clipboard){await navigator.clipboard.writeText($("request").value);}else{$("request").select();if(!document.execCommand("copy"))throw new Error("请手动复制已选中的文本");}$("request-status").textContent="已复制参数请求";}catch(e){$("request-status").textContent=e.message;$("request").select();}};
  $("download-selection").onclick=()=>{const value={asset_ids:[...selection]};if($("columns").value)value.columns=Number($("columns").value);download(value,"native-selection.json");$("results").textContent=command("native").replace("request.json","native-selection.json");};
  $("clear-selection").onclick=()=>{selection.clear();render();};$("close-detail").onclick=()=>$("detail").close();
  $("previous").onclick=()=>{page--;render();};$("next").onclick=()=>{page++;render();};
  let timer;$("search").oninput=()=>{clearTimeout(timer);timer=setTimeout(()=>{page=0;render();},120);};for(const id of ["source","category","executable","hidden"])$(id).onchange=()=>{page=0;render();};
  const navEntries=[["","全部组件"],...Object.entries(labels).filter(([k])=>data.items.some(r=>r.kind===k))];
  for(const [k,label] of navEntries){const b=append($("kinds"),"button",null,k===""?"active":"");append(b,"span",label);append(b,"span",(k?data.items.filter(r=>r.kind===k).length:data.items.length).toLocaleString(),"count");b.onclick=()=>{kind=k;page=0;for(const sibling of $("kinds").children)sibling.classList.toggle("active",sibling===b);render();};}
  const sources=[...new Set(data.items.map(r=>r.source_id).filter(Boolean))];for(const s of sources){const opt=append($("source"),"option",s);opt.value=s;}
  for(const [key,label] of Object.entries(categories)){const opt=append($("category"),"option",label);opt.value=key;}
  for(const palette of data.palettes||[]){const opt=append($("palette"),"option",palette.label);opt.value=palette.palette_id;}
  $("palette").disabled=!(data.palettes||[]).length;$("palette").onchange=changePalette;updatePaletteStatus();
  if(data.text_profile&&lookup.has(data.text_profile.id)){$("text-profile-summary").textContent=`report-14pt · 正文 ${data.text_profile.body_pt}pt · computed生成文字最低 ${data.text_profile.minimum_pt}pt`;
    $("show-text-profile").disabled=false;$("show-text-profile").onclick=()=>show(lookup.get(data.text_profile.id));}
  document.title=data.title;$("inventory-note").textContent=`${data.items.length.toLocaleString()} 项 · ${sources.length} 个源库 · 离线可浏览`;render();
})();
