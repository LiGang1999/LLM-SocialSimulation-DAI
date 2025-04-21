"""数据源模块，负责从各种数据源获取用户配置信息。

此模块包含以下主要功能：
- 从本地文件获取职业数据
- 生成真实的地理位置信息
- 生成年龄信息
- 生成性别信息
"""

import json
import os
import random
import asyncio
from functools import lru_cache
from typing import Dict, List, Optional, Union
from geonamescache import GeonamesCache
from utils.llm import get_completion

_occupations_cache = None

@lru_cache(maxsize=1)
async def get_occupations() -> List[str]:
    """从本地文件获取职业数据。

    从预定义的JSON文件中读取职业列表。使用lru_cache装饰器避免重复读取文件。
    如果文件读取失败，将返回空列表。

    Returns:
        List[str]: 职业列表。如果获取失败则返回空列表
    """
    try:
        file_path = os.path.join(os.path.dirname(__file__), 'data', 'occupations.json')
        with open(file_path, 'r', encoding='utf-8') as f:
            occupations = json.load(f)
        return occupations
    except Exception as e:
        print(f"Error loading occupations data: {e}")
        return []

async def generate_age_info() -> Dict[str, Union[int, str]]:
    """生成年龄信息。

    首先在3-95岁范围内随机生成一个年龄，然后根据年龄确定对应的年龄组。
    年龄组包括：幼儿、儿童、青少年、青年、成年、中年、老年。

    Returns:
        Dict[str, Union[int, str]]: 包含以下字段的字典：
            - age: 具体年龄（整数）
            - age_group: 年龄组类别
    """
    # 首先随机生成年龄
    age = random.randint(7, 95)

    # 根据年龄确定年龄组
    if age <= 6:
        age_group = "幼儿"  # 幼儿
    elif age <= 12:
        age_group = "儿童"    # 儿童
    elif age <= 19:
        age_group = "青少年"  # 青少年
    elif age <= 29:
        age_group = "青年"  # 青年
    elif age <= 45:
        age_group = "成年"  # 成年
    elif age <= 65:
        age_group = "中年"  # 中年
    else:
        age_group = "老年"  # 老年

    return {
        "age": age,
        "age_group": age_group
    }

async def generate_career_info(age: int) -> Dict[str, str]:
    """生成职业相关信息。

    根据年龄决定职业生成方式：
    - 对18岁以下和65岁以上的人，职业状态将由GPT根据年龄生成
    - 其他年龄段的人，从本地职业数据库中随机选择职业

    Args:
        age: 年龄

    Returns:
        Dict[str, str]: 职业相关信息，包含职业状态
    """
    if age < 18 or age > 65:
        # 对18岁以下和65岁以上的人，职业状态由GPT生成
        prompt = f"为{age}岁的人生成一个合适的职业或状态。"
        if age < 18:
            prompt += "考虑到这些人可能正在上学或参与青少年活动，同时也要考虑他们可能对早期就业机会、实习或非传统教育路径的兴趣。"
        else:  # age > 65
            prompt += "考虑到他们可能已经退休，但仍可能以各种方式保持活跃。"

        status = await get_completion(sys_prompt="你是一个基于年龄生成真实职业状态的AI。只需回复状态，不需要解释。", user_prompt=prompt)
        if not status:
            return {"status": ""}
        return {"status": status}

    # 其他年龄段从职业数据库选择
    occupations = await get_occupations()
    if not occupations:
        return {"status": ""}

    career_status = random.choice(occupations)
    return {"status": career_status}

async def generate_location() -> Dict[str, str]:
    """生成真实的地理位置信息。

    使用 GeoNames 数据库随机选择一个国家和城市。

    Returns:
        Dict[str, str]: 包含以下字段的字典：
            - country: 国家名称
            - city: 城市名称
    """
    gc = GeonamesCache()

    # 获取所有国家
    countries = gc.get_countries()
    country_code = random.choice(list(countries.keys()))
    country = countries[country_code]

    # 获取选国家的所有城市
    cities = gc.get_cities()
    country_cities = [city for city in cities.values() if city['countrycode'] == country_code]

    if not country_cities:
        return {
            "country": country['name'],
            "city": "Unknown City"
        }

    # 随机选择一个城市
    city_data = random.choice(country_cities)

    return {
        "country": country['name'],
        "city": city_data['name']
    }

async def generate_gender() -> str:
    """随机生成性别（男/女）"""
    return random.choice(['男', '女'])

# def generate_values_background_alignment() -> Dict[str, bool]:
#     """随机生成核心价值观与背景是否一致的信息。

#     Returns:
#         Dict[str, bool]: 包含核心价值观与背景一致性的字典：
#             - is_aligned: 核心价值观是否与背景相符
#     """
#     return {
#         "is_aligned": random.choice([True, False])
#     }

# def generate_life_attitude() -> Dict[str, str]:
#     """随机生成生活状态。

#     Returns:
#         Dict[str, str]: 包含生活状态的字典：
#             - attitude: 生活状态（消极/积极/平庸）

async def generate_values_background_alignment() -> Dict[str, Union[int, str]]:
    """生成核心价值观与背景的一致性，采用更详细的方法。

    此函数返回一个1到5的分数，表示用户的核心价值观与其背景的一致程度。
    - 1: "完全不一致"
    - 2: "大部分不一致"
    - 3: "部分一致"
    - 4: "大部分一致"
    - 5: "完全一致"

    该函数还包括一个描述，提供对一致性的更全面的视图。

    Returns:
        Dict[str, Union[int, str]]: 包含以下内容的字典：
            - alignment_level: 表示一致性的整数分数（1-5）
            - alignment_description: 解释一致性级别的描述
    """
    alignment_level = random.choice([1, 2, 3, 4, 5])

    if alignment_level == 1:
        alignment_description = "核心价值观与背景完全不一致。"
    elif alignment_level == 2:
        alignment_description = "核心价值观与背景大部分不一致。"
    elif alignment_level == 3:
        alignment_description = "存在一些一致性，但也有相当大的差异。"
    elif alignment_level == 4:
        alignment_description = "核心价值观与背景大部分一致。"
    else:
        alignment_description = "核心价值观与背景完全一致。"

    return {
        "alignment_level": alignment_level,
        "alignment_description": alignment_description
    }

async def generate_life_attitude() -> Dict[str, Union[str, Dict, bool]]:
    """生成详细的生活态度，反映用户的总体观点。

    此函数随机生成生活态度，带有加权分布，偏向更负面的观点。
    它包含有关情绪倾向、应对机制和对变化的开放性的额外信息。

    Returns:
        Dict: 包含以下内容的字典：
            - attitude: 表示用户生活态度的字符串。
            - attitude_category: 态度的类别（积极、中性、消极）。
            - attitude_details: 有关这种态度如何表现的其他详细信息。
            - seeking_advice: 用户是否可能寻求外部建议或反馈。
            - coping_mechanism: 该人如何应对生活挑战。
    """
    # 按类别定义态度，带有加权概率
    positive_attitudes = [
        "乐观",
        "热情",
        "感恩",
        "坚韧"
    ]

    neutral_attitudes = [
        "现实",
        "坚忍",
        "好奇",
        "务实"
    ]

    negative_attitudes = [
        "悲观",
        "焦虑",
        "愤世嫉俗",
        "痛苦",
        "虚无主义",
        "冷漠",
        "宿命论",
        "厌世",
        "多疑",
        "沮丧"
    ]

    # 以加权概率选择类别（负面类别概率更高）
    category = random.choices(
        ["积极", "中性", "消极"],
        weights=[0.2, 0.3, 0.5],  # 50%的概率是消极态度
        k=1
    )[0]

    # 从选定类别中选择一种态度
    if category == "积极":
        attitude = random.choice(positive_attitudes)
    elif category == "中性":
        attitude = random.choice(neutral_attitudes)
    else:  # 消极
        attitude = random.choice(negative_attitudes)

    # 生成关于这种态度如何表现的详细信息
    attitude_details = {
        "乐观": "在挑战中看到机会，相信事情会得到解决。",
        "热情": "充满活力和兴奋地对待生活，渴望尝试新的经历。",
        "感恩": "经常实践感恩，重视自己所拥有的而非关注缺失的。",
        "坚韧": "已经克服了重大挑战并发展出强大的应对机制。",

        "现实": "基于事实而非情绪或希望性思维来评估情况。",
        "坚忍": "无论外部环境如何，都保持情绪平衡。",
        "好奇": "不断寻求新知识和新经验，对改变观点持开放态度。",
        "务实": "关注实用解决方案和具体成果，而非理想。",

        "悲观": "经常预期负面结果并为最坏情况做准备。",
        "焦虑": "对未来事件和潜在问题持续感到担忧。",
        "愤世嫉俗": "不信任他人的动机，对积极意图持怀疑态度。",
        "痛苦": "因过去的失望而怀怨恨，影响当前的看法。",
        "虚无主义": "认为生活没有内在意义或目的，导致留心无所托。",
        "冷漠": "对活动或人际关系几乎没有兴趣或情感投入。",
        "宿命论": "相信结果是注定的，减少了个人主观能动性。",
        "厌世": "普遍不喜欢或不信任人类，更喜欢独处。",
        "多疑": "没有足够证据就怀疑他人有恶意。",
        "沮丧": "持续感到绝望和失败。"
    }.get(attitude, "表现出影响日常观点的复杂情绪模式。")

    # Determine if they seek advice (less likely for certain negative attitudes)
    if attitude in ["Cynical", "Bitter", "Nihilistic", "Apathetic", "Misanthropic", "Paranoid"]:
        seeking_advice_probability = 0.2  # 20% chance for these attitudes
    elif attitude in ["Pessimistic", "Fatalistic", "Despondent"]:
        seeking_advice_probability = 0.3  # 30% chance for these attitudes
    elif attitude in ["Anxious"]:
        seeking_advice_probability = 0.7  # 70% chance for anxious people
    else:
        seeking_advice_probability = 0.5  # 50% chance for others

    seeking_advice = random.random() < seeking_advice_probability

    # Generate coping mechanisms based on attitude
    coping_mechanisms = {
        "积极": [
            "寻求社交支持",
            "使用积极的重新框架",
            "练习正念",
            "参与问题解决"
        ],
        "中性": [
            "客观分析情况",
            "保持情感距离",
            "适应情况",
            "专注于实际解决方案"
        ],
        "消极": [
            "避免处理问题",
            "使用逃避（例如，过度使用媒体）",
            "进行消极自言自语",
            "孤立于他人",
            "使用物质来应对",
            "归咎于他人的问题",
            "夸大小事的负面影响",
            "沉浸在过去的失败中"
        ]
    }

    coping_mechanism = random.choice(coping_mechanisms[category])

    # Generate emotional stability level
    emotional_stability_levels = {
        "积极": ["非常稳定", "稳定", "大部分稳定"],
        "中性": ["中度稳定", "变化的", "依赖于环境"],
        "消极": ["不稳定", "易波动", "高度敏感", "不可预测"]
    }
    emotional_stability = random.choice(emotional_stability_levels[category])
    
    # Generate risk tolerance level
    risk_tolerance_mapping = {
        "Optimistic": "High",
        "Enthusiastic": "Very high",
        "Grateful": "Moderate",
        "Resilient": "High",
        "Realistic": "Moderate",
        "Stoic": "Moderate to high",
        "Curious": "High",
        "Pragmatic": "Calculated",
        "Pessimistic": "Low",
        "Anxious": "Very low",
        "Cynical": "Selective",
        "Bitter": "Low",
        "Nihilistic": "Erratic",
        "Apathetic": "Indifferent",
        "Fatalistic": "Extreme or none",
        "Misanthropic": "Low for social risks",
        "Paranoid": "Very low",
        "Despondent": "Low"
    }
    risk_tolerance = risk_tolerance_mapping.get(attitude, "Moderate")
    
    # Generate adaptability to change
    change_adaptability_mapping = {
        "积极": ["拥抱变化", "快速适应", "将变化视为机会"],
        "中性": ["充分适应", "需要时间调整", "实用的变化方法"],
        "消极": ["抵制变化", "在过渡中挑战", "感到变化的威胁", "避免新情况"]
    }
    change_adaptability = random.choice(change_adaptability_mapping[category])
    
    # Generate social outlook
    social_outlook_options = {
        "积极": ["相信人性本善", "容易相信他人", "重视社区", "认为社会正在进步"],
        "中性": ["对社会有平衡的看法", "选择性信任", "重视证据而非意识形态", "务实的社会观点"],
        "消极": ["不信任机构", "看到社会衰退", "期待他人最坏的一面", "认为社会存在根本缺陷", "相信系统是被操控的"]
    }
    social_outlook = random.choice(social_outlook_options[category])
    
    # Generate future orientation
    future_orientation_mapping = {
        "乐观":"具有前瞻性和积极的期望",
        "热情":"对未来的可能性感到兴奋",
        "感恩":"关注当下，展望未来",
        "韧性":"为未来的挑战做好准备",
        "现实":"平衡未来前景",
        "斯多葛学派":"接受未来带来的一切",
        "好奇":"对未来发展感兴趣",
        "务实":"务实规划未来",
        "悲观":"预计未来会出现负面结果",
        "焦虑":"过分担心未来",
        "愤世嫉俗":"期待未来的失望",
        "苦涩":"深陷于过去的冤屈之中",
        "虚无主义":"看不到未来努力的意义",
        "冷漠":"对未来结果漠不关心",
        "宿命论":"相信未来是预先确定的",
        "厌世":"期待人类继续失败",
        "偏执狂":"担心未来的阴谋或威胁",
    }
    future_orientation = future_orientation_mapping.get(attitude, "Mixed feelings about the future")
    
    # Generate personal growth mindset
    growth_mindset_options = {
        "积极":["强烈的成长心态","相信自我提升","寻求学习机会"],
        "中性":["选择性成长领域","自我提升的实用方法","必要时培养技能"],
        "消极":["固定心态","对个人改变持怀疑态度","避免具有挑战性的情况","相信特质大多是固定的"]
    }
    growth_mindset = random.choice(growth_mindset_options[category])
    
    # Generate decision-making style
    decision_making_styles = [
        "分析","直觉","深思熟虑","冲动",
        "协作","独立","回避","依赖",
        "理性","情绪化","拖延","果断"
    ]
    # Weight the selection based on attitude
    if attitude in ["现实", "务实", "斯多葵学派"]:
        decision_style_weights = [0.3, 0.1, 0.2, 0.05, 0.1, 0.1, 0.05, 0.05, 0.3, 0.05, 0.05, 0.15]  # More analytical/rational
    elif attitude in ["焦虑", "偏执狂"]:
        decision_style_weights = [0.1, 0.05, 0.2, 0.05, 0.05, 0.05, 0.3, 0.2, 0.1, 0.2, 0.3, 0.05]  # More avoidant/procrastinating
    elif attitude in ["乐观", "热情"]:
        decision_style_weights = [0.1, 0.3, 0.05, 0.2, 0.2, 0.1, 0.05, 0.05, 0.1, 0.2, 0.05, 0.2]  # More intuitive/decisive
    else:
        decision_style_weights = None  # Equal weights
    
    decision_making_style = random.choices(
        decision_making_styles,
        weights=decision_style_weights,
        k=1
    )[0] if decision_style_weights else random.choice(decision_making_styles)
    
    return {
        "attitude": attitude,
        "attitude_category": category,
        "attitude_details": attitude_details,
        "seeking_advice": seeking_advice,
        "coping_mechanism": coping_mechanism,
        "emotional_stability": emotional_stability,
        "risk_tolerance": risk_tolerance,
        "change_adaptability": change_adaptability,
        "social_outlook": social_outlook,
        "future_orientation": future_orientation,
        "growth_mindset": growth_mindset,
        "decision_making_style": decision_making_style
    }

async def generate_habit_timeline(habit: str, age: int, overcome: bool) -> List[Dict]:
    """生成习惯的时间线，包括开始、发展和可能的克服过程。

    随机生成1-3个数字，然后使用GPT生成故事。

    Args:
        habit: 具体的习惯
        age: 用户当前年龄
        overcome: 是否已克服该习惯

    Returns:
        List[Dict]: 习惯发展的时间线事件列表
    """
    # 随机生成1-3个数字
    num_events = random.randint(1, 3)
    random_numbers = [random.randint(1, 100) for _ in range(num_events)]

    # 计算合理的开始年龄
    start_age = max(13, age - random.randint(5, 20))

    # 构建提示词，使用随机数字和习惯信息
    prompt = f"""生成一个关于一个人与{habit.lower()}经历的故事。
    故事应该包括{num_events}个关键事件，从年龄{start_age}开始，到年龄{age}结束。
    这个人是否克服了这个习惯：{'是' if overcome else '否'}。

    使用这些随机数字作为灵感：{random_numbers}

    将响应格式化为JSON数组，每个事件都有以下字段：
    - age：事件发生的年龄（介于{start_age}和{age}之间）
    - event：发生的事情的简短标题
    - description：事件的详细描述
    - impact：这一事件如何影响该人与习惯的关系
    确保事件按时间顺序排列，并讲述一个关于这个习惯的连贯故事。
    如果这个人已经克服了这个习惯，包括他们在最后一场比赛中是如何做到的。

    """

    response = await get_completion(sys_prompt= "你是一个能够生成关于个人习惯的现实而详细的时间表的人工智能。只使用有效的JSON进行响应。", user_prompt=prompt, temperature=0.7)

    # 如果API调用失败，使用备用方法生成时间线
    if not response:
        return await generate_fallback_timeline(habit, age, overcome, start_age)

    # 尝试解析JSON响应
    try:
        timeline = json.loads(response)
        # 确保结果是列表
        if not isinstance(timeline, list):
            return await generate_fallback_timeline(habit, age, overcome, start_age)
        # 确保每个事件都有必要的字段
        for event in timeline:
            if not all(key in event for key in ["age", "event", "description"]):
                return await generate_fallback_timeline(habit, age, overcome, start_age)
        return timeline
    except json.JSONDecodeError:
        # 如果JSON解析失败，使用备用方法
        return await generate_fallback_timeline(habit, age, overcome, start_age)

async def generate_fallback_timeline(habit: str, age: int, overcome: bool, start_age: int) -> List[Dict]:
    """生成备用的习惯时间线，当GPT调用失败时使用。

    Args:
        habit: 具体的习惯
        age: 用户当前年龄
        overcome: 是否已克服该习惯
        start_age: 开始年龄

    Returns:
        List[Dict]: 习惯发展的时间线事件列表
    """
    timeline = []

    # 添加开始事件
    timeline.append({
        "age": start_age,
        "event": f"开始{habit.lower()}",
        "description": f"开始{habit.lower()}是因为{random.choice(['同伴压力', '压力缓解', '好奇心', '工作需求', '个人危机', '社会影响'])}",
        "impact": "对习惯的初步接触"
    })

    # 添加1-3个中间事件
    events_count = random.randint(1, 3)
    available_years = list(range(start_age + 1, age))

    if len(available_years) >= events_count:
        event_years = sorted(random.sample(available_years, events_count))

        for year in event_years:
            event_type = random.choice([
                "加剧", "减少", "暂时戒断", "认识", "干预"
            ])

            if event_type == "加剧":
                trigger = random.choice(["增加压力", "生活变化", "新社交圈", "工作压力", "个人危机"])
                timeline.append({
                    "age": year,
                    "event": f"增加{habit.lower()}的频率/强度",
                    "description": f"习惯加剧是因为{trigger}",
                    "impact": "习惯在日常生活中变得更加根深蒂固"
                })
            elif event_type == "减少":
                trigger = random.choice(["健康问题", "亲人干预", "个人成长", "生活方式改变"])
                timeline.append({
                    "age": year,
                    "event": f"减少{habit.lower()}的频率/强度",
                    "description": f"尝试减少习惯是因为{trigger}",
                    "impact": "开始对习惯有了更多的控制"
                })
            elif event_type == "暂时戒断":
                trigger = random.choice(["健康问题", "新关系", "个人挑战", "专业建议"])
                duration = random.randint(1, 12)
                timeline.append({
                    "age": year,
                    "event": f"暂时戒断{habit.lower()}",
                    "description": f"戒断{habit.lower()}的时间是{duration}个月，因为{trigger}",
                    "impact": "经历了没有习惯的生活，但最终又回到了习惯",
                    "duration_months": duration
                })
            elif event_type == "认识":
                trigger = random.choice(["自我反思", "外部反馈", "健康后果", "生活事件"])
                timeline.append({
                    "age": year,
                    "event": f"认识到{habit.lower()}的影响",
                    "description": f"对习惯的影响有了新的认识，因为{trigger}",
                    "impact": "对习惯的作用有了新的看法"
                })
            elif event_type == "干预":
                trigger = random.choice(["家庭干预", "医疗建议", "治疗会议", "支持小组"])
                timeline.append({
                    "age": year,
                    "event": f"对{habit.lower()}进行干预",
                    "description": f"他人通过{trigger}来解决习惯问题",
                    "impact": "外部支持创造了改变的机会"
                })

    # 如果已克服习惯，添加克服事件
    if overcome:
        quit_age = age - random.randint(1, min(5, age - start_age))
        trigger = random.choice(["健康原因", "个人承诺", "支持系统", "生活变化", "专业帮助", "精神觉醒"])
        methods = random.sample(["逐渐减少", "直接戒断", "治疗", "支持小组", "替代习惯", "生活方式改变", "药物"], random.randint(1, 3))
        timeline.append({
            "age": quit_age,
            "event": f"成功克服{habit.lower()}",
            "description": f"最终克服了习惯，因为{trigger}，使用了{', '.join(methods)}",
            "impact": "实现了对习惯的自由，并经历了积极的生活变化",
            "methods": methods
        })

    # 按年龄排序
    return sorted(timeline, key=lambda x: x["age"])

async def generate_bad_habits(age: int = None) -> Dict[str, Union[bool, str, List, Dict]]:
    """生成有关不良习惯的信息，包括详细的时间维度。

    此函数随机生成用户是否有不良习惯，并提供有关这些习惯的具体信息。
    它包括常见的不良习惯，如吸烟、饮酒、熬夜或过度使用屏幕，以及用户是否已经克服了这些习惯。
    该函数还生成了一个详细的时间线，展示了习惯如何随着时间的推移而发展，包括开始年龄、关键事件以及可能的克服时间。

    Args:
        age: 用户的年龄（如果为None，则使用generate_age_info函数生成年龄）

    Returns:
        Dict：包含有关不良习惯的全面时间相关信息：
            - has_bad_habits：一个布尔值，指示用户是否有不良习惯
            - habit_details：一个字符串，描述具体的不良习惯，或者如果没有不良习惯，则为None
            - overcome_habits：一个布尔值，指示用户是否已经克服了任何以前的不良习惯
            - current_status：不良习惯的当前状态（"没有不良习惯"、"活跃"或"克服"）
            - timeline：一个事件列表，展示了习惯如何随着时间的推移而发展
            - future_plans：有关戒断计划的信息（如果习惯处于活跃状态）
    """
    if age is None:
        # 如果未提供年龄，使用generate_age_info函数获取年龄
        age_info = await generate_age_info()
        age = age_info["age"]

    bad_habits = ['吸烟', '饮酒', '熬夜', '过度使用屏幕', '暴饮暴食', '咬指甲']  # Translate 'Smoking', 'Drinking alcohol', 'Staying up late', 'Excessive screen time', 'Overeating', 'Nail-biting' to '吸烟', '饮酒', '熬夜', '过度使用屏幕', '暴饮暴食', '咬指甲'
    has_bad_habits = random.choice([True, False])

    result = {
        "has_bad_habits": has_bad_habits,
        "habit_details": None,
        "overcome_habits": False,
        "current_status": "没有不良习惯",
        "timeline": []
    }

    if has_bad_habits:
        habit = random.choice(bad_habits)
        overcome_habits = random.choice([True, False])

        result["habit_details"] = habit
        result["overcome_habits"] = overcome_habits
        result["current_status"] = "克服" if overcome_habits else "活跃"

        # 生成习惯的时间线
        result["timeline"] = await generate_habit_timeline(habit, age, overcome_habits)

        # 添加未来计划（如果习惯尚未克服）
        if not overcome_habits:
            has_plans = random.choice([True, False])
            if has_plans:
                result["future_plans"] = {
                    "intends_to_quit": True,
                    "planned_timeframe": random.choice([
                        "一个月内", "六个月内",
                        "一年内", "将来某个时候"
                    ]),
                    "methods_considered": random.sample([
                        "逐渐减少", "专业帮助", "支持小组",
                        "替代习惯", "生活方式改变", "药物"
                    ], random.randint(1, 3))  # Translate 'gradual reduction', 'professional help', 'support groups', 'alternative habits', 'lifestyle changes', 'medication' to '逐渐减少', '专业帮助', '支持小组', '替代习惯', '生活方式改变', '药物'
                }
            else:
                result["future_plans"] = {
                    "intends_to_quit": False,
                    "reason": random.choice([
                        "喜欢这个习惯", "不认为这个习惯有问题",
                        "曾经尝试过但失败了", "缺乏动力"
                    ])  # Translate 'enjoys the habit', 'doesn\'t see it as problematic', 'has tried and failed before', 'lacks motivation' to '喜欢这个习惯', '不认为这个习惯有问题', '曾经尝试过但失败了', '缺乏动力'
                }

    return result