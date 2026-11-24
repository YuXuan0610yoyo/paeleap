"""Offline destination entries and editorial angles for the creator form."""

# General suggestions are framed as writing angles. Only the place entries below
# attach specific, sourced details to an attraction.
CATEGORY_TOPICS = {
    '自然景观': (
        ('代表性地貌', 'Landforms and scenery', '看风景时，可以留意地形和植被怎样连在一起，先看整体，再挑一处细节。'),
        ('四季风景', 'Seasonal scenery', '想看花、秋色或水景，可以先查目的地当季的观赏信息。'),
        ('观景点位', 'Viewpoints', '先在地图上找合适的观景位置，到了现场试着把近景和远景放进同一个画面。'),
        ('徒步与步道', 'Walking trails', '想边走边看，可以先确认步道的入口和开放范围，再按自己的节奏安排。'),
        ('动植物观察', 'Wildlife and plants', '带着科普资料观察身边的动植物，记下一两个能辨认的特征。'),
    ),
    '博物馆': (
        ('代表展品', 'Signature exhibits', '不妨挑一件感兴趣的展品，从造型、用途和展签上的年代开始看。'),
        ('展览主题', 'Exhibition themes', '先看展览的主题介绍，再带着一个问题去看展品之间的联系。'),
        ('藏品故事', 'Collection stories', '除了看外形，也可以留意展签里提到的用途、来历或制作方法。'),
        ('互动体验', 'Interactive experiences', '想参加现场体验，可以先在馆方公告中确认当期项目和参与方式。'),
        ('参观导览', 'Visitor guide', '出发前先确认馆区和参观安排，再用馆方导览挑出最想看的内容。'),
    ),
    '研学基地': (
        ('学习主题', 'Learning theme', '出发前带上一个具体问题，到现场找能帮助回答它的线索。'),
        ('观察任务', 'Observation activity', '选两个可以比较的细节，用速写或关键词记下它们的相同点和差异。'),
        ('动手实践', 'Hands-on activity', '有动手环节时，可以把材料、步骤和遇到的问题记在同一页。'),
        ('适龄与分组', 'Age groups and teams', '报名或组团前，可以先核对适用的学习阶段和分组安排。'),
        ('学习成果', 'Learning outcomes', '结束时选一个发现，用笔记、作品或简短汇报说清依据。'),
    ),
    '古镇／历史街区': (
        ('历史建筑', 'Historic architecture', '逛街区时可以多看一眼门窗、砖瓦和院落布局，再对照现场说明了解建筑旧时的用途。'),
        ('街巷格局', 'Historic streets', '沿着可通行的街巷走一走，看看窄巷、建筑和公共空间怎样衔接。'),
        ('非遗工艺', 'Traditional crafts', '看传统工艺时，试着从一件作品的材料或纹样入手，再了解它的制作过程。'),
        ('地方风物', 'Local specialities', '器物、饮食和日常风俗都是认识地方生活的切入口，可以选一样仔细看看。'),
        ('漫步路线', 'Walking route', '先在景区地图上圈出想去的点位，再给停下来观察和拍照留些余地。'),
    ),
    '主题乐园': (
        ('特色项目', 'Signature attractions', '先挑一个最想体验的项目，出发前看看园方公布的开放情况和参与条件。'),
        ('主题演出', 'Themed shows', '对演出感兴趣的话，可以先看主题介绍，再根据园方公布的场次安排。'),
        ('沉浸场景', 'Immersive settings', '逛主题场景时，可以找找布景、服装和故事线之间的呼应。'),
        ('亲子体验', 'Family experiences', '可以和孩子一起选想尝试的项目，再核对适龄范围和身高要求。'),
        ('游玩动线', 'Visit sequence', '把固定时间的活动先标在园区地图上，其余看点再按位置和兴趣安排。'),
    ),
}


def recommended_highlights(category):
    return [
        {'id': 'topic:' + label, 'label': label, 'text': text,
         'source': '推广方向', 'provenance': 'editorial_angle'}
        for label, _, text in CATEGORY_TOPICS.get(category, ())
    ]


def _entry(name, category, source, introduction, highlights):
    details = [
        {'id': f'F{number:02}', 'label': label, 'text': text, 'source': source, 'provenance': 'case_sheet'}
        for number, (label, text) in enumerate(highlights, 2)
    ]
    return {
        'name': name, 'category': category,
        'facts': [{'id': 'F01', 'text': introduction, 'source': source}, *details],
        'highlights': details,
        'boundaries': ['不推断票价、营业时间、当前活动或现场服务安排。'],
        'reviewed_on': '2026-11-19',
    }


EXTRA_CASES = (
    _entry('乌镇东栅', '古镇', 'https://www.ewuzhen.com/strategy/detail/201903147783946',
           '乌镇东栅是乌镇的江南水乡历史街区。',
           (('茅盾故居', '茅盾故居是东栅的文化看点，可以从江南民居与作家生平两方面了解。'),
            ('江南百床馆', '江南百床馆可作为了解江南床榻与生活文化的切入点。'),
            ('宏源泰染坊', '宏源泰染坊是东栅的传统工艺看点。'))),
    _entry('乌镇乌村', '古镇',
           'https://www.ewuzhen.com/ticket/detail?goodsCode=PK-202004-4468&goodsId=239404869971841025',
           '乌村位于乌镇西栅北侧，靠近京杭大运河。',
           (('田园风景', '乌村保留江南乡村风貌，可关注田地、水系与村落的关系。'),
            ('农事体验', '乌村以江南农耕文化为主题，具体体验项目可向景区查询。'),
            ('运河村落', '村落与水系相连，可从运河文化了解聚落格局。'))),
    _entry('浙江省博物馆之江馆区', '博物馆', 'https://www.zjmuseum.com.cn/cn/',
           '之江馆区是浙江省博物馆的馆区之一。',
           (('浙江历史文化', '可围绕浙江历史文化主题，结合馆方公布的展览了解相关藏品。'),
            ('讲解与导览', '浙江省博物馆官网列有之江馆区的讲解预约咨询方式。'),
            ('参观安排', '馆方发布参观和团队预约说明，出发前可通过官网了解。'))),
)
