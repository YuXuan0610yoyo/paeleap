"""Welcome screen for the offline tourism studio."""
import base64
from functools import lru_cache
from html import escape
from pathlib import Path

import streamlit as st


ROOT = Path(__file__).resolve().parent
PHOTOS = (
    ('assets/template_examples/canal.jpg', '乌镇西栅水乡', 'Wuzhen canal', 'Gerbil',
     'https://commons.wikimedia.org/wiki/File:Wuzhen_Xizha_2009-11.jpg', 'by-sa/3.0'),
    ('assets/gallery/1.jpg', '西溪湿地', 'Xixi Wetland', 'Yoshi Canopus',
     'https://commons.wikimedia.org/wiki/File:Xixi_Wetland_Park,_Hangzhou,_China.jpg', 'by-sa/3.0'),
    ('assets/gallery/2.jpg', '雷峰塔', 'Leifeng Pagoda', 'xiquinhosilva',
     'https://commons.wikimedia.org/wiki/File:Leifeng_Pagoda_20191102.jpg', 'by/2.0'),
    ('assets/template_examples/street.jpg', '乌镇西栅街道', 'Wuzhen street', 'Gerbil',
     'https://commons.wikimedia.org/wiki/File:Wuzhen_Xizha_2009-10.jpg', 'by-sa/3.0'),
    ('assets/gallery/0.jpg', '杭州西湖', 'West Lake', 'Bjoertvedt',
     'https://commons.wikimedia.org/wiki/File:West_Lake_IMG_8756_hangzhou_panorama.jpg', 'by-sa/4.0'),
)


@lru_cache(maxsize=16)
def asset_data(path):
    file = ROOT / path
    if not file.exists():
        return ''
    mime = {'.webp': 'image/webp', '.svg': 'image/svg+xml'}.get(file.suffix, 'image/jpeg')
    return f'data:{mime};base64,' + base64.b64encode(file.read_bytes()).decode('ascii')


def render_marquee(lang):
    cards = []
    styles = []
    credits = []
    for index, (path, zh, en, author, source, license_id) in enumerate(PHOTOS):
        image = asset_data(path)
        if not image:
            continue
        name = zh if lang == '中文' else en
        styles.append(f'.landing-photo-{index}{{background-image:url("{image}")}}')
        cards.append(f'<div class="landing-photo landing-photo-{index}" role="img" aria-label="{escape(name)}"></div>')
        credits.append(f'<a href="{escape(source, quote=True)}" target="_blank" rel="noopener noreferrer">'
                       f'{escape(name)} · {escape(author)}</a> '
                       f'<a href="https://creativecommons.org/licenses/{license_id}/" target="_blank" rel="noopener noreferrer">CC {license_id.upper()}</a>')
    group = ''.join(cards)
    label = '旅行灵感图片' if lang == '中文' else 'Travel inspiration photographs'
    credit_label = '图片来源' if lang == '中文' else 'Photo credits'
    return (f'<style>{"".join(styles)}</style><section class="landing-gallery" aria-label="{label}">'
            f'<div class="landing-rail"><div class="landing-rail-group">{group}</div>'
            f'<div class="landing-rail-group" aria-hidden="true">{group}</div></div></section>'
            f'<details class="landing-credits"><summary>{credit_label}</summary>'
            f'<p>{" · ".join(credits)}</p></details>')


def render_landing(change_language):
    st.markdown('<style>' + (ROOT / 'landing.css').read_text() + (ROOT / 'flow.css').read_text() + '</style>', unsafe_allow_html=True)
    st.session_state.setdefault('language', '中文')
    with st.container(key='landing_header'):
        logo_column, language_column = st.columns([3, 1], vertical_alignment='center')
        with logo_column:
            logo = asset_data('assets/paeleap-logo.webp')
            st.markdown(f'<img class="landing-logo" src="{logo}" alt="像素跃迁 PAELEAP">', unsafe_allow_html=True)
        with language_column:
            lang = st.radio('EN | 中文', ['English', '中文'],
                            format_func=lambda value: 'EN' if value == 'English' else '中文',
                            horizontal=True, key='language', label_visibility='collapsed',
                            on_change=change_language)
    cn = lang == '中文'
    title = '让每一处风景<br>被更多人看见' if cn else 'Help every place<br>find its audience'
    subtitle = ('选择平台，整理景点亮点，轻松创作旅游宣传文案' if cn else
                'Choose a platform, highlight your destination, and create a travel post')
    st.markdown(f'<div class="landing-intro"><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)
    with st.container(key='landing_action'):
        if st.button('开始创作' if cn else 'Start creating', key='enter_studio', type='primary', width='stretch'):
            st.session_state['show_studio'] = True
            st.rerun()
    st.markdown(render_marquee(lang), unsafe_allow_html=True)
