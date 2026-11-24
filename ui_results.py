"""Read-only workspace results and editable Preview, sharing durable draft keys."""
from html import escape
from io import BytesIO
from zipfile import ZipFile
from xiaohongshu_templates import ordered_photos
import streamlit as st
from platform_profiles import DEFAULT_PLATFORM, PLATFORM_PROFILES, platform_label
from local_photo import adapt_photo
from image_brief import context_fingerprint
from image_workspace import selected_caption, STYLE_LABELS


def render_results(workspace, field, label, t, lang):
    result = st.session_state.get('result', {})
    variants = result.get('variants', [])
    if workspace == 'text':
        st.markdown('### ' + label('Caption results', '文案结果'))
        title_label = label('Title', '标题')
        body_label = label('Caption', '正文')
        tags_label = label('Hashtags', '话题标签')
        if variants:
            index = min(st.session_state.get('form_caption_variant', 0), len(variants) - 1)
            draft = variants[index]
            field(st.text_input, f'draft_{index}_title', draft['title'],
                  label=title_label, label_visibility='collapsed')
            field(st.text_area, f'draft_{index}_caption', draft['caption'],
                  label=body_label, label_visibility='collapsed', height='stretch')
            field(st.text_input, f'draft_{index}_hashtags', ' '.join(draft['hashtags']),
                  label=tags_label, label_visibility='collapsed')
        else:
            st.text_input(title_label, key='empty_caption_title', disabled=True, label_visibility='collapsed',
                          placeholder=label('Your title appears here after generation', '生成后在此显示标题'))
            st.text_area(body_label, key='empty_caption_body', disabled=True,
                         label_visibility='collapsed', height='stretch',
                         placeholder=label('Fill in the form, then select Generate Caption.',
                                           '填写左侧资料后，点击「生成文案」。'))
            st.text_input(tags_label, key='empty_caption_tags', disabled=True, label_visibility='collapsed',
                          placeholder=label('Hashtags appear here', '生成后在此显示话题标签'))
        return

    image = result.get('image')
    photos = ordered_photos(result.get('text_plan',{}),result.get('photos',[]))
    text_plan = result.get('text_plan', result.get('plan', {}))
    saved_platform = text_plan.get('platform', DEFAULT_PLATFORM)
    settings = result.get('image_settings', {})
    if settings.get('platform') != saved_platform:
        settings = {'ratio': PLATFORM_PROFILES[saved_platform]['recommendations']['default_ratio'], 'fit': 'pad'}
    if variants:
        st.caption(label('Draft platform: ', '草稿平台：') + platform_label(saved_platform, lang))
    image_plan = result.get('image_plan', result.get('plan', {}))
    if workspace == 'image':
        st.markdown('### ' + label('Image results', '图片结果'))
    else:
        st.markdown('### ' + label('Final Preview', '整体预览'))

    if workspace == 'preview' and variants:
        index = field(st.selectbox, 'caption_variant', 0,
                      label=label('Preferred variation', '首选文案版本'), options=list(range(len(variants))),
                      format_func=lambda i: label(f'Caption {i + 1}', f'文案 {i + 1}'))
    with st.container(key='preview_stage' if workspace == 'preview' else 'workspace_results'):
        if workspace == 'preview' and (variants or image is not None):
            st.markdown('<div class="preview-label">' + escape(platform_label(saved_platform, lang)) + label(' · POST PREVIEW', ' · 图文预览') + '</div>', unsafe_allow_html=True)
            attraction = text_plan.get('attraction') or image_plan.get('attraction', '')
            st.markdown('<div class="post-masthead"><span class="avatar">p.</span><div>' +
                        label('PAELEAP Travel Notes', 'PAELEAP 旅行手记') + '<small>' +
                        escape(attraction) + '</small></div></div>', unsafe_allow_html=True)
        if workspace in ('image', 'preview'):
            if photos:
                options=list(range(len(photos)))
                if st.session_state.get('preview_photo',0) not in options: st.session_state['preview_photo']=0
                photo_index=st.selectbox(label('Photo order','配图顺序'),options,
                    format_func=lambda i: str(i+1)+' / '+str(len(photos))+' · '+photos[i]['name'],key='preview_photo')
                image=photos[photo_index]['image']
            if image is not None:
                if result.get('image_source') == 'local_upload':
                    image = adapt_photo(image, settings['ratio'], settings['fit'])
                st.image(image, caption=label('Uploaded photo', '本地上传配图') if result.get('image_source') == 'local_upload' else t['image'], width='stretch')
            else:
                st.caption(label('No photos added. Add photos in Image.', '尚未添加配图。可在「图片」中上传照片。'))
        if workspace == 'preview':
            if variants:
                source = variants[index]
                if result.get('copy_source') == 'local_template_not_llm' and lang != '中文':
                    st.caption('Draft language: Chinese')
                elif text_plan.get('language') != lang:
                    st.warning(label('This draft keeps its original language. Generate Caption to create an English draft.',
                                     '此草稿保留原语言。点击生成文案以创建中文草稿。'))
                title = field(st.text_input, f'draft_{index}_title', source['title'],
                              label=label('Title', '标题'))
                caption = field(st.text_area, f'draft_{index}_caption', source['caption'],
                                label=label('Caption', '正文'), height=280)
                hashtags = field(st.text_area, f'draft_{index}_hashtags', ' '.join(source['hashtags']),
                                 label=label('Hashtags', '话题标签'), height=85)
                st.download_button(t['download_copy'], title + '\n\n' + caption + '\n\n' + hashtags,
                                   f'{saved_platform}_caption_{index + 1}.txt', key=f'download_{index}', width='stretch')
            else:
                st.caption(label('Enter the destination details, then generate a caption.', '填写景点资料后生成文案。'))
        if workspace in ('image', 'preview') and image is not None:
            bio = BytesIO()
            image.save(bio, format='PNG')
            st.download_button(t['download_image'], bio.getvalue(), 'paeleap_visual.png', 'image/png', width='stretch')
            if len(photos)>1:
                bundle=BytesIO()
                with ZipFile(bundle,'w') as archive:
                    for number,p in enumerate(photos,1):
                        data=BytesIO();adapt_photo(p['image'], settings['ratio'], settings['fit']).save(data,format='PNG')
                        archive.writestr(f'{number:02d}.png',data.getvalue())
                st.download_button(label('Download ordered photos','按顺序下载全部配图'),bundle.getvalue(),'paeleap_photos.zip','application/zip',width='stretch')

        if workspace == 'image' and image is not None:
            with st.expander(t['prompt']):
                st.code(image_plan.get('image_prompt', ''), language='text')
        if workspace == 'preview' and (variants or image is not None):
            visual_brief = result.get('visual_brief')
            stale = bool(visual_brief and visual_brief['context_fingerprint'] != context_fingerprint(text_plan, selected_caption(st.session_state)))
            if visual_brief:
                st.caption(label('Image brief: ', '配图方案：') + STYLE_LABELS[visual_brief['style_id']][0 if lang=='中文' else 1] + ' · ' + visual_brief['selections']['ratio'])
                if stale:
                    st.warning(label('Caption changed. Return to Image to refresh the brief.', '文案已修改，请返回图片页更新配图方案。'))
