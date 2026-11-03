"""Platform state across workspaces, old drafts and replacement confirmation."""
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest
from test_detailed_inputs import make_brief


def studio():
    return AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()


def go(a, workspace):
    a.radio(key='workspace').set_value(workspace).run()
    assert not a.exception


def test_brief_platform_default_and_validation():
    assert make_brief()['platform'] == 'xiaohongshu'
    assert make_brief(platform='weibo')['platform'] == 'weibo'
    with pytest.raises(ValueError, match='平台'):
        make_brief(platform='unknown')


@pytest.mark.parametrize('platform', ['xiaohongshu', 'douyin', 'weibo'])
def test_platform_survives_language_navigation_and_image_brief(platform):
    a = studio()
    assert a.selectbox[0].key == 'platform'
    a.selectbox(key='platform').select(platform).run()
    a.radio(key='language').set_value('中文').run()
    assert a.selectbox(key='platform').value == platform
    a.button(key='generate_caption').click().run()
    assert a.session_state['result']['text_plan']['platform'] == platform
    go(a, 'image')
    assert a.session_state['result']['visual_brief']['platform'] == platform
    go(a, 'preview')
    from platform_profiles import PLATFORM_PROFILES
    name = PLATFORM_PROFILES[platform]['labels']['zh']
    assert any(name + ' · 图文预览' in x.value for x in a.markdown)
    go(a, 'text')
    assert a.selectbox(key='platform').value == platform


def test_platform_change_preserves_edits_and_cancels_pending_generation():
    a = studio()
    a.button(key='generate_caption').click().run()
    go(a, 'preview')
    a.text_area(key='draft_0_caption').set_value('保留我的修改').run()
    go(a, 'text')
    a.selectbox(key='platform').select('weibo').run()
    a.button(key='generate_caption').click().run()
    assert a.session_state['pending_offline_brief']['platform'] == 'weibo'
    a.selectbox(key='platform').select('douyin').run()
    assert 'pending_offline_brief' not in a.session_state
    go(a, 'image')
    assert any('Platform changed' in x.value for x in a.warning)
    assert a.session_state['result']['visual_brief']['platform'] == 'xiaohongshu'
    go(a, 'preview')
    assert a.text_area(key='draft_0_caption').value == '保留我的修改'
    assert any('Xiaohongshu · POST PREVIEW' in x.value for x in a.markdown)
    go(a, 'text')
    a.button(key='generate_caption').click().run()
    a.button(key='replace_offline_edits').click().run()
    assert a.session_state['result']['text_plan']['platform'] == 'douyin'
    go(a, 'image')
    assert a.session_state['result']['visual_brief']['platform'] == 'douyin'
    assert not any('Platform changed' in x.value for x in a.warning)


def test_legacy_brief_defaults_without_false_stale_notice():
    a = studio()
    a.button(key='generate_caption').click().run()
    result = a.session_state['result']
    result['text_plan'].pop('platform', None)
    a.session_state['result'] = result
    a.run()
    assert not any('Inputs changed' in x.value for x in a.info)
    go(a, 'preview')
    assert any('Xiaohongshu · POST PREVIEW' in x.value for x in a.markdown)


def test_direct_regeneration_clears_old_platform_warning():
    a = studio()
    a.button(key='generate_caption').click().run()
    a.selectbox(key='platform').select('weibo').run()
    assert any('Platform changed' in x.value for x in a.warning)
    a.button(key='generate_caption').click().run()
    assert a.session_state['result']['text_plan']['platform'] == 'weibo'
    assert not any('Platform changed' in x.value for x in a.warning)
    assert not any('Inputs changed' in x.value for x in a.info)
