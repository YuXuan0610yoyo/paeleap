"""Local-only photo validation and state. No generation or external requests."""
from io import BytesIO
from PIL import Image, ImageOps, UnidentifiedImageError
import streamlit as st

IMAGE_SIZES = {'3:4': (1080, 1440), '1:1': (1080, 1080), '16:9': (1440, 810)}


def adapt_photo(image, ratio, method):
    """Fit a copy of an uploaded photo to the same pixels used for preview and export."""
    size = IMAGE_SIZES[ratio]
    if method == 'crop':
        return ImageOps.fit(image.convert('RGB'), size, method=Image.Resampling.LANCZOS)
    if method == 'pad':
        return ImageOps.pad(image.convert('RGB'), size, method=Image.Resampling.LANCZOS, color='white')
    raise ValueError('Unknown image fitting method')


def decode_photo(data):
    if len(data) > 20 * 1024 * 1024:
        raise ValueError('Photo exceeds 20 MB')
    try:
        with Image.open(BytesIO(data)) as source:
            if source.width * source.height > 25_000_000:
                raise ValueError('Photo exceeds 25 megapixels')
            source.load()
            return ImageOps.exif_transpose(source).convert('RGB')
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError) as exc:
        raise ValueError('Invalid photo') from exc


def clear_photo_if_removed(widget_key):
    if not st.session_state.get(widget_key):
        for key in ('image', 'image_source', 'image_plan', 'photos'):
            st.session_state.get('result', {}).pop(key, None)
        st.session_state.pop('photo_digest', None)


def remove_photo():
    for key in ('image', 'image_source', 'image_plan', 'photos'):
        st.session_state.get('result', {}).pop(key, None)
    st.session_state.pop('photo_digest', None)
    st.session_state['photo_epoch'] = st.session_state.get('photo_epoch', 0) + 1
