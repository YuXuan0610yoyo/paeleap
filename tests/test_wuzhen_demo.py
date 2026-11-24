import re
from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_wuzhen_recording_flow_keeps_one_image_and_uses_platform_layout():
    app = AppTest.from_file(str(ROOT / 'app.py'))
    app.query_params['demo'] = 'wuzhen'
    app.run()
    app.button(key='enter_studio').click().run()
    assert app.radio(key='platform').value is None
    assert app.selectbox(key='input_category').value is None
    assert app.selectbox(key='example').value is None
    assert app.selectbox(key='target_audience').value is None
    assert app.button(key='generate_caption').disabled

    app.radio(key='platform').set_value('xiaohongshu').run()
    app.selectbox(key='input_category').select('古镇／历史街区').run()
    app.selectbox(key='example').select('乌镇西栅').run()
    assert app.multiselect(key='focus_choices').value == []
    app.multiselect(key='focus_choices').set_value(['水乡风景', '蓝印花布']).run()

    for audience, caption_fragment in [
        ('一般游客', '慢慢走'),
        ('亲子家庭', '找一找'),
        ('学生／研学团体', '观察笔记'),
    ]:
        app.selectbox(key='target_audience').select(audience).run()
        app.button(key='generate_caption').click().run()
        caption = app.text_area(key='draft_0_caption').value
        assert caption_fragment in caption
        assert '老邮局' not in caption

    app.radio(key='workspace').set_value('image').run()
    app.button(key='generate_image').click().run()
    first = app.session_state['result']['image_plan']['asset']
    app.button(key='generate_image').click().run()
    selected = app.session_state['result']['image_plan']['asset']
    assert selected != first

    for platform in ('xiaohongshu', 'douyin', 'weibo'):
        if platform != 'xiaohongshu':
            app.radio(key='workspace').set_value('text').run()
            app.radio(key='platform').set_value(platform).run()
            app.button(key='generate_caption').click().run()
        caption = app.session_state['form_draft_0_caption']
        app.radio(key='workspace').set_value('preview').run()
        assert not app.exception
        post = next(item.value for item in app.markdown if item.value.startswith('<article class="prepared-post '))
        assert f'prepared-post--{platform}' in post
        assert caption.splitlines()[0] in post
        assert re.search(r'<img[^>]+src="data:image/jpeg;base64,', post)
        assert app.session_state['result']['image_plan']['asset'] == selected
