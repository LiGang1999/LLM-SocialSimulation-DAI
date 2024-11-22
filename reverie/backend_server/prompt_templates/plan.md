## Description
Plan the next action for the agent based on the given task and context.

## Parameters
- task: The specific task the agent needs to plan for (e.g., deciding whether to vote, selecting a topic to speak on, etc.).
- public_memory: The latest public information retrieved from the shared memory database.
- retrieved_context: Information from the agent's personal memory relevant to the task.
- time: The current time.
- persona_name: The name of the agent.
- persona_iss: The agent's profile information (e.g., age, profession, political stance).

## System Prompt
You are tasked with planning a specific action for an agent involved in a public or private scenario. The task requires considering the agent's personal information, retrieved context, and the latest public memory. Your response should include a detailed reasoning process and a concrete decision or plan tailored to the given task.

Here are some examples:
---
Example 1: Deciding Whether to Vote
Task: Decide whether the agent should vote on a policy proposal.
Public Memory: The government is proposing a new environmental policy to reduce carbon emissions by 50% by 2030.
Retrieved Context: Alex is an environmental scientist. Alex has previously supported similar initiatives and has publicly spoken out about the importance of combating climate change.
Time: November 22, 2024, 10:00 AM.
Persona Name: Alex
Persona ISS: Alex is a 45-year-old environmental scientist and a member of the Green Party.

Question: Should Alex vote on this policy proposal?

Answer:
{
    "reasoning": "Let's think step by step. Alex is an environmental scientist who has consistently supported environmental policies. This proposal aligns with Alex's professional expertise and political stance. Furthermore, Alex has actively advocated for combating climate change, making it highly likely that Alex will support the policy and vote on it.",
    "decision": "Yes"
}


Example 2: Deciding a Speaking Topic
Task: Decide the topic for the agent's next speech during a discussion.
Public Memory: A recent economic report highlighted growing income inequality in urban areas.
Retrieved Context: Jordan is an economist who frequently discusses income inequality and labor market policies.
Time: November 22, 2024, 10:30 AM.
Persona Name: Jordan
Persona ISS: Jordan is a 50-year-old professor of economics with expertise in labor economics and public policy.

Question: What topic should Jordan choose for their speech?

Answer:
{
    "reasoning": "Let's think step by step. Jordan is an economist with a strong interest in income inequality. The recent economic report is directly relevant to Jordan's area of expertise and aligns with their previous discussions. Therefore, Jordan should choose income inequality as the topic for their next speech.",
    "decision": "Income inequality in urban areas"
}
---

## User prompt
Task: {{task}}
Public Memory: {{public_memory}}
Context: {{persona_iss}}. {{retrieved_context}}
Question: What is the plan for {{persona_name}} regarding this task?