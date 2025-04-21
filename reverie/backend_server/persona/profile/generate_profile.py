#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
这个模块用于生成完整的个人资料。

主要功能：
1. 从 generate_based_summary.py 获取基础摘要
2. 动态加载并验证属性结构
3. 生成完整的个人资料
4. 生成最终的总结摘要
5. 支持批量生成多个用户配置文件
"""

import json
import os
import sys
import time
import asyncio
from typing import Dict, List, Any, Optional
from utils.llm import get_completion
from utils.logs import L

# 导入基础摘要生成函数
from persona.profile.generate_based_summary import generate_simple_summary

def get_project_root() -> str:
    """获取项目根目录的路径"""
    return os.path.dirname(os.path.abspath(__file__))

def load_json_file(file_path: str) -> Dict:
    """读取并验证JSON文件
    
    Args:
        file_path: JSON文件路径
        
    Returns:
        Dict: JSON文件内容
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        L.info(f"读取JSON文件时出错: {e}")
        return {}

def save_json_file(file_path: str, data: Dict) -> None:
    """保存JSON文件
    
    Args:
        file_path: 目标文件路径
        data: 要保存的数据
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        L.info(f"保存JSON文件时出错: {e}")

def extract_paths(obj: Dict, prefix: str = "") -> List[str]:
    """从嵌套的JSON对象中提取所有属性路径
    
    Args:
        obj: 嵌套的JSON对象
        prefix: 当前路径前缀
        
    Returns:
        List[str]: 属性路径列表
    """
    paths = []
    for key, value in obj.items():
        new_prefix = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            if not value:  # 空字典表示叶子节点
                paths.append(new_prefix)
            else:
                paths.extend(extract_paths(value, new_prefix))
    return paths

async def generate_attribute_value(path: str, base_summary: str) -> str:
    """为给定的属性路径生成值
    
    Args:
        path: 属性路径
        base_summary: 基础摘要文本
        
    Returns:
        str: 生成的属性值
    """
    system_prompt = """你是一个创意无限的AI助手，专门为个人资料生成深度、丰富、有趣的属性值。根据提供的基本摘要和属性路径，生成一个详细的、有深度的、充满个性的值，要求：

1. 与基本摘要中的信息保持一致，但可以扩展和丰富这些信息
2. 与属性路径的语义含义相关，并深入探索这个属性的各个方面
3. 包含丰富的细节、具体的例子和生动的描述
4. 可以充分发挥想象力，创造独特的、有趣的内容，但要保持与人物性格的一致性
5. 如果是描述类属性，生成的内容应该丰富详尽，不设字数限制

请充分发挥创造力，创造出真实、丰富、有深度的人物属性。"""
    
    # 为不同的属性路径定制提示词
    if path == "daily_plan_req":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请基于这个人的性格、生活态度和习惯，生成一个详细的每日计划要求。这个要求应该反映他们的个人偏好、优先事项和日常结构偏好。请非常具体地描述他们对时间安排、活动类型和日常结构的偏好。"
    elif path == "name" or path == "first_name" or path == "last_name":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请基于这个人的背景、文化和个性，生成一个适合的{path}。这个名字应该反映他们的身份、文化背景和个人特质。如果可能，请解释这个名字的来源或含义。"
    elif path == "innate":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请生成一个详细的描述，说明这个人天生的特质、性格特点和天赋。这应该包括他们天生的性格特点、情绪倾向、认知风格和人际交往偏好。请提供具体的例子和细节，以展示这些天生特质如何影响他们的生活和与他人的互动。"
    elif path == "learned":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请生成一个详细的描述，说明这个人通过经验和学习获得的技能、知识和特质。这应该包括他们的教育背景、职业技能、生活经验和重要的人生课程。请提供具体的例子，说明这些后天获得的特质如何形成并影响他们的人生道路。"
    elif path == "currently":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请生成一个详细的描述，说明这个人当前的生活状态、目标和挑战。这应该包括他们目前的职业状态、个人项目、关系状态和短期目标。请提供具体的细节，说明他们当前的生活情况和他们正在处理的任何特定问题或机会。"
    elif path == "lifestyle":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请生成一个详细的描述，说明这个人的日常生活方式、习惯和偏好。这应该包括他们的日常作息、饮食习惯、运动习惯、休闲活动和社交模式。请提供具体的细节，展示他们如何度过一天，以及这些习惯如何反映他们的价值观和优先事项。"
    elif path == "age":
        user_prompt = f"基本摘要：\n{base_summary}\n\n请基于这个人的生活经历、职业阶段和生活状态，提取或生成一个具体的年龄。如果摘要中已经提到了年龄，请直接使用该年龄。"
    else:
        user_prompt = f"基本摘要：\n{base_summary}\n\n属性路径：{path}\n\n请为这个属性生成一个详细、丰富、有深度的值，与基本摘要一致且符合属性语义含义。请充分发挥想象力，创造独特、有趣的内容，并提供具体的细节和例子。"
    
    try:
        response = await get_completion(sys_prompt=system_prompt, user_prompt=user_prompt)
        return response.strip() if response else ""
    except Exception as e:
        L.info(f"生成属性值时出错 ({path}): {e}")
        return ""

async def generate_final_summary(profile: Dict, base_summary: str) -> str:
    """生成最终的总结摘要
    
    Args:
        profile: 完整的个人资料
        base_summary: 基础摘要
        
    Returns:
        str: 最终的总结摘要
    """
    system_prompt = """你是一个AI助手，专门撰写全面的个人资料摘要。根据提供的基本摘要和完整资料，生成一个250字的摘要，要求：
1. 包含基本摘要中的核心信息
2. 整合完整资料中的重要细节
3. 保持逻辑流畅和连贯性
4. 以清晰的段落呈现，每段关注不同方面
5. 确保所有信息一致且相互关联"""
    
    user_prompt = f"基本摘要：\n{base_summary}\n\n完整资料：\n{json.dumps(profile, ensure_ascii=False, indent=2)}\n\n请生成一个全面的摘要，将资料的各个方面编织成一个连贯的叙述，并以清晰的段落组织。"
    try:
        response = await get_completion(sys_prompt=system_prompt, user_prompt=user_prompt)
        return response.strip() if response else ""
    except Exception as e:
        L.info(f"生成最终摘要时出错: {e}")
        return ""

def print_section(section: Dict, indent: int = 0) -> None:
    """打印配置部分的内容
    
    Args:
        section: 要打印的配置部分
        indent: 缩进级别
    """
    indent_str = "  " * indent
    for key, value in section.items():
        if isinstance(value, dict):
            L.info(f"{indent_str}{key}:")
            print_section(value, indent + 1)
        else:
            L.info(f"{indent_str}{key}: {value}")

async def generate_section(template_section: Dict, base_summary: str, section_name: str, indent: int = 0) -> Dict:
    """生成配置文件的一个部分
    
    Args:
        template_section: 模板中的对应部分
        base_summary: 基础摘要
        section_name: 部分名称
        indent: 缩进级别
        
    Returns:
        Dict: 生成的配置部分
    """
    section_result = {}
    indent_str = "  " * indent
    
    L.info(f"{indent_str}正在生成 {section_name} 部分...")
    
    try:
        # 如果模板部分是字典，则处理其中的每个项
        if isinstance(template_section, dict):
            for key, value in template_section.items():
                current_path = f"{section_name}.{key}" if section_name else key
                
                # 如果值是字典，递归处理
                if isinstance(value, dict):
                    if not value:  # 空字典表示叶子节点
                        generated_value = await generate_attribute_value(current_path, base_summary)
                        section_result[key] = generated_value
                        L.info(f"{indent_str}  - {key}: {generated_value}")
                    else:  # 嵌套节点
                        section_result[key] = await generate_section(value, base_summary, current_path, indent + 1)
                else:
                    # 对于非字典值，直接使用模板中的值
                    section_result[key] = value
                    L.info(f"{indent_str}  - {key}: {value} (保留原值)")
        else:
            # 如果模板部分不是字典，直接生成值
            generated_value = await generate_attribute_value(section_name, base_summary)
            return generated_value
    except Exception as e:
        L.info(f"{indent_str}生成 {section_name} 部分时出错: {e}\n")
        # 出错时返回原始值
        return template_section
    
    return section_result

async def generate_single_profile(template: Dict, profile_index: int = 0) -> Dict:
    """生成一个完整的个人资料
    
    Args:
        template: 属性模板
        profile_index: 配置文件索引
        
    Returns:
        Dict: 生成的个人资料
    """
    L.info(f"\n正在生成第 {profile_index+1} 个个人资料...")
    
    # 初始化结果字典
    profile = {}
    
    # 生成基础摘要
    L.info(f"\n正在生成第 {profile_index+1} 个个人资料的基础摘要...")
    base_summary = await generate_simple_summary()
    
    if not base_summary:
        L.info("基础摘要生成失败，无法继续生成个人资料")
        return None
    
    L.info("\n基础摘要:")
    L.info(base_summary)
    
    # 初始化个人资料字典
    profile = {
        "Base Summary": base_summary,
        "Generated At": time.strftime("%Y-%m-%d %H:%M:%S"),
        "Profile Index": profile_index + 1
    }
    
    # 逐个生成各个部分
    for section_name, section_template in template.items():
        L.info(f"\n正在生成 {section_name} 部分...")
        
        try:
            profile[section_name] = await generate_section(section_template, base_summary, section_name)
            L.info(f"\n{section_name} 部分生成完成\n")
            L.info("当前生成的内容:")
            print_section({section_name: profile[section_name]})
            L.info("\n" + "-"*50 + "\n")
        except Exception as e:
            L.info(f"生成 {section_name} 部分时出错: {e}\n")
            continue
    
    # 生成最终摘要
    L.info("正在生成最终总结...")
    final_summary = await generate_final_summary(profile, base_summary)
    
    # 添加最终摘要到结果中
    profile["Final Summary"] = final_summary
    
    L.info("\n最终总结:")
    L.info(final_summary)
    
    return profile

async def generate_scratch_profile(description: str) -> Dict:
    template_path = os.path.join(get_project_root(), 'data', 'scratch_1.json')
    template = load_json_file(template_path)
    profile = await generate_single_profile(template)
    return profile


async def generate_multiple_profiles(num_profiles: int = 1) -> None:
    """生成多个完整的个人资料，并只保存在一个合并的JSON文件中
    
    Args:
        num_profiles: 要生成的个人资料数量
    """
    # 获取项目相关路径
    project_root = get_project_root()
    
    # 设置输出目录
    output_dir = os.path.join(project_root, 'src', 'generate_user_profile', 'code', 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 加载属性模板
    template_path = "/home/zhou/persona/src/generate_user_profile/code/data/100.json"
    template = load_json_file(template_path)
    if not template:
        L.info("无法加载属性模板文件，请确保文件存在且格式正确")
        return
    
    L.info(f"开始生成 {num_profiles} 个个人资料...\n")
    
    # 生成时间戳用于文件名
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    
    # 初始化存储所有配置文件的字典
    all_profiles = {
        "metadata": {
            "timestamp": timestamp,
            "profiles_completed": 0,
            "total_profiles": num_profiles,
            "generation_start_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    # 设置合并文件路径
    all_profiles_path = os.path.join(output_dir, f"all_profiles_{timestamp}.json")
    
    # 初始化保存合并文件
    save_json_file(all_profiles_path, all_profiles)
    L.info(f"初始化合并文件: {all_profiles_path}")
    
    # 逐个生成配置文件
    for i in range(num_profiles):
        L.info(f"\n===== 开始生成第 {i+1}/{num_profiles} 个用户资料 =====\n")
        
        # 生成单个配置文件
        profile = await generate_single_profile(template, i)
        
        if not profile:
            L.info(f"第 {i + 1} 个资料生成失败，跳过")
            continue
        
        # 添加到总字典并保存
        all_profiles[f"Profile_{i+1}"] = profile
        all_profiles["metadata"]["profiles_completed"] = i + 1
        all_profiles["metadata"]["last_update_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存更新后的合并文件
        save_json_file(all_profiles_path, all_profiles)
        L.info(f"\n总进度更新: {i+1}/{num_profiles} 个资料已完成")
        L.info(f"已将第 {i+1} 个用户资料添加到合并文件: {all_profiles_path}")
        L.info("\n" + "="*50 + "\n")
    
    # 添加生成完成时间
    all_profiles["metadata"]["generation_end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
    all_profiles["metadata"]["status"] = "completed"
    save_json_file(all_profiles_path, all_profiles)
    
    L.info(f"\n所有 {num_profiles} 个个人资料已成功生成并保存到: {all_profiles_path}")



if __name__ == "__main__":
    # 加载模板文件
    template_path = os.path.join(get_project_root(), 'data', 'scratch_1.json')
    template = load_json_file(template_path)
    
    # 异步运行生成单个用户配置文件
    async def main():
        profile = await generate_single_profile(template)
        
        # 保存到user profile目录
        timestamp = int(time.time())
        output_dir = os.path.join(get_project_root(), 'user profile')
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'user_profile_{timestamp}.json')
        save_json_file(output_path, profile)
    
    # 运行异步主函数
    asyncio.run(main())