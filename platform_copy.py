"""Adapt the existing offline draft structure for the chosen platform."""
from copy import deepcopy

from platform_profiles import DEFAULT_PLATFORM


def adapt_platform_copy(brief, draft):
    platform = brief.get('platform', DEFAULT_PLATFORM)
    if platform == 'xiaohongshu':
        return draft

    result = deepcopy(draft)
    name = brief['attraction']
    lead = brief['highlights'][0]['label']
    for variant in result['versions']:
        paragraphs = variant['caption'].split('\n\n')
        if platform == 'douyin':
            variant['title'] = '看点速览｜' + variant['title']
            opening = f'{name}，先看{lead}。'
            variant['caption'] = '\n\n'.join([opening] + [
                f'{index + 1}｜{paragraph}' for index, paragraph in enumerate(paragraphs)
            ])
        else:
            variant['title'] = '目的地动态｜' + variant['title']
            variant['caption'] = f'{name} · {lead}。\n' + '\n'.join(paragraphs)
    result['suggested_titles'] = [v['title'] for v in result['versions']]
    result['hashtags'] = list(dict.fromkeys(result['hashtags'] + [
        '#图文分享' if platform == 'douyin' else '#文旅资讯'
    ]))
    return result
