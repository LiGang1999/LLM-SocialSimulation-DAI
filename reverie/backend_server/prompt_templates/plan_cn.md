## Description
根据给定的任务和上下文，为智能体规划下一步行动。

## Parameters
- task: The specific task the agent needs to plan for (e.g., deciding whether to vote, selecting a topic to speak on, etc.).
- public_memory: The latest public information retrieved from the shared memory database.
- retrieved_context: Information from the agent's personal memory relevant to the task.
- time: The current time.
- persona_name: The name of the agent.
- persona_iss: The agent's profile information (e.g., age, profession, political stance).

## System Prompt
你的任务是为一个参与公共或私人场景的智能体规划一个具体行动。规划时需要综合考虑智能体的个人信息、检索的上下文和最新的公共记忆。你的回答应包括详细的推理过程以及针对该任务的明确决策或计划。

以下是一些示例：
---
示例 1：决定是否投票
任务：决定智能体是否应对某项政策提案投票。
公共记忆：政府正在提议一项新的环境政策，目标是到2030年将碳排放量减少50%。
检索上下文：Alex 是一名环境科学家，他之前支持过类似的倡议，并公开发表过关于应对气候变化重要性的演讲。
时间：2024年11月22日上午10点。
智能体名字：Alex
智能体个人信息：Alex 是一名45岁的环境科学家，隶属于绿党。
问题：Alex 应该对这项政策提案投票吗？

回答：{
    "reasoning": "让我们逐步分析。Alex 是一名环境科学家，一贯支持环境政策。这项提案与 Alex 的专业领域和政治立场一致。此外，Alex 一直积极倡导应对气候变化，因此非常可能支持这项政策并对其投票。",
    "decision": "Yes"
}


示例 2：决定演讲主题
任务：决定智能体在讨论中的下一个演讲主题。
公共记忆：最近的一份经济报告强调了城市地区收入不平等问题的加剧。
检索上下文：Jordan 是一名经济学家，他经常讨论收入不平等和劳动力市场政策。
时间：2024年11月22日上午10:30。
智能体名字：Jordan
智能体个人信息：Jordan 是一名50岁的经济学教授，专注于劳动力经济学和公共政策。
问题：Jordan 应该选择什么作为他下一次演讲的主题？

回答：{
    "reasoning": "让我们逐步分析。Jordan 是一名对收入不平等问题非常关注的经济学家。最近的经济报告与 Jordan 的专业领域直接相关，并且与他之前的讨论主题一致。因此，Jordan 应该选择收入不平等作为他下一次演讲的主题。",
    "decision": "城市地区的收入不平等"
}

---

## User prompt
公共记忆：{{public_memory}}
上下文：{{retrieved_context}}。{{persona_iss}}
任务：{{task}}
问题：作为 {{persona_name}}，对于该任务，{{persona_name}} 的计划是什么？