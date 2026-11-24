"""Build the evidence-grounded Xiaohongshu display pack; no API calls."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
R=Path(__file__).resolve().parents[1]; OUT=R/'output/pdf'; OUT.mkdir(parents=True,exist_ok=True)
D=json.loads((R/'templates/xiaohongshu_library_v1.json').read_text()); T=D['templates']; POSTS=D['research_posts']
AUDIT=R.parent/'outputs/01a12e9f-8427-7e62-b8e2-38dc79936eca/visual-audit'
pdfmetrics.registerFont(TTFont('CN','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W,H=595.28,841.89; BG='#F8F6EF'; INK='#292D29'; MUTED='#686B64'; RUST='#A65331'; LINE='#DDD9CE'
def txt(c,s,x,y,w,size=11,color=INK):
 p=Paragraph(s,ParagraphStyle('body',fontName='CN',fontSize=size,leading=size*1.5,textColor=HexColor(color),wordWrap='CJK'))
 _,h=p.wrap(w,1000);p.drawOn(c,x,H-y-h);return y+h

def rect(c,x,y,w,h,color='#FFFFFF',stroke=LINE):
 c.setFillColor(HexColor(color));c.setStrokeColor(HexColor(stroke));c.roundRect(x,H-y-h,w,h,8,fill=1,stroke=1)

def page(c,title,sub,n,total=5):
 c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
 txt(c,'PAELEAP / 小红书模板库 V1.1',38,24,390,9,RUST)
 txt(c,'2026.10.29',470,24,90,9,MUTED)
 txt(c,title,38,61,520,24);txt(c,sub,38,103,520,10,MUTED)
 c.setStrokeColor(HexColor(LINE));c.line(38,47,557,47)
 txt(c,f'{n}/{total}',529,807,40,8,MUTED)

def photo(c,name,x,y,w,h):
 f=R/'assets/gallery/0.jpg' if name=='westlake' else R/'assets/template_examples'/f'{name}.jpg'
 im=ImageReader(str(f));iw,ih=im.getSize();sc=min(w/iw,h/ih);dw,dh=iw*sc,ih*sc
 c.drawImage(im,x+(w-dw)/2,H-y-(h-dh)/2-dh,dw,dh)

def cover(c,t,x,y,w,h):
 if t['photo']:
  photo(c,t['photo'],x,y,w,h)
 else:
  im=ImageReader(str(AUDIT/'P56-contact-1.jpg'));iw,ih=im.getSize();sc=min(w/341,h/450)
  left=x+(w-341*sc)/2;top=H-y-(h-450*sc)/2
  c.saveState();tile=c.beginPath();tile.rect(left,top-450*sc,341*sc,450*sc);c.clipPath(tile,stroke=0,fill=0)
  c.drawImage(im,left-8*sc,top+23*sc-ih*sc,iw*sc,ih*sc);c.restoreState()

def visual_flow(c,t,y):
 txt(c,'模板这样排：从素材到一篇笔记',38,y,519,12,RUST)
 y+=30
 for i,title in enumerate(['1 选一张主图','2 排好配图顺序','3 配上标题和正文']):
  x=38+i*177;rect(c,x,y,165,194);txt(c,title,x+10,y+9,145,10,RUST)
  if i==0:
   cover(c,t,x+10,y+36,145,135)
  elif i==1:
   if t['category']=='古镇':
    for j,name in enumerate(['canal','street','courtyard']):
     photo(c,name,x+9+j*49,y+44,45,68)
     txt(c,str(j+1),x+26+j*49,y+115,20,9,MUTED)
    txt(c,'水乡 → 街巷 → 庭院',x+10,y+147,145,9)
   else:
    cover(c,t,x+10,y+39,65,80)
    rect(c,x+82,y+39,72,80,'#F8F6EF')
    txt(c,'看点清单' if t['photo'] else '项目介绍',x+87,y+47,62,9,RUST)
    txt(c,'01 湖面\n02 岸线'.replace('\n','<br/>') if t['photo'] else '怎么玩？<br/>适合谁？',x+87,y+69,62,8)
    txt(c,'主图 → 看点页 → 实用提醒',x+10,y+145,145,9)
  else:
   txt(c,escape(t['title']),x+10,y+39,145,10)
   sample={'古镇':'喜欢建筑细节，可以留意沿河木屋、街巷与庭院。你更想先看哪一处？','自然风光':'喜欢看开阔水面，可以从湖面与岸线认识西湖。你旅行时会为风景停留吗？','主题乐园':'先从滑车体验画面认识这个项目。出发前确认开放与参与要求。你更喜欢哪类玩法？'}[t['category']]
   txt(c,sample,x+10,y+82,145,9,MUTED)
   tags={'古镇':'#乌镇西栅 #古镇旅行','自然风光':'#杭州西湖 #风景分享','主题乐园':'#千岛湖 #乐园体验'}[t['category']]
   txt(c,tags,x+10,y+168,145,8,RUST)
  if i<2:txt(c,'→',x+166,y+85,15,12,RUST)
 return y+210

def section(c,title,body,y,x=38,w=519):
 y=txt(c,title,x,y,w,12,RUST)+6
 return txt(c,body,x,y,w,10.5)+17

def refs(c,ids,y):
 for code in ids:
  p=next(p for p in POSTS if p['label']==code)
  y=txt(c,f'<link href="{escape(p["url"])}" color="{RUST}">{code} · {escape(p["shortTitle"])}</link>',38,y,519,9)+3
 return y

f=OUT/'Paeleap_小红书模板库V1_导师展示版_2026-10-29.pdf';c=canvas.Canvas(str(f),pagesize=(W,H));c.setTitle('Paeleap 小红书模板库 V1.1');c.setAuthor('Paeleap C1')
page(c,'不会运营，也能做一篇推广笔记','输入少一点；封面、图片顺序和文案组织由模板承担。',1)
for i,t in enumerate(T):
 x=38+i*177;rect(c,x,155,165,133)
 txt(c,t['category'],x+12,170,141,17,t['color']);txt(c,'建议视觉：'+t['style'],x+12,203,141,10)
 txt(c,t['goal'],x+12,230,141,9)
y=section(c,'用户只回答三个问题','① 推广哪里？ ② 主要给谁看？ ③ 最想突出哪1–3个看点？<br/>然后选择对应照片。默认做种草推荐；需要攻略或活动宣传时，再补相应资料。',330)
y=section(c,'得到的是一篇笔记，而不只是一张海报','2个标题备选＋按现有照片数量安排的配图＋分段正文＋相关话题。主重点放在首图和首段；每张图片对应同一个正文看点。',y)
y=section(c,'模板如何替用户做决定','只有1张照片 → 做单图笔记，不重复照片凑页数。<br/>选择3个看点 → 标题、正文与配图逐项对齐；缺图的看点留在正文。<br/>改选亲子 → 加观察互动建议；改选朋友 → 加共同选择看点的提问。<br/>缺路线 → 改成看点清单；缺活动日期和参与方式 → 提示补齐。<br/>价格、场次等未知信息不写进成品；内部提示放在编辑区。',y)
c.showPage()
for n,t in enumerate(T,2):
 page(c,t['category']+'｜'+t['style'],t['goal'],n)
 cover(c,t,38,149,180,210)
 y=section(c,'用户这样选',escape(t['choices']),151,240,317)
 y=section(c,'标题怎么写',escape(t['formula']),y,240,317)
 y=section(c,'套用后的例子',escape(t['title']),y,240,317)
 y=visual_flow(c,t,391)
 y=section(c,'正文跟着图片写',escape(t['body']),y+8)
 attribution={'古镇':'照片：Gerbil · <link href="https://commons.wikimedia.org/wiki/File:Wuzhen_Xizha_2009-11.jpg">Wuzhen Xizha 2009-11</link> · CC BY-SA 3.0；缩放排版。','自然风光':'照片：Bjoertvedt · <link href="https://commons.wikimedia.org/wiki/File:West_Lake_IMG_8756_hangzhou_panorama.jpg">West Lake panorama</link> · CC BY-SA 4.0；缩放排版。','主题乐园':'图片为参考笔记截图，仅作内部版式示例；正式推广时替换为可用素材。'}[t['category']]
 txt(c,attribution,38,764,519,8,MUTED)
 c.showPage()
page(c,'乌镇西栅｜一篇可理解的完整示例','输入：乌镇西栅＋首次来访＋水乡／街巷／庭院。示例不虚构亲身到访。',5)
for i,(name,title,caption) in enumerate([('canal','01 封面','水乡慢游，看这3处细节'),('street','02 街巷','沿着木门窗，看看街巷'),('courtyard','03 庭院','把目光留给院落细节')]):
 x=38+i*177;rect(c,x,148,165,177);photo(c,name,x+7,179,151,112)
 txt(c,title,x+10,157,145,11,RUST);txt(c,caption,x+10,298,145,8.5)
y=section(c,'标题','乌镇西栅｜水乡慢游，看这3处细节',351)
body='如果你喜欢慢慢逛、看看建筑细节，可以把乌镇西栅放进旅行清单。比起把景点名记满，不妨先从水面、街巷和庭院这三个角度认识它。<br/><br/>01 看水乡环境<br/>沿河木屋与水面，是认识西栅的一个角度。<br/><br/>02 看街巷细节<br/>木门窗、屋檐与石板路，藏着不同的纹理与线条。<br/><br/>03 看院落一角<br/>庭院里的树影与窗格，也值得留意。喜欢观察建筑细节的话，可以把这些小地方放进看点清单。<br/><br/>你逛古镇时，更喜欢看水乡风景，还是建筑细节？'
y=txt(c,body,38,y,519,10.5)+15
txt(c,'#乌镇西栅  #乌镇旅行  #江南水乡  #古镇慢游',38,y,519,10,RUST)
txt(c,'照片：Gerbil · Wuzhen Xizha 2009-11 / 10 / 08 · CC BY-SA 3.0；照片及排版示例按相同许可提供。历史照片，推广前确认现况。',38,745,519,8,MUTED);c.showPage()
lessons=[
'古镇：围绕一个文化主题串起看点；位置必须有资料。','自然：拼图说明来访理由，路线另页呈现。','自然：确有地图时，让路线承担决策任务。','古镇/自然：普通实景也有效，不强制大字封面。','乐园：动作画面说明怎么玩；不把好玩等同研学。','自然：季节作为主题；花期与促销要核实。','古镇：主题串点，图片与正文说同一件事。','通用：一页一个看点，短标注帮助识别。','通用：顺序/空间信息另页，不塞满封面。','通用：活动名称与有效日期单独组织。','通用：真人在场支撑服务体验，不伪造亲历。','自然：用空间层次显示环境，不泛夸“震撼”。','乐园：按区域/项目拆页，便于连续浏览。','通用：合集用相同字段，减少选择负担。','乐园：区分游乐与学习成果，不混淆承诺。','通用：把抽象目标变成可做的任务。','乐园：材料、动作和成品组成体验说明。','乐园：活动步骤可借鉴，旧护照和场次不沿用。','乐园：过程按动作编排，奖励不等于学习。','通用：结果要有可观察证据，不保证他人同样成长。']
c.save()
# Human-editable operating rules and copy, sourced from the same data.
md=['# 小红书模板库 V1.1\n','目标：让不懂运营的人，用少量选择得到完整推广笔记。\n','产品分类：古镇、自然风光、主题乐园。视觉建议：人文纪实、自然清新、活力体验。视觉建议不是已确认的研究分类。\n']
for t in T:
 md+=['## '+t['category']+' / '+t['style'],t['goal'],'用户输入：'+t['choices'],'封面：'+t['cover'],'标题：'+t['title'],'图片顺序：\n'+'\n'.join('- '+s for s in t['sequence']),'画面：'+t['visual'],'正文：'+t['body'],'依据：'+', '.join(t['refs'])]
md+=['## 20篇逐条映射']
md += [f'- [{p["label"]} {p["shortTitle"]}]({p["url"]})：{l}' for p,l in zip(POSTS,lessons)]
(R/'docs/xiaohongshu_template_library_v1.md').write_text('\n\n'.join(md)+'\n')
# Submission is small and honest about the implementation boundary.
f2=OUT/'Paeleap_第三周交付说明_2026-10-29.pdf';c=canvas.Canvas(str(f2),pagesize=(W,H));page(c,'第三周交付说明','小红书推广笔记模板库 V1.1 · 无API展示版',1,1)
y=148
for title,body in [('目标','让不懂运营的人，选择景点、人群和重点后，也能组织一篇自然、具体的小红书推广笔记。'),('本次修订','按Week 2记录恢复古镇／自然风光／主题乐园三类产品模板。每套补齐封面、图片顺序、标题公式、正文结构和样本依据；包含乌镇完整图文示例。'),('建议查看顺序','先看模板库第1页的使用方法，再看第2–4页怎么套用，最后看第5页乌镇笔记成品示例。'),('当前范围','导师已认可此前基本功能和页面布局。本次完成文档与离线展示模板，未改线上网页、未接API，未执行自动图片生成。网页中的旧画风名称仍需后续同步；本附件为本次修订依据。'),('下一步','将经审阅的模板规则接入现有离线工作区，让少量选择决定封面与图片顺序。正式推广前替换或确认可用素材与当前景点资料。')]:y=section(c,title,body,y)
txt(c,'已有原型：<link href="https://paeleap-week3-yuxuan.streamlit.app/" color="'+RUST+'">打开Streamlit</link>（本次附件尚未同步上线）',38,y,519,10)
c.showPage();c.save()
(OUT/'给导师的提交消息_2026-10-29.txt').write_text('老师好～我们把模板库进一步改成了适合小红书的图文笔记形式，按古镇、自然风光、主题乐园整理。每套都包含封面、图片顺序和文案结构，也放了乌镇的完整图文示例，让不懂运营的人也比较容易照着用。\n\n这版结合了之前20篇笔记的研究，重点展示如何选择素材、安排配图并形成完整笔记。目前先完成离线展示稿，还没有接API，也还没同步替换网页里的旧画风选项，想先给您看看这版内容组织是否更贴近实际使用～\n')
print(f);print(f2)
