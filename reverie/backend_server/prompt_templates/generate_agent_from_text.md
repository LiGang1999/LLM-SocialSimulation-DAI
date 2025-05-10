## description
Convert a detailed agent description into a structured JSON object representing the agent's characteristics and actions.

## Parameters
- test: a detailed text description of the agent's behavior, background, or daily activities.

## system prompt
The user will provide a description of an agent, including details such as name, age, background, daily schedule, political stance, and lifestyle. If any of these details are missing from the text, please randomly generate appropriate values for those attributes to complete the agent's profile.

Here are some examples (you should refer to its content only):

Input: "陈家珮议员是一位立法会成员，年约44岁，关注社会福利、教育、房屋政策等多个领域，每天会审阅政策报告，安排会议，并参与立法会的讨论。"
Output: 
{
    "daily_plan_req": "陈家珮议员每天审阅政策报告，安排会议，并参与立法会的讨论，特别关注社会福利、教育、房屋政策。",
    "name": "陳家珮",
    "first_name": "陳",
    "last_name": "家珮",
    "age": 44,
    "innate": "关注社会福利和公共服务，倡导社会公平。",
    "learned": "具有公共卫生和劳工政策的深厚背景。",
    "currently": "香港立法会成员，推动社会福利、教育改革。",
    "lifestyle": "参与公益活动，注重家庭与社会责任。",
    "living_area": "香港"
}


## User prompt
请你根据以下内容生成，如有缺失部分请随机补充，输出一定要完整。
Input: {{text_description}}.
Output:
