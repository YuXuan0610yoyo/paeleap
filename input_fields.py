"""Input fields only. No page configuration, columns, menu or output layout.

Integration contract: render_input_fields() -> serializable brief or None.
Generate with template_engine.generate_drafts(brief, mode='offline').
"""
import streamlit as st
from attraction_catalog import EXTRA_CASES, recommended_highlights
from template_engine import list_attractions
from promotional_brief import (CATEGORIES, CASE_CATEGORIES, CATEGORY_GUIDANCE, STYLES,
    PURPOSES, AUDIENCES, STAGES, DURATIONS, case_highlights, parse_highlights, build_detailed_brief)

from platform_profiles import PLATFORM_PROFILES, DEFAULT_PLATFORM, platform_label

CUSTOM = '其他场所（填写资料）'
CASES = {c['name']: c for c in [*list_attractions(), *EXTRA_CASES]}


def _change_category(start_blank=False):
    category = st.session_state['input_category']
    current = CASES.get(st.session_state.get('example'))
    if current and CASE_CATEGORIES[current['category']] == category:
        return
    if start_blank and not current:
        return
    default = next((name for name, case in CASES.items() if CASE_CATEGORIES[case['category']] == category), CUSTOM)
    st.session_state['example'] = None if start_blank else default
    _reset_place_details()


def _change_example():
    case = CASES.get(st.session_state['example'])
    if case:
        st.session_state['input_category'] = CASE_CATEGORIES[case['category']]
    _reset_place_details()


def _reset_place_details():
    st.session_state['place'] = ''
    st.session_state.pop('primary_focus', None)
    st.session_state['keywords'] = ''
    for key in ('custom_introduction', 'custom_highlights', 'event_name', 'event_date', 'event_location', 'event_participation'):
        st.session_state.pop(key, None)


def render_input_fields(language="中文", *, start_blank=False):
    from input_labels import LocalizedFields
    ui = LocalizedFields(language)
    blank_placeholder = {'placeholder': '请选择'} if start_blank else {}
    if not start_blank:
        st.session_state.setdefault('platform', DEFAULT_PLATFORM)
        st.session_state.setdefault('input_category', '古镇／历史街区')
        if 'example' not in st.session_state:
            _change_category()
    st.markdown('<div class="creator-section"><span>1</span><div>' +
                ('发布平台<small>选择发布平台，匹配对应的文案风格与图片比例。</small>' if language == '中文' else
                 'Publishing platform<small>Choose where to publish your caption and images.</small>') +
                '</div></div>', unsafe_allow_html=True)
    with st.container(key='platform_row'):
        label_column, choice_column = st.columns([.22, 1], gap='small', vertical_alignment='center')
        with label_column:
            st.markdown('<div class="platform-label">' +
                        ('发布平台' if language == '中文' else 'Platform') +
                        ' <span aria-hidden="true">*</span></div>', unsafe_allow_html=True)
        with choice_column:
            st.radio('发布平台' if language == '中文' else 'Publishing platform',
                     list(PLATFORM_PROFILES), key='platform', horizontal=True,
                     format_func=lambda value: platform_label(value, language), label_visibility='collapsed',
                     index=None if start_blank else 0, width='stretch')
    st.markdown('<div class="creator-section creator-section-details"><span>2</span><div>' +
                ('景点资料<small>选择景点和推广重点，生成贴合的文案</small>' if language == '中文' else
                 'Destination details<small>Choose a place and its highlights</small>') +
                '</div></div>', unsafe_allow_html=True)
    category = ui.selectbox('景区类型', CATEGORIES, key='input_category', index=None if start_blank else 0,
                            on_change=_change_category, args=(start_blank,), **blank_placeholder)
    with st.container(key='attraction_group', gap=None):
        example = ui.selectbox('景点', [*CASES, CUSTOM], key='example', on_change=_change_example,
                               index=None if start_blank else 0, placeholder='输入景点名称搜索')
    if example == CUSTOM:
        st.session_state.setdefault('place', '')
        name = ui.text_input('场所名称', key='place', max_chars=80, placeholder='填写景点或场所名称')
    else:
        name = example
    data = CASES.get(example)
    introduction = ''
    highlights = []
    input_error = None
    if data:
        highlights = data['highlights'] if 'highlights' in data else case_highlights(data)
    elif example == CUSTOM and category:
        ui.info('请填写场所简介和已确认的亮点，文案将以这些资料为依据。')
        introduction = ui.text_area('场所简介', key='custom_introduction', max_chars=600,
                                   placeholder='写清场所是什么、有哪些已确认的特色。')
        raw = ui.text_area('候选亮点：一行一个“名称｜具体说明”', key='custom_highlights',
                           placeholder='例如填写已确认的' + CATEGORY_GUIDANCE[category][0], max_chars=4300)
        try:
            highlights = parse_highlights(raw)
        except ValueError as exc:
            input_error = str(exc)
    choices = {h['label']: h for h in highlights}
    for topic in recommended_highlights(category):
        choices.setdefault(topic['label'], topic)
    options = list(choices)[:max(5, len(highlights))]
    signature = (category, example)
    previous_signature = st.session_state.get('input_case_signature')
    if previous_signature != signature:
        keep = previous_signature in ((None, None), (category, None))
        st.session_state['focus_choices'] = (
            st.session_state.get('focus_choices', []) if keep else
            ([] if start_blank else [h['label'] for h in highlights[:2]])
        )
        st.session_state.pop('primary_focus', None)
        st.session_state['input_case_signature'] = signature
    with st.container(key='highlights_group', gap=None):
        selected = ui.multiselect('推广重点', options, key='focus_choices', max_selections=3,
                                  accept_new_options=True, select_all=False, placeholder='选择或输入推广重点')
        st.markdown('<div class="field-help">' +
                    ('选 1–3 项，也可输入后按回车添加。' if language == '中文' else
                     'Choose 1–3 highlights, or type your own and press Enter.') + '</div>', unsafe_allow_html=True)
    with st.container(key='audience_group', gap=None):
        audience = ui.selectbox('目标人群', AUDIENCES[:3] if start_blank else AUDIENCES,
                                key='target_audience', index=None if start_blank else 0, **blank_placeholder)
    style = ui.selectbox('文本风格', STYLES, key='text_style', index=None if start_blank else 0,
                         help='简洁：短句直述；活泼：轻松口语；严肃：稳重说明。', **blank_placeholder)
    purpose = ui.selectbox('推文目的', PURPOSES, key='copy_purpose',
                           index=None if start_blank else 0, **blank_placeholder)
    if st.session_state.get('primary_focus') not in selected:
        st.session_state['primary_focus'] = selected[0] if selected else None
    with st.expander('更多选项' if language == '中文' else 'More options'):
        primary = ui.selectbox('最想突出的一个重点', selected, key='primary_focus', disabled=not selected,
                               help='这个重点会进入标题和开头，其余选择作为支持内容。')
        supplement = ui.text_area('补充事实（选填）', key='keywords', max_chars=600,
                                  help='会原样放入“补充信息”，请填真实信息，不要在此填写写作指令；语气与目的使用上面的选项。')
        stage = '不限定'
        if audience == '学生／研学团体':
            stage = ui.selectbox('学习阶段（选填）', STAGES, key='learning_stage')
        duration = '不限定'
        if purpose == '游玩攻略':
            duration = ui.selectbox('计划游玩时长（选填）', DURATIONS, key='visit_duration',
                                    help='用于建议取舍看点，不会据此编造路线或承诺游览耗时。')
    event = None
    if purpose == '活动宣传':
        ui.caption('活动文案需要以下四项信息；仅使用你填写的内容。')
        event = {key: ui.text_input(label, key='event_' + key, max_chars=300)
                 for key, label in [('name', '活动名称'), ('date', '活动日期／时间'),
                                    ('location', '活动地点'), ('participation', '参与方式')]}
    if input_error:
        ui.warning(input_error)
        return None
    if start_blank and not all((st.session_state['platform'], category, example, selected, audience, style, purpose)):
        return None
    if any(len(value) > 30 for value in selected):
        ui.warning('推广重点请控制在30字以内。')
        return None
    for value in selected:
        if value not in choices:
            choices[value] = {'id': 'topic:' + value, 'label': value,
                              'text': f'可以把「{value}」作为观察或咨询的方向，具体信息以景区资料为准。',
                              'source': '用户选择的推广方向', 'provenance': 'editorial_angle'}
    try:
        return build_detailed_brief(name=data['name'] if data else name, category=category,
            style=style, purpose=purpose, audience=audience, highlights=list(choices.values()),
            selected=selected, primary=primary, data=data, introduction=introduction,
            supplement=supplement, stage=stage, duration=duration, event=event,
            platform=st.session_state['platform'])
    except ValueError as exc:
        ui.warning(str(exc))
        return None
