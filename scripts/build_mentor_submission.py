from pathlib import Path
from xml.sax.saxutils import escape
import json
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/pdf'
OUT.mkdir(parents=True,exist_ok=True)
LIB=json.loads((ROOT/'templates/visual_library_v1.json').read_text())
pdfmetrics.registerFont(TTFont('CN','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
W,H=595.28,841.89
INK=HexColor('#292D29'); MUTED=HexColor('#656B63'); RUST=HexColor('#A65331'); BG=HexColor('#F8F6EF'); LINE=HexColor('#DDD9CE'); GREEN=HexColor('#E5EBDF'); PAPER=HexColor('#EEE5D4')

def text(c,txt,x,y,w,size=11,leading=None,color=INK):
    p=Paragraph(txt,ParagraphStyle('p',fontName='CN',fontSize=size,leading=leading or size*1.55,textColor=color,wordWrap='CJK',alignment=TA_LEFT))
    _,h=p.wrap(w,1000);p.drawOn(c,x,H-y-h);return y+h

def box(c,x,y,w,h,fill=BG,stroke=LINE):
    c.setFillColor(fill);c.setStrokeColor(stroke);c.roundRect(x,H-y-h,w,h,9,fill=1,stroke=1)

def label(c,txt,x,y,w,size=10,color=MUTED):return text(c,escape(txt),x,y,w,size,color=color)

def base(c,title,sub,page,total):
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0)
    label(c,'PAELEAP  /  C1',42,28,300,10,RUST)
    label(c,'2026.10.29  ·  V1',410,28,150,9)
    text(c,title,42,67,515,25,33)
    text(c,sub,42,111,510,10.5,color=MUTED)
    c.setStrokeColor(LINE);c.line(42,49,W-42,49)
    label(c,'离线原型与设计方案 · 未接入 API',42,H-39,420,8)
    label(c,f'{page} / {total}',510,H-39,45,8)

def photo(c,name,x,y,w,h):
    from reportlab.lib.utils import ImageReader
    src=ImageReader(str(ROOT/'assets/template_examples'/f'{name}.jpg'))
    iw,ih=src.getSize(); scale=min(w/iw,h/ih)
    dw,dh=iw*scale,ih*scale
    c.drawImage(src,x+(w-dw)/2,H-y-(h-dh)/2-dh,dw,dh)

def wire(c,x,y,w,h,style):
    box(c,x,y,w,h,PAPER if style=='heritage' else HexColor('#FFFFFF'))
    if style=='natural':
        label(c,'乌镇西栅',x+12,y+12,w-24,16,INK)
        label(c,'沿水而行，看见日常',x+12,y+40,w-24,8.5)
        photo(c,'canal',x+8,y+59,w-16,h-91)
        label(c,'WUZHEN / 水乡实景',x+12,y+h-24,w-24,8)
    elif style=='heritage':
        c.setStrokeColor(HexColor('#9C967E'));c.setLineWidth(.6)
        c.rect(x+7,H-y-h+7,w-14,h-14,fill=0,stroke=1)
        label(c,'水乡 · 乌镇',x+17,y+19,w-34,19,INK)
        label(c,'临水木屋，枕河人家',x+17,y+52,w-34,8.5)
        photo(c,'canal',x+14,y+75,w-28,h-121)
        label(c,'西栅印象',x+17,y+h-38,w-55,10,INK)
        c.setFillColor(RUST);c.rect(x+w-37,H-y-h+23,15,15,fill=1,stroke=0)
        label(c,'游',x+w-34,y+h-37,13,9,HexColor('#FFFFFF'))
    else:
        label(c,'乌镇慢游手记',x+10,y+10,w-20,13,INK)
        photo(c,'canal',x+8,y+36,w-16,h*.34)
        label(c,'01 沿河风景',x+10,y+38+h*.34,w-20,8)
        cw=(w-24)/2; yy=y+h*.60
        photo(c,'street',x+8,yy,cw,h*.23)
        photo(c,'courtyard',x+16+cw,yy,cw,h*.23)
        label(c,'02 街巷',x+8,y+h*.86,cw,8)
        label(c,'03 庭院',x+16+cw,y+h*.86,cw,8)
    caption='纸感排版 · 未做水墨转绘' if style=='heritage' else '实拍照片排版 · 非 AI 生成'
    label(c,caption,x,y+h+8,w,8)

library=OUT/'Paeleap_三种视觉风格模板库V1_展示版_2026-10-29.pdf'
c=canvas.Canvas(str(library),pagesize=(W,H));c.setTitle('Paeleap 三种视觉风格模板库 V1 · 展示版');c.setAuthor('Paeleap C1 项目组')
base(c,'三种风格，一套简单流程','旅游景点视觉模板库 V1  /  乌镇照片案例版',1,5)
text(c,'用同一张乌镇照片，比较单图、纸感海报和多图拼贴的表达。',42,156,510,12)
for i,(sid,name,desc) in enumerate([('natural','自然照片','看清景点与环境'),('heritage','水墨海报','突出文化与主题'),('experience','旅行拼贴','展示整体与细节')]):
    x=42+i*175
    label(c,f'0{i+1}  {name}',x,202,160,13,INK)
    wire(c,x,237,160,195,sid)
    label(c,desc,x,465,160,10)
text(c,'用户只需做四个选择',42,520,510,16)
text(c,'风格 → 主要突出什么 → 画面感觉 → 图片尺寸',42,554,510,12,color=RUST)
text(c,'主体默认沿用文案重点；感觉可选“帮我搭配、清新明亮、温暖柔和、安静自然”；尺寸可选竖图、方图和横图。照片与补充想法均为选填。',42,589,510,11)
box(c,42,665,511,94)
text(c,'依据与当前范围',56,678,480,11,color=RUST)
text(c,'基于前期小红书 20 篇研究和导师提供的风格化示例，归纳为三套 V1 方向。原研究按风景区、文博、研学分类；本次风格是产品设计转化。本册以实拍照片展示排版效果，照片来源见第 5 页；实际图片生成尚未开放。',56,704,480,10)
c.showPage()

cards=[
 dict(id='natural',title='自然照片',sub='对应模板：自然实景感  /  让景点本身成为主角',use='自然景区、古镇街区、建筑与场馆空间；适合景点介绍、种草推荐。',look='单一主体清楚，环境有层次；自然低饱和，轻度调色。保留地标结构与材质，不增加不存在的设施。',auto='自动采用轻度处理；“帮我搭配”沿用模板或参考图光线。留出标题空间，避免文字遮住主体。',example='乌镇西栅 · 水乡风景',brief='沿着河岸看乌镇，木屋、船只与水面组成日常风景。此例保留实拍色彩，标题放在照片外，让建筑与水面保持完整。',reuse='换成杭州西湖时，将主体改为湖面山景，沿用自然色彩与环境层次。',refs=['P4','P12']),
 dict(id='heritage',title='水墨海报',sub='对应模板：人文故事海报  /  一个清晰的文化主题',use='历史街区、文化景点、文博场所；适合文化介绍和主题封面。',look='一个可识别的景区或文化主体，配淡水墨背景、米白纸感和细边框。装饰退后，主体细节保持清楚。',auto='选择此风格即采用水墨纸感和标题留白。可选加入用户提供的人物照片；当前只记录合成要求，不执行合成。',example='乌镇西栅 · 水乡风景',brief='临水木屋，枕河人家。此例用同一张实拍搭配米色纸感、细边框和印章式装饰，展示文化海报排版；照片尚未转成水墨画。',reuse='换成杭州西湖时，突出湖景主题，保留同样的主视觉与留白规则。',refs=['P7','P8','P10']),
 dict(id='experience',title='旅行拼贴',sub='对应模板：体验步骤拼贴  /  一张图看见多个层次',use='景点亮点汇总、研学观察与有资料支持的体验活动；适合展示多个看点。',look='三格统一组织：整体场景、重点细节、另一观察角度。统一色温、边距和纸片边缘，让主次容易理解。',auto='自动采用整齐剪贴质感。没有活动依据时展示景物观察角度；有真实活动资料时，才使用材料、动作与成果画面。',example='乌镇西栅 · 水乡风景',brief='从河边走进街巷，再看一眼庭院。三张西栅照片依次展示沿河场景、街道与庭院细节。这是多看点组合示例，不代表已核实的游览路线。',reuse='换成杭州西湖时，可按湖面全景、岸边细节、另一湖景角度组织。',refs=['P13','P16','P17'])
]
for n,card in enumerate(cards,2):
    base(c,card['title'],card['sub'],n,5)
    wire(c,42,167,186,248,card['id'])
    yy=166
    for heading,key in [('适用场景','use'),('画面要求','look'),('模板默认要求（未出图）','auto')]:
        yy=text(c,heading,254,yy,299,12,color=RUST)+7
        yy=text(c,escape(card[key]),254,yy,299,10.5)+17
    y=max(yy+4,460)
    box(c,42,y,511,140)
    label(c,'乌镇照片案例 · 示例配文',56,y+12,480,10,RUST)
    label(c,card['example'],56,y+37,480,13,INK)
    text(c,card['brief'],56,y+69,480,10.5)
    y+=155
    text(c,'复用方式：'+card['reuse'],42,y,511,10.5)
    y+=48
    refs={r['label']:r for st in LIB['styles'] for r in st['references']}
    text(c,'研究依据（点击可查看原笔记）',42,y,511,10,color=RUST);y+=23
    for code in card['refs']:
        r=refs[code]
        text(c,f'<link href="{escape(r["url"])}" color="#656B63">{code} · {escape(r["shortTitle"])}</link>',42,y,511,9);y+=17
    if card['id']=='heritage':
        text(c,'文化主题来自研究；水墨纸感与可选人物参考来自导师示例。',42,y+3,511,9,color=MUTED)
    c.showPage()
base(c,'照片素材与参考','素材来源透明，区分实拍、版式设计与生成能力',5,5)
for i,(name,num,desc) in enumerate([('canal','11','沿河木屋与船只'),('street','10','西栅北部街道'),('courtyard','08','西栅庭院')]):
    yy=165+i*117
    photo(c,name,42,yy,140,99)
    text(c,desc,202,yy+5,350,13,color=RUST)
    text(c,f'Gerbil · Wuzhen Xizha 2009-{num}.jpg<br/>2009 年拍摄，作为版式素材，不代表景区现况。',202,yy+31,350,10)
    text(c,f'<link href="https://commons.wikimedia.org/wiki/File:Wuzhen_Xizha_2009-{num}.jpg" color="#A65331">查看原图与来源</link>',202,yy+75,350,10)
text(c,'照片与本册照片排版示例：<link href="https://creativecommons.org/licenses/by-sa/3.0/" color="#A65331">CC BY-SA 3.0</link>。照片等比例缩放，叠加的是独立文字、边框与底色；未做 AI 转绘或人物合成。',42,532,511,10)
text(c,'补充小红书参考',42,600,511,13,color=RUST)
text(c,'<link href="https://www.rednote.com/discovery/item/69d838e0000000002301e9ab" color="#A65331">CC不起早 · 乌镇西栅一日游，选的初九，男票手机拍照片</link>',42,628,511,10)
text(c,'2026-10-29 浏览封面：前景人物、中景水面、远景沿河建筑形成清楚层次。本册借鉴景物层次的思路，未复制该作者照片；三种模板仍依据前期研究与导师示例整理。',42,658,511,10)
text(c,'阅读提示：自然照片看环境；水墨海报页看纸感与标题组织（水墨转绘待实现）；旅行拼贴看多个看点如何放在一起。',42,724,511,10,color=MUTED)
c.showPage()
c.save()

submission=OUT/'Paeleap_第三周交付说明_2026-10-29.pdf'
c=canvas.Canvas(str(submission),pagesize=(W,H));c.setTitle('Paeleap C1 第三周交付说明');c.setAuthor('Paeleap C1 项目组')
base(c,'第三周交付说明','提交内容：文生图工作区交互原型 + 三种视觉风格模板库 V1',1,1)
y=158
for title,body in [
 ('已收到的反馈','导师于 10 月 28 日认可原型基本功能，并确认当前页面布局可以保留。本次继续完善模板库展示与交付材料。'),
 ('本次交付','① 在线交互原型：文案 → 配图 → 预览。\n② 三种视觉风格模板库 V1：自然照片、水墨海报、旅行拼贴，含适用场景、乌镇照片排版案例、画面要求、示例与研究依据。'),
 ('简单试用','生成文案后进入图片页，选择风格、主体、感觉和尺寸；可选上传照片，再到预览页查看文案与原图。示例：乌镇西栅 → 水乡风景 → 水墨海报。'),
 ('当前完成程度','已完成离线文案、配图选项与方案组织、原图预览及下载。10 月 27 日版本通过 65 项自动化测试。本次为文档整理；未接入 API，未执行图片生成、风格化或人物合成，尚未验证实际出图质量。'),
]:
    y=text(c,title,42,y,511,13,color=RUST)+7
    y=text(c,escape(body).replace('\n','<br/>'),42,y,511,10.5)+19
text(c,'原型链接',42,y,511,13,color=RUST);y+=27
text(c,'<link href="https://paeleap-week3-yuxuan.streamlit.app/" color="#A65331">https://paeleap-week3-yuxuan.streamlit.app/</link>',42,y,511,10.5);y+=42
box(c,42,y,511,105)
text(c,'后续可请导师确认（不影响本次提交）',56,y+12,480,11,color=RUST)
text(c,'1. 三种风格是否覆盖日常推广需求？哪一种最值得优先完善？<br/>2. 下一步优先围绕哪类景点或哪个实际项目深化？<br/>3. 是否有可供参考的景区照片、品牌颜色或标题排版规范？',56,y+39,480,10)
c.showPage();c.save()

message='''老师好～根据您对基本功能和页面布局的反馈，我们整理好了本周的交互原型和三种视觉风格模板库 V1，发给您查看。

模板库包括自然照片、水墨海报和旅行拼贴，每套都整理了适用场景、画面要求、乌镇照片排版案例和示例配文，也结合了前期小红书研究及您提供的参考。

目前仍是离线版本，图片部分完成了选项和配图方案整理，暂未接入 API，照片案例采用已有实拍素材排版，不代表系统已能生成或风格化图片。

原型链接：https://paeleap-week3-yuxuan.streamlit.app/
附件：模板库 V1 展示版、第三周交付说明。

您有空时可以看看三种风格是否贴合日常推广需求，我们再根据建议完善～

【可选追问，不必一次全部发送】
1. 这三种风格里，您更希望我们优先完善哪一种？
2. 接下来有没有一个实际景点或推广项目，可以作为重点案例？
3. 如果有现成的景区照片或品牌排版要求，能否给我们参考？
'''
(OUT/'给导师的提交消息_2026-10-29.txt').write_text(message)
print(library);print(submission)
