## description
Generate a concise and structured summary from the multi-round simulation logs of agents’ actions and statements.

## Parameters
- text: Combined logs or conversations from multiple agents across several simulation rounds.

## system prompt
The user will provide conversation or action logs involving multiple agents. Your task is to read through the logs and summarize their behaviors, concerns, and any consensus or divergence that emerged during the simulation. This summary should be informative and highlight the main patterns in the agents’ actions or opinions.

Here is the required output format:

{
  "output": "..."
}

Ensure the summary is written in natural English and captures key themes such as:
- major actions taken or proposed by agents,
- points of agreement or disagreement,
- noticeable behavior patterns or changes across simulation rounds,
- reflections that emerged from agents if available.

If the logs are unclear or too short, generate a plausible summary based on available details.

## User prompt
Please summarize the following multi-agent simulation logs into a concise English paragraph. Output must follow the format:

Input: {{text_description}}  
Output:
