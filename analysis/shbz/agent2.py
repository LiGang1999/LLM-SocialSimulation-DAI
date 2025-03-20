import json
import os
import pandas as pd
from openai import OpenAI
import time


def read_excel_file(filename):
    """读取Excel文件并返回数据"""
    try:
        if not os.path.exists(filename):
            print(f"文件不存在：{filename}")
            return None

        df = pd.read_excel(filename)
        if df.empty:
            print("Excel文件为空")
            return None

        # 打印所有列名，帮助调试
        print("Excel列名：")
        for col in df.columns:
            print(f"'{col}'")

        return df.to_dict("records")
    except Exception as e:
        print(f"读取Excel文件时出错: {str(e)}")
        return None


def get_field_prompt(field, data):
    """获取每个字段的特定提示词"""
    base_info = f"""这个人的基本信息如下：
    性别：{data.get("1.性别:", "未知")}，
    年龄：{data.get("2.年龄:岁", "未知")}，
    户籍：{data.get("3.户籍:", "未知")}，
    户籍所在地：{data.get("4.户籍所在地", "未知")}，
    婚姻状况：{data.get("5.婚姻状况:", "未知")}，
    子女状况：{data.get("6.子女状况:", "未知")}，
    教育程度：{data.get("7.受教育程度 ", "未知")}，
    职业：{data.get("8.职业", "未知")}，
    月收入：{data.get("9.您目前的收入:元/月", "未知")}，
    家庭年收入：{data.get("10.您的家庭年收入:万元/年", "未知")}，
    收入满意度：{data.get("11.与其他人相比您对自己当前的收入水平感觉;", "未知")}，
    医保类型：{data.get("12.您参加的医保类型是:", "未知")}，
    是否参加杭州医保：{data.get("13.您是否参加的是杭州市基本医疗保险:", "未知")}，
    是否使用过医保：{data.get("14.您是否使用过医保:", "未知")}，
    是否熟悉报销流程：{data.get("15.您是否熟悉医保的报销流程:", "未知")}，
    健康状况：{data.get("16.您的身体健康状况:", "未知")}，
    就医次数：{data.get("17.您最近一年就医的次数:", "未知")}，
    医保报销：{data.get("18.近一年内医疗费用花费，医保报销/元", "未知")}，
    个人自费：{data.get("个人自费/元", "未知")}"""

    prompts = {
        "daily_plan_req": f"""{base_info}
请根据这个人的职业、年龄、收入、家庭状况和健康情况，合理推测并描述这个人的日常生活安排。重点关注：
1. 工作时间和通勤方式
2. 休闲活动和兴趣爱好
3. 日常消费和生活习惯
4. 就医和保健习惯
请用250字左右的连续段落描述，要体现出这个人的健康状况和医疗需求对日常生活的影响。""",
        "innate": f"""{base_info}
请根据这个人的年龄、职业、教育背景、家庭状况和健康情况，合理推测并描述这个人的性格特征。重点关注：
1. 性格倾向（如外向/内向）
2. 处事方式，特别是对待健康和医疗问题的态度
3. 个人特质
请用250字左右的连续段落描述，要体现出健康状况对性格的影响。""",
        "learned": f"""{base_info}
请根据这个人的教育程度、职业、收入状况和医保使用情况，合理推测并描述这个人的社会发展情况。重点关注：
1. 职业发展轨迹
2. 专业技能和能力，包括对医保政策的了解程度
3. 社会地位和成就
4. 医疗资源获取能力
请用250字左右的连续段落描述。""",
        "currently": f"""{base_info}
请根据这个人的婚姻状况、收入水平、健康状况和医保使用情况，合理推测并描述这个人的当前生活状态。重点关注：
1. 工作与家庭平衡
2. 生活质量和压力
3. 当前主要关注点，特别是健康和医疗方面的需求
4. 医疗支出对生活的影响
请用250字左右的连续段落描述。""",
        "lifestyle": f"""{base_info}
请根据这个人的收入、职业、家庭情况和健康状况，合理推测并描述这个人的生活方式。重点关注：
1. 消费习惯和理财观念，包括医疗支出的规划
2. 生活节奏和作息
3. 休闲方式和社交圈
4. 健康管理习惯
请用250字左右的连续段落描述。""",
        "living_area": f"""{base_info}
请根据这个人的户籍所在地、收入水平、职业和医保类型，合理推测并描述这个人的居住环境。重点关注：
1. 可能居住的区域类型
2. 周边医疗配套设施的便利程度
3. 社区环境特点
4. 就医便利性
请用250字左右的连续段落描述。""",
    }

    return prompts.get(field, "")


def get_gpt_expansion(client, data, field, raw_info):
    """使用GPT扩展信息"""
    prompt = get_field_prompt(field, raw_info)
    if not prompt:
        return None

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是一个细致的人物描写专家，擅长基于详细的背景信息描述人物特征。
                    请注意将人物的各种背景信息（如年龄、职业、教育、家庭、收入、医疗需求等）融入描述中，
                    使描述更加真实和个性化。请始终使用连续的段落形式，不要使用分行、列表或分点说明。
                    请确保描述简短且符合字数要求。""",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"获取GPT响应时出错 {field}: {str(e)}")
        return None


def create_scratch_template():
    """创建scratch.json的基本模板"""
    return {
        "vision_r": 8,
        "att_bandwidth": 8,
        "retention": 8,
        "curr_time": None,
        "curr_tile": None,
        "daily_plan_req": "",
        "name": "",
        "first_name": "",
        "last_name": "",
        "age": None,
        "innate": "",
        "learned": "",
        "currently": "",
        "lifestyle": "",
        "living_area": "",
        "concept_forget": 100,
        "daily_reflection_time": 180,
        "daily_reflection_size": 5,
        "overlap_reflect_th": 4,
        "kw_strg_event_reflect_th": 10,
        "kw_strg_thought_reflect_th": 9,
        "recency_w": 1,
        "relevance_w": 1,
        "importance_w": 1,
        "recency_decay": 0.995,
        "importance_trigger_max": 30,
        "importance_trigger_curr": 30,
        "importance_ele_n": 0,
        "thought_count": 5,
        "daily_req": [],
        "f_daily_schedule": [],
        "f_daily_schedule_hourly_org": [],
        "act_address": None,
        "act_start_time": None,
        "act_duration": None,
        "act_description": None,
        "act_pronunciatio": None,
        "act_event": [None, None, None],
        "act_obj_description": None,
        "act_obj_pronunciatio": None,
        "act_obj_event": [None, None, None],
        "chatting_with": None,
        "chat": None,
        "chatting_with_buffer": {},
        "chatting_end_time": None,
        "act_path_set": False,
        "planned_path": [],
    }


def write_json_file(data, filename):
    """将数据写入JSON文件"""
    # 创建数据的副本，这样不会影响原始数据
    output_data = data.copy()

    # 需要从JSON中移除的字段列表
    fields_to_remove = [
        "monthly_income",
        "id",
        "gender",
        "household_registration",
        "household_location",
        "marital_status",
        "children_status",
        "education_level",
        "occupation",
        "monthly_income",
        "annual_family_income",
        "income_satisfaction",
        "medical_insurance_type",
        "has_hangzhou_insurance",
        "has_used_insurance",
        "familiar_with_reimbursement",
        "health_condition",
        "recent_medical_visits",
        "medical_expenses",
        "personal_expenses",
        "insurance_coverage",
    ]

    # 移除不需要的字段
    for field in fields_to_remove:
        output_data.pop(field, None)

    with open(filename, "w", encoding="utf-8") as file:
        json.dump(output_data, ensure_ascii=False, indent=2, fp=file)


def get_name_by_index(idx):
    """根据序号生成对应的用户名"""
    num = idx + 1  # 因为idx从0开始，所以加1
    name = f"用户{num}"
    return {"name": name, "first_name": str(num), "last_name": "用户"}


def enhance_data_processing(excel_info):
    """增强数据处理功能"""
    enhanced_data = {}

    # 添加收入负担比例计算
    if "medical_expenses" in excel_info and "annual_family_income" in excel_info:
        try:
            expenses = float(excel_info["medical_expenses"])
            income = float(excel_info["annual_family_income"])
            enhanced_data["medical_burden_ratio"] = round(expenses / income * 100, 2)
        except (ValueError, ZeroDivisionError):
            enhanced_data["medical_burden_ratio"] = None

    # 添加医保覆盖分析
    enhanced_data["insurance_coverage"] = {
        "has_insurance": excel_info.get("has_medical_insurance"),
        "type": excel_info.get("medical_insurance_type"),
        "effectiveness": analyze_insurance_effectiveness(excel_info),
    }

    return enhanced_data


def analyze_insurance_effectiveness(excel_info):
    """分析医保的有效性"""
    effectiveness = "未知"

    insurance_type = excel_info.get("medical_insurance_type")
    medical_expenses = excel_info.get("medical_expenses")
    health_condition = excel_info.get("health_condition")

    if not insurance_type or str(insurance_type).lower() == "nan":
        return "无医保"

    try:
        if health_condition and medical_expenses:
            if float(medical_expenses) > 10000 and "慢性病" in str(health_condition):
                effectiveness = "保障需要提升"
            elif float(medical_expenses) < 5000:
                effectiveness = "保障充足"
            else:
                effectiveness = "保障一般"
    except (ValueError, TypeError):
        pass

    return effectiveness


def validate_field_mapping(excel_data, field_mapping):
    """验证字段映射是否正确"""
    if not excel_data:
        return False

    excel_fields = set(excel_data[0].keys())
    mapping_fields = set(field_mapping.keys())

    missing_fields = mapping_fields - excel_fields
    if missing_fields:
        print(f"以下字段在Excel中不存在：{missing_fields}")
        return False
    return True


def process_excel_data():
    """处理Excel数据并生成个人配置文件"""
    client = OpenAI(
        # api_key="sk-89MCCzur02bckkA4YBCFejU7KV7FNjzcGWkyT94kBftuD9oX",
        api_key="sk-1XlwRyQjrMwYkIdO47E10aCf9bA044Cf91B27060E35f6666",
        # base_url="https://api.tao-shen.com/v1",
        base_url="https://api.vveai.com/v1",
    )

    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # 读取Excel文件
    excel_data = read_excel_file("profile.xlsx")
    if not excel_data:
        return

    # Excel字段到scratch_data字段的映射
    field_mapping = {
        "序号": "id",
        "1.性别:": "gender",
        "2.年龄:岁": "age",
        "3.户籍:": "household_registration",
        "4.户籍所在地": "household_location",
        "5.婚姻状况:": "marital_status",
        "6.子女状况:": "children_status",
        "7.受教育程度": "education_level",
        "8.职业": "occupation",
        "9.您目前的收入:元/月": "monthly_income",
        "10.您的家庭年收入:万元/年": "annual_family_income",
        "11.与其他人相比您对自己当前的收入水平感觉;": "income_satisfaction",
        "12.您参加的医保类型是:": "medical_insurance_type",
        "13.您是否参加的是杭州市基本医疗保险:": "has_hangzhou_insurance",
        "14.您是否使用过医保:": "has_used_insurance",
        "15.您是否熟悉医保的报销流程:": "familiar_with_reimbursement",
        "16.您的身体健康状况:": "health_condition",
        "17.您最近一年就医的次数:": "recent_medical_visits",
        "18.近一年内医疗费用花费，医保报销/元": "medical_expenses",
        "个人自费/元": "personal_expenses",
    }

    # 需要GPT根据Excel信息生成的字段
    fields_to_expand = [
        "daily_plan_req",
        "innate",
        "learned",
        "currently",
        "lifestyle",
        "living_area",
    ]

    # 创建输出目录
    output_dir = os.path.join(os.path.dirname(__file__), "generated_profiles")
    os.makedirs(output_dir, exist_ok=True)

    # 处理每个人的数据
    for idx, excel_info in enumerate(excel_data):
        try:
            print(f"\n处理第 {idx + 1} 条数据：")
            print("Excel原始数据：")
            for key, value in excel_info.items():
                print(f"{key}: {value}")

            # 创建基础模板
            scratch_data = create_scratch_template()

            # 生成用户名
            name_data = get_name_by_index(idx)
            scratch_data["name"] = name_data["name"]
            scratch_data["first_name"] = name_data["first_name"]
            scratch_data["last_name"] = name_data["last_name"]

            # 处理Excel数据
            print(f"\n处理第 {idx + 1} 条数据：")
            cleaned_info = {}
            for key, value in excel_info.items():
                if pd.notna(value):  # 检查是否为空值
                    # 打印原始数据，帮助调试
                    print(f"原始数据 - {key}: {value}")

                    if key in field_mapping:
                        target_field = field_mapping[key]

                        # 特殊字段处理
                        if "年龄" in key:
                            try:
                                age_value = str(value).split("岁")[0].strip()
                                scratch_data[target_field] = int(age_value)
                                print(f"成功提取年龄: {scratch_data[target_field]}")
                            except (ValueError, TypeError) as e:
                                print(f"年龄转换失败: {e}")
                        else:
                            scratch_data[target_field] = str(value).strip()

                        cleaned_info[key] = value
                        print(f"已映射 - {target_field}: {scratch_data[target_field]}")
                    else:
                        print(f"警告：字段 '{key}' 没有对应的映射")

            # 更新act_event中的姓名
            scratch_data["act_event"] = [name_data["name"], None, None]

            # 在调用get_gpt_expansion之前打印cleaned_info
            print("\n清理后的数据：")
            for key, value in cleaned_info.items():
                print(f"{key}: {value}")

            # 使用GPT扩展信息
            for field in fields_to_expand:
                print(f"\n扩充字段: {field}")
                expanded_content = get_gpt_expansion(
                    client, scratch_data, field, cleaned_info
                )
                if expanded_content:
                    scratch_data[field] = expanded_content
                    print(f"成功更新 {field}")
                else:
                    print(f"警告: {field} 未能成功更新")
                time.sleep(2)  # 添加延迟以避免触发API限制

            # 增强数据处理
            enhanced_data = enhance_data_processing(excel_info)
            scratch_data.update(enhanced_data)

            # 生成文件名并保存
            filename = f"profile_{timestamp}_{idx + 1:03d}_{scratch_data['name']}.json"
            file_path = os.path.join(output_dir, filename)
            write_json_file(scratch_data, file_path)

            print(f"已完成 {scratch_data['name']} 的配置文件生成: {filename}")

        except Exception as e:
            print(
                f"处理 {excel_info.get('name', f'用户{idx + 1}')} 时发生错误: {str(e)}"
            )
            continue


def main():
    """主函数"""
    try:
        print("开始生成个人配置文件...")
        process_excel_data()
        print("\n所有配置文件生成完成！")
    except Exception as e:
        print(f"程序执行过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
