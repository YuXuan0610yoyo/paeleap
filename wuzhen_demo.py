"""Prepared Wuzhen copy, bundled concept images, and platform post previews."""

from base64 import b64encode
from html import escape
from io import BytesIO
from pathlib import Path

import streamlit as st

from local_photo import IMAGE_SIZES, adapt_photo, decode_photo
from platform_profiles import PLATFORM_PROFILES, platform_label


WUZHEN = '乌镇西栅'
IMAGE_DIR = Path(__file__).parent / 'assets' / 'wuzhen-demo'
COVERS = (
    ('wuzhen-xiaohongshu-cover.png', 'day', 'Riverside walk', '沿河慢游',
     ('沿水', '沿河', '水边', '散步', '慢游', '街巷', '老街', '临水')),
    ('wuzhen-xiaohongshu-daylight.png', 'day', 'Stone bridge and boat', '石桥与摇橹船',
     ('石桥', '过桥', '摇橹船', '游船', '日景', '白天', '倒影', '水乡风景')),
    ('wuzhen-xiaohongshu-night.png', 'night', 'Canal after dark', '水巷夜景',
     ('夜景', '夜游', '亮灯', '灯火', '夜色', '暮色', '蓝调', '入夜')),
    ('wuzhen-xiaohongshu-dyehouse.png', 'dyehouse', 'Indigo dyehouse', '蓝印花布',
     ('蓝印花布', '染坊', '晒布', '纹样', '印染', '花布', '非遗')),
)
NOTE_HEADINGS = {'F02': '🛶 水乡风景', 'F03': '🧵 草木本色染坊', 'F04': '💌 乌镇老邮局'}
NOTE_DETAILS = {
    'F02': '过桥时回头看，临水木屋和倒影刚好同框。',
    'F03': '先看晒布场的蓝白长布，再走近看上面的花纹。',
    'F04': '在老邮局门前停一停，看看门窗的细节，想想以前的信怎么送到水乡人家。',
}

# Each audience has its own story. Assemble only the paragraphs for selected highlights.
AUDIENCE_COPY = {
    '一般游客': (
        '乌镇西栅｜慢慢看{lead}',
        '想在乌镇慢慢走，可以先给西栅留一段沿水散步的时间。',
        '走累了就放慢一点，给自己留些看细节的时间。',
        '#古镇慢游',
        {
            'F02': '沿着水边走一走，看看石桥、临水的屋檐和倒影。进街巷前回头多看一眼，水面和老房子连在一起，最有江南水乡的味道。',
            'F03': '到草木本色染坊，留意晒布场的蓝印花布。先看一整匹布的蓝白配色，再凑近看纹样，远看和近看各有意思。',
            'F04': '走到乌镇老邮局，可以看看外墙和门窗的细节，顺便把这座老建筑和水乡的邮政文化联系起来。',
        },
    ),
    '亲子家庭': (
        '带孩子逛乌镇西栅｜从{lead}开始',
        '带孩子逛西栅，可以玩一轮「找一找」，每到一处找一个以前没留意过的细节。',
        '回家后让孩子挑一个最喜欢的细节画下来，就有一张自己的西栅旅行卡。',
        '#亲子出游',
        {
            'F02': '先在水边找一座桥。问问孩子，水里倒映的是桥、屋檐还是树？换个角度再看一次，看看倒影有什么变化。',
            'F03': '到了草木本色染坊，在蓝印花布上找一组重复的纹样。让孩子用几个词形容它，再看看旁边的布有没有同样的图案。',
            'F04': '在乌镇老邮局找一处有特色的门窗，再和孩子聊聊以前一封信是怎么从一个地方到另一个地方的。',
        },
    ),
    '学生／研学团体': (
        '乌镇西栅观察笔记｜从{lead}入手',
        '在乌镇西栅做一页观察笔记，把看到的细节、自己的判断和还想查证的问题分开记。',
        '最后交换笔记，挑一条大家都能用现场细节解释的发现。',
        '#研学观察',
        {
            'F02': '画一张水边的速写，标出河道、石桥和临水建筑的位置。再用一句话解释，这几样东西怎样连成一处街景。',
            'F03': '在草木本色染坊选一组蓝印花布纹样，记录颜色、形状和重复方式。把有关制作工艺的问题留在旁边，回去找资料核对。',
            'F04': '在乌镇老邮局记下两个建筑细节，再写一个关于水乡邮政的问题。把现场观察和后续查证分别写在两栏。',
        },
    ),
}


def prepare_caption(brief, draft):
    """Use the prepared audience copy for the default Wuzhen walkthrough."""
    audience = AUDIENCE_COPY.get(brief['audience'])
    platform = brief['platform']
    style = brief['text_style']
    allowed_styles = ('简洁', '活泼') if platform == 'xiaohongshu' else ('简洁',)
    if (not audience or brief['attraction'] != WUZHEN or
            brief['purpose'] != '种草推荐' or style not in allowed_styles):
        return draft
    title_format, opening, ending, tag, details = audience
    highlights = brief['highlights']
    highlight_text = [details.get(h['id'], h['text']) for h in highlights]
    title = title_format.format(lead=highlights[0]['label'])
    extra = [brief['supplement']] if brief['supplement'] else []
    if platform == 'xiaohongshu':
        if style == '活泼' and brief['audience'] == '一般游客':
            if len(highlights) == 3:
                title = '乌镇西栅｜慢慢逛这三处'
            opening = '第一次去西栅，可以先沿河走一段，再拐进老街。'
            ending = ''
            highlight_text = [NOTE_DETAILS.get(h['id'], paragraph)
                              for h, paragraph in zip(highlights, highlight_text)]
        parts = [opening] + [
            f"{NOTE_HEADINGS.get(h['id'], '📍 ' + h['label'])}\n{paragraph}"
            for h, paragraph in zip(highlights, highlight_text)
        ] + extra + [ending]
    elif platform == 'douyin':
        parts = [opening] + [
            f'{number:02d}｜{h["label"]}\n{paragraph.split("。", 1)[0]}。'
            for number, (h, paragraph) in enumerate(zip(highlights, highlight_text), 1)
        ] + extra + [ending]
    else:
        parts = [opening, *highlight_text, *extra, ending]
    separator = '\n' if platform == 'weibo' else '\n\n'
    tags = list(dict.fromkeys([f'#{WUZHEN}', tag, *(f'#{h["label"]}' for h in highlights)]))
    variant = {**draft['versions'][0], 'title': title, 'caption': separator.join(filter(None, parts))}
    return {**draft, 'versions': [variant], 'suggested_titles': [title], 'hashtags': tags}


def _current_draft(result):
    variants = result['variants']
    index = min(st.session_state.get('form_caption_variant', 0), len(variants) - 1)
    draft = variants[index]
    prefix = f'form_draft_{index}_'
    title = st.session_state.get(prefix + 'title', draft['title'])
    caption = st.session_state.get(prefix + 'caption', draft['caption'])
    hashtags = st.session_state.get(prefix + 'hashtags', ' '.join(draft['hashtags']))
    return index, title, caption, hashtags


def _caption_html(caption):
    paragraphs = []
    for paragraph in caption.split('\n\n'):
        if not paragraph.strip():
            continue
        first, separator, rest = paragraph.partition('\n')
        if separator and first.startswith(('🛶 ', '🧵 ', '💌 ', '📍 ')):
            first = f'<strong>{escape(first)}</strong>'
            content = first + '<br>' + escape(rest).replace('\n', '<br>')
        else:
            content = escape(paragraph).replace('\n', '<br>')
        paragraphs.append(f'<p>{content}</p>')
    return ''.join(paragraphs)


def render_caption_result(result, field, label, lang, go_to):
    brief = result['text_plan']
    saved_platform = brief['platform']
    st.markdown('### ' + label('Caption results', '文案结果'))
    platform = st.segmented_control(
        label('Preview platform', '预览平台'), list(PLATFORM_PROFILES),
        default=saved_platform, required=True,
        format_func=lambda value: platform_label(value, lang),
        key='wuzhen_caption_platform', label_visibility='collapsed', width='stretch',
    )
    index, title, caption, hashtags = _current_draft(result)
    if platform != saved_platform:
        from template_engine import generate_drafts
        preview_brief = {**brief, 'platform': platform}
        preview = prepare_caption(preview_brief, generate_drafts(preview_brief, mode='offline'))
        title = preview['versions'][0]['title']
        caption = preview['versions'][0]['caption']
        hashtags = ' '.join(preview['hashtags'])

    with st.container(key='wuzhen_caption_preview', height='stretch'):
        masthead = escape(brief['attraction'] + label(' · Travel notes', ' · 文旅笔记'))
        st.markdown(
            f'<article class="wuzhen-caption wuzhen-caption--{platform}">'
            f'<header><span aria-hidden="true">P</span>{masthead}</header>'
            f'<h4>{escape(title)}</h4>{_caption_html(caption)}'
            f'<div class="wuzhen-caption__tags">{escape(hashtags)}</div></article>',
            unsafe_allow_html=True,
        )
    if platform != saved_platform:
        st.caption(label('Selected publishing platform: ', '配图将使用已选平台 ') +
                   platform_label(saved_platform, lang))

    with st.container(key='wuzhen_caption_actions'):
        edit, _, next_step = st.columns([1, 1.3, 1.4], wrap=False)
        with edit:
            edit_label = label('Edit caption', '编辑文案')
            if platform == saved_platform:
                with st.popover(edit_label, width='stretch'):
                    field(st.text_input, f'draft_{index}_title', title, label=label('Title', '标题'))
                    field(st.text_area, f'draft_{index}_caption', caption, label=label('Caption', '正文'),
                          height=220)
                    field(st.text_input, f'draft_{index}_hashtags', hashtags,
                          label=label('Hashtags', '话题标签'))
            else:
                st.button(edit_label, disabled=True, width='stretch')
        with next_step:
            st.button(label('Next: Image', '下一步：配图'), key='caption_to_image',
                      on_click=go_to, args=('image',), type='primary', width='stretch')


def _fitted_visual(result):
    image = result.get('image')
    if image is None:
        return None
    ratio = PLATFORM_PROFILES[result['text_plan']['platform']]['recommendations']['default_ratio']
    width, height = IMAGE_SIZES[ratio]
    if image.width * height == image.height * width:
        return image
    return adapt_photo(image, ratio, 'crop')


def _suggest_covers(result):
    _, title, caption, _ = _current_draft(result)
    highlights = result['text_plan']['highlights']
    lead = title + ' ' + highlights[0]['label']
    copy = ' '.join([caption, *(highlight['label'] for highlight in highlights)])

    def relevance(cover):
        terms = cover[4]
        return 3 * sum(term in lead for term in terms) + sum(term in copy for term in terms)

    available = [cover for cover in COVERS if (IMAGE_DIR / cover[0]).is_file()]
    ranked = sorted(available, key=relevance, reverse=True)
    # Show the strongest cover for each distinct subject before using a second angle.
    by_subject = {}
    for cover in ranked:
        by_subject.setdefault(cover[1], cover)
    suggestions = list(by_subject.values())
    suggestions.extend(cover for cover in ranked if cover not in by_subject.values())
    return suggestions[:3]


def render_image_workspace(result, label, lang):
    brief = result['text_plan']
    platform = brief['platform']
    ratio = PLATFORM_PROFILES[platform]['recommendations']['default_ratio']
    st.markdown('### ' + label('Choose a cover', '选择配图'))
    covers = _suggest_covers(result)
    if not covers:
        st.warning(label('The demo covers could not be loaded.', '暂时无法载入配图素材。'))
        return False

    image_plan = result.get('image_plan', {})
    selected = None
    if result.get('image') is not None and image_plan.get('ratio', '3:4') == ratio:
        selected = image_plan.get('asset')

    with st.container(key='wuzhen_image_cards'):
        columns = st.columns(len(covers), border=True)
    for column, (asset, _, en, zh, _) in zip(columns, covers):
        is_selected = selected == asset
        image_path = IMAGE_DIR / asset
        with column, st.container(horizontal_alignment='center'):
            with st.container(key='wuzhen_cover_selected' if is_selected else f'wuzhen_cover_{asset}',
                              width=340, horizontal_alignment='center'):
                st.image(image_path, width='stretch', output_format='PNG', caption=label(en, zh))
                if not st.button(label('Selected', '已选用') if is_selected else label('Use cover', '选用这张'),
                                 key=f'choose_{asset}', disabled=is_selected, width=200):
                    continue
            try:
                image = decode_photo(image_path.read_bytes())
            except (OSError, ValueError):
                st.error(label('Unable to load an image. Try again.', '暂时无法载入配图，请重试。'))
            else:
                # Include the whole cover when the platform preview needs a square.
                if ratio == '1:1':
                    image = adapt_photo(image, ratio, 'pad')
                result.update(
                    image=image, image_source='bundled_ai_concept',
                    image_plan={'attraction': WUZHEN, 'asset': asset, 'ratio': ratio},
                )
                st.rerun()
    return any(selected == cover[0] for cover in covers)


def render_post(result, label, lang):
    platform = result['text_plan']['platform']
    _, title, caption, hashtags = _current_draft(result)
    image = _fitted_visual(result)
    st.markdown('### ' + label('Post preview', '整体预览'))
    if image is None:
        st.info(label('Add an image in the Image workspace to complete the post.', '在「图片」中添加一张配图，完成图文帖子。'))

    platform_name = platform_label(platform, lang)
    metadata = (
        f'<header><span class="prepared-post__platform">{escape(platform_name)}</span>'
        f'<span>{escape(WUZHEN)}</span></header>'
    )
    title_html = f'<h4>{escape(title)}</h4>'
    caption_html = _caption_html(caption)
    tags_html = f'<div class="prepared-post__tags">{escape(hashtags)}</div>'
    visual = ''
    if image is not None:
        image_bytes = BytesIO()
        if platform == 'xiaohongshu':
            image.save(image_bytes, format='PNG')
            mime_type = 'image/png'
        else:
            image.save(image_bytes, format='JPEG', quality=89, optimize=True)
            mime_type = 'image/jpeg'
        encoded = b64encode(image_bytes.getvalue()).decode('ascii')
        credit = escape(label('AI concept image', 'AI 概念图'))
        overlay = title_html if platform == 'douyin' else ''
        visual = (
            f'<figure class="prepared-post__visual"><img src="data:{mime_type};base64,{encoded}" '
            f'alt="{escape(WUZHEN)} · {credit}">{overlay}<figcaption>{credit}</figcaption></figure>'
        )
    copy_title = '' if platform == 'douyin' and image is not None else title_html
    copy = f'<section class="prepared-post__copy">{copy_title}{caption_html}{tags_html}</section>'
    content = copy + visual if platform == 'weibo' else visual + copy
    st.markdown(
        f'<article class="prepared-post prepared-post--{platform}">{metadata}'
        f'<div class="prepared-post__body">{content}</div></article>',
        unsafe_allow_html=True,
    )
