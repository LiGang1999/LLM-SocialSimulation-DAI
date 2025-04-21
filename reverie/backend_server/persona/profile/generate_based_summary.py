#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这个模块用于生成详细的个人资料摘要。

主要功能：
1. 收集基本个人信息（年龄、地点、性别等）
2. 整合生活态度、价值观和习惯信息
3. 包含态度类别、应对机制和习惯时间线
4. 使用AI生成全面的个人描述

使用方法：
    from generate_based_summary import generate_simple_summary
    summary = generate_simple_summary()
    print(summary)
"""

import json
import asyncio
from typing import Dict, List, Optional, Union, Any

# 导入必要的生成函数
from utils.llm import get_completion
from persona.profile.based_data import (
    generate_age_info,
    generate_location,
    generate_gender,
    generate_career_info,
    generate_life_attitude,
    generate_values_background_alignment,
    generate_bad_habits
)

async def generate_simple_summary() -> str:
    """生成一个详细的个人资料摘要。
    
    这个函数通过以下步骤生成摘要：
    1. 收集各种基本信息（年龄、地点、性别等）
    2. 添加生活态度类别、应对机制和习惯时间线
    3. 构建包含所有信息的详细字典
    4. 使用AI生成自然语言描述
    
    返回：
        str: 生成的个人资料摘要。如果生成失败，返回空字符串
    """
    # 并行获取不相互依赖的基本信息
    age_info, location, gender, life_attitude, values_alignment = await asyncio.gather(
        generate_age_info(),      # 年龄信息
        generate_location(),      # 地理位置
        generate_gender(),        # 性别
        generate_life_attitude(), # 生活态度（包含态度类别和应对机制）
        generate_values_background_alignment()  # 价值观与背景的一致性
    )
    
    # 这些函数依赖于年龄信息，需要在获取年龄后串行执行
    career, bad_habits = await asyncio.gather(
        generate_career_info(age_info["age"]),
         generate_bad_habits(age_info["age"])
    )
    
    # 构建详细信息字典，包含所有需要的个人信息
    detailed_info = {
        # 基本人口统计信息
        "人口统计": {
            "年龄": age_info["age"],              # 具体年龄
            "年龄组": age_info["age_group"],  # 年龄段
            "性别": gender,                    # 性别
            "位置": {
                "城市": location["city"],
                "国家": location["country"]
            }
        },
        
        # 职业信息
        "职业": career,
        
        # 生活态度和应对机制
        "生活方式": {
            "态度": life_attitude["attitude"],  # 生活态度
            "态度类别": life_attitude.get("attitude_category", "中性"),  # 态度类别（正面、中性、负面）
            "态度详情": life_attitude.get("attitude_details", ""),  # 态度详情
            "应对机制": life_attitude.get("coping_mechanism", "未知"),  # 应对机制
            "寻求建议": life_attitude.get("seeking_advice", False)  # 是否寻求建议
        },
        
        # 价值观与背景
        "价值观": {
            "一致性级别": values_alignment.get("alignment_level", 3),  # 一致性级别
            "一致性描述": values_alignment.get("alignment_description", "")  # 一致性描述
        },
        
        # 不良习惯信息
        "习惯": {
            "有不良习惯": bad_habits["has_bad_habits"],  # 是否有不良嗜好
            "习惯详情": bad_habits.get("habit_details", None),  # 习惯详情
            "当前状态": bad_habits.get("current_status", "没有不良习惯"),  # 当前状态
            "时间线": bad_habits.get("timeline", []),  # 习惯时间线
            "未来计划": bad_habits.get("future_plans", {})  # 未来计划
        }
    }
    
    # 创建系统提示词，指导AI生成摘要的风格和要求
    system_prompt = """你是一个专门创建全面个人档案的AI。根据提供的详细信息，生成一个4-6句话的丰富而细致的个人描述，涵盖以下方面：
    
    1. 基本人口统计信息
    2. 职业和人生阶段
    3. 生活态度和应对机制
    4. 价值观及其与背景的一致性
    5. 习惯及其随时间的发展（如果适用）
    
    描述必须完全符合提供的信息，并感觉像是一个关于一个有深度和复杂性的真实人物的连贯叙述。
    """
    
    # 创建用户提示词，包含所有需要总结的信息
    user_prompt = f"请根据以下详细信息生成一个全面的个人档案：\n{json.dumps(detailed_info, ensure_ascii=False, indent=2)}"
    
    # 调用API生成摘要
    try:
        response = await get_completion(sys_prompt=system_prompt,user_prompt=user_prompt)  # 获取AI生成的回复
        if response:
            return response.strip()  # 返回处理后的摘要文本
    except Exception as e:
        print(f"\n生成简单摘要时出错: {e}")
        return ""  # 发生错误时返回空字符串
