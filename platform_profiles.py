"""Research-backed platform metadata and display labels.

Recommendations are product defaults, not upload validators. None means
unverified, never unlimited. API evidence must not constrain manual publishing.
Selection and identity are wired into the app; copy and size adaptation follow later.
See docs/week4_platform_requirements.md for sources, scope and gaps.
"""

REVIEWED_ON = "2026-11-03"
DEFAULT_PLATFORM = "xiaohongshu"
SOURCES = {
    "S1": {
        "url": "https://school.xiaohongshu.com/lesson/normal/af0fe7e97bb0433fac9da5d1df52b07f",
        "evidence": "official_search_excerpt_only",
        "scope": "merchant_course_recommendation",
    },
    "S2": {
        "url": "https://partner.open-douyin.com/docs/resource/zh-CN/dop/develop/openapi/video-management/douyin/create-image-text/create-image-text",
        "evidence": "official_page_read",
        "scope": "create_image_text_api_only",
    },
    "S3": {
        "url": "https://kefu.weibo.com/faqdetail?id=12483",
        "evidence": "official_page_read",
        "scope": "manual_image_post",
    },
}

PLATFORM_PROFILES = {
    "xiaohongshu": {
        "labels": {"zh": "小红书", "en": "Xiaohongshu"},
        "content_type": "image_text",
        "recommendations": {
            "copy_structure": ["景点与看点标题", "简短引入", "2–3个亮点", "已知实用信息"],
            "tone": "自然具体，不虚构亲身体验",
            "default_ratio": "3:4",
            "default_pixels": [1080, 1440],
            "alternative_ratios": ["1:1", "4:3"],
            "ratio_basis": "official_course_suggestion_search_excerpt",
            "ratio_source": "S1",
            "export_formats": ["jpg", "png"],
        },
        "verified_manual_constraints": [],
        "api_evidence": [],
        "unverified_manual_limits": ["title_length", "body_length", "image_count", "image_size", "image_formats"],
    },
    "douyin": {
        "labels": {"zh": "抖音图文", "en": "Douyin image posts"},
        "content_type": "image_text",
        "recommendations": {
            "copy_structure": ["首句核心看点", "逐页短句", "已知实用信息"],
            "tone": "简洁易读，不夸大",
            "default_ratio": "3:4",
            "default_pixels": [1080, 1440],
            "alternative_ratios": ["1:1", "9:16"],
            "ratio_basis": "project_default",
            "ratio_source": None,
            "export_formats": ["jpg", "png"],
        },
        "verified_manual_constraints": [],
        "api_evidence": [{
            "source": "S2", "scope": "create_image_text_api_only",
            "max_images": 30, "max_image_size_source_text": "单张图片最大支持20M",
            "max_image_bytes": None,
        }],
        "unverified_manual_limits": ["title_length", "body_length", "image_count", "image_size", "image_formats"],
    },
    "weibo": {
        "labels": {"zh": "微博", "en": "Weibo"},
        "content_type": "image_text",
        "recommendations": {
            "copy_structure": ["主要信息", "地点与亮点", "必要背景与相关话题"],
            "tone": "清楚直接",
            "default_ratio": "1:1",
            "default_pixels": [1080, 1080],
            "alternative_ratios": ["3:4", "4:3"],
            "ratio_basis": "project_default",
            "ratio_source": None,
            "export_formats": ["jpg", "png"],
        },
        "verified_manual_constraints": [{
            "source": "S3", "scope": "manual_image_post",
            "formats": ["gif", "jpg", "png"],
            "image_size_source_text": "单张图片大小要在20M以下",
            "max_image_bytes": None,
        }],
        "api_evidence": [],
        "unverified_manual_limits": ["title_length", "body_length", "image_count", "image_size_byte_definition"],
    },
}


def platform_label(platform=DEFAULT_PLATFORM, language="中文"):
    """Display a stable platform ID in the current interface language."""
    return PLATFORM_PROFILES[platform]['labels']['en' if language == 'English' else 'zh']
