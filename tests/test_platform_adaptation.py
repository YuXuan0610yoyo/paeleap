from PIL import Image
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile
import pytest
from streamlit.testing.v1 import AppTest
from template_engine import generate_drafts
from test_detailed_inputs import make_brief


def test_platform_copy_changes_structure_and_keeps_selected_facts():
    copies = {platform: generate_drafts(make_brief(platform=platform))
              for platform in ('xiaohongshu', 'douyin', 'weibo')}
    for key in ('title', 'caption'):
        assert len({result['versions'][0][key] for result in copies.values()}) == 3
    assert len({tuple(result['hashtags']) for result in copies.values()}) == 3
    for result in copies.values():
        for variant in result['versions']:
            assert '苏堤是西湖堤岸之一' in variant['caption']
            assert '白堤也是西湖堤岸之一' in variant['caption']
            assert variant['used_fact_ids'] == ['F01', 'F03', 'F04']


@pytest.mark.parametrize('original', [(300, 200), (200, 300), (200, 200)])
@pytest.mark.parametrize('method', ['crop', 'pad'])
@pytest.mark.parametrize('ratio,size', [('3:4', (1080, 1440)), ('1:1', (1080, 1080)), ('16:9', (1440, 810))])
def test_image_adaptation(original, method, ratio, size):
    from local_photo import adapt_photo
    image = Image.new('RGB', original, 'red')
    adapted = adapt_photo(image, ratio, method)
    assert adapted.size == size
    assert image.size == original
    if method == 'pad' and original[0] * size[1] != original[1] * size[0]:
        assert adapted.getpixel((0, 0)) == (255, 255, 255)


def test_platform_defaults_follow_saved_draft_and_survive_navigation():
    a = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    a.button(key='enter_studio').click().run()
    a.radio(key='platform').set_value('weibo').run()
    a.button(key='generate_caption').click().run()
    a.radio(key='workspace').set_value('image').run()
    assert a.selectbox(key='image_ratio').value == '1:1'
    a.selectbox(key='image_ratio').select('16:9').run()
    a.radio(key='image_fit').set_value('crop').run()
    a.button(key='workflow_next').click().run()
    a.button(key='workflow_back').click().run()
    assert a.selectbox(key='image_ratio').value == '16:9'
    assert a.radio(key='image_fit').value == 'crop'
    assert not a.exception


def test_photo_preview_and_downloads_use_the_same_fitting(monkeypatch):
    import streamlit as st
    downloads = {}
    previews = []
    original_download = st.download_button
    original_image = st.image

    def capture(label, data, *args, **kwargs):
        if args:
            downloads[args[0]] = data
        return original_download(label, data, *args, **kwargs)

    def capture_image(image, *args, **kwargs):
        if isinstance(image, Image.Image):
            previews.append(image.copy())
        return original_image(image, *args, **kwargs)

    monkeypatch.setattr(st, 'download_button', capture)
    monkeypatch.setattr(st, 'image', capture_image)
    a = AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'app.py')).run()
    a.button(key='enter_studio').click().run()
    a.radio(key='platform').set_value('weibo').run()
    a.button(key='generate_caption').click().run()
    a.session_state['result']['photos'] = [
        dict(digest='a', fact_id='F02', name='wide.png', image=Image.new('RGB', (300, 200), 'red')),
        dict(digest='b', fact_id='F03', name='tall.png', image=Image.new('RGB', (200, 300), 'blue')),
    ]
    a.radio(key='workspace').set_value('image').run()
    assert any(image.size == (1080, 1080) for image in previews)
    a.button(key='workflow_next').click().run()
    assert not a.exception
    single = Image.open(BytesIO(downloads['paeleap_visual.png']))
    with ZipFile(BytesIO(downloads['paeleap_photos.zip'])) as bundle:
        first = Image.open(BytesIO(bundle.read('01.png')))
        second = Image.open(BytesIO(bundle.read('02.png')))
        assert first.size == second.size == single.size == (1080, 1080)
        assert first.tobytes() == single.tobytes()
