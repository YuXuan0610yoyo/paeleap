from pathlib import Path

from streamlit.testing.v1 import AppTest


ROOT = Path(__file__).resolve().parents[1]


def test_landing_opens_creator_and_keeps_language():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    assert not app.exception
    assert app.button(key='enter_studio').label == '开始创作'
    assert not app.selectbox
    app.radio(key='language').set_value('English').run()
    assert app.button(key='enter_studio').label == 'Start creating'
    app.button(key='enter_studio').click().run()
    assert not app.exception
    assert app.radio(key='language').value == 'English'
    assert app.radio(key='platform').value == 'xiaohongshu'
    app.button(key='generate_caption').click().run()
    assert app.session_state['result']['variants']


def test_creator_keeps_platform_choices_and_editable_caption():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    assert app.radio(key='platform').options == ['小红书', '抖音图文', '微博']
    app.button(key='generate_caption').click().run()
    app.text_area(key='draft_0_caption').set_value('修改后的正文').run()
    app.radio(key='workspace').set_value('image').run()
    app.button(key='workflow_next').click().run()
    assert app.text_area(key='draft_0_caption').value == '修改后的正文'


def test_return_home_and_resume_keeps_work_in_progress():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    app.radio(key='platform').set_value('weibo').run()
    app.selectbox(key='text_style').select('活泼').run()
    app.button(key='generate_caption').click().run()
    app.text_input(key='draft_0_title').set_value('我修改的标题').run()
    app.radio(key='workspace').set_value('image').run()
    app.selectbox(key='image_ratio').select('16:9').run()

    assert app.button(key='home_logo').label == '返回首页'
    app.button(key='home_logo').click().run()
    assert app.button(key='enter_studio').label == '开始创作'
    app.button(key='enter_studio').click().run()

    assert not app.exception
    assert app.radio(key='workspace').value == 'image'
    assert app.selectbox(key='image_ratio').value == '16:9'
    app.radio(key='workspace').set_value('text').run()
    assert app.radio(key='platform').value == 'weibo'
    assert app.selectbox(key='text_style').value == '活泼'
    assert app.text_input(key='draft_0_title').value == '我修改的标题'


def test_return_home_uses_selected_language():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.radio(key='language').set_value('English').run()
    app.button(key='enter_studio').click().run()
    assert app.button(key='home_logo').label == 'Return home'
    app.button(key='home_logo').click().run()
    assert app.button(key='enter_studio').label == 'Start creating'


def test_compact_creator_keeps_advanced_options_available():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    assert any(expander.label == '更多选项' for expander in app.expander)
    app.selectbox(key='text_style').select('活泼').run()
    app.selectbox(key='target_audience').select('亲子家庭').run()
    app.button(key='generate_caption').click().run()
    assert app.session_state['result']['text_plan']['text_style'] == '活泼'
    assert app.session_state['result']['text_plan']['audience'] == '亲子家庭'


def test_compact_hashtag_edit_survives_preview_navigation():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    app.button(key='generate_caption').click().run()
    app.text_input(key='draft_0_hashtags').set_value('#乌镇 #我的修改').run()
    app.radio(key='workspace').set_value('preview').run()
    assert app.text_area(key='draft_0_hashtags').value == '#乌镇 #我的修改'
    app.text_area(key='draft_0_hashtags').set_value('#再次修改').run()
    app.radio(key='workspace').set_value('text').run()
    assert app.text_input(key='draft_0_hashtags').value == '#再次修改'


def test_caption_versions_keep_edits_in_the_new_results_panel():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    assert app.text_input(key='empty_caption_title').disabled
    app.button(key='generate_caption').click().run()
    app.text_input(key='draft_0_title').set_value('我修改的标题').run()
    app.selectbox(key='caption_variant').select(1).run()
    assert app.text_input(key='draft_1_title').value != '我修改的标题'
    app.selectbox(key='caption_variant').select(0).run()
    assert app.text_input(key='draft_0_title').value == '我修改的标题'
    assert not app.exception


def test_reference_photo_follows_the_generated_destination():
    app = AppTest.from_file(str(ROOT / 'app.py')).run()
    app.button(key='enter_studio').click().run()
    app.button(key='generate_caption').click().run()
    references = next(panel for panel in app.get('popover') if panel.proto.popover.label == '素材参考')
    assert any('alt="乌镇西栅"' in item.value for item in references.markdown)
    app.selectbox(key='input_category').select('自然景观').run()
    # An existing draft and its photo remain together until regenerated.
    references = next(panel for panel in app.get('popover') if panel.proto.popover.label == '素材参考')
    assert any('alt="乌镇西栅"' in item.value for item in references.markdown)
    app.button(key='generate_caption').click().run()
    references = next(panel for panel in app.get('popover') if panel.proto.popover.label == '素材参考')
    assert any('alt="杭州西湖"' in item.value for item in references.markdown)
    assert not app.exception


def test_marquee_uses_local_attributed_images_and_respects_reduced_motion():
    from landing import render_marquee
    markup = render_marquee('中文')
    assert markup.count('class="landing-rail-group"') == 2
    assert 'aria-hidden="true"' in markup
    assert 'creativecommons.org/licenses/' in markup
    css = (ROOT / 'landing.css').read_text()
    assert 'prefers-reduced-motion: reduce' in css
    assert 'landing-scroll' in css
