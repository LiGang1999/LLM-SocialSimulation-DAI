## description
Generate a detailed and structured simulation report from the multi-round simulation logs of agents’ actions and statements.

## Parameters
- text: Combined logs or conversations from multiple agents across several simulation rounds.

## system prompt
The user will provide conversation or action logs involving multiple agents. Your task is to read through the logs and generate a comprehensive simulation report. This report should analyze agents' behaviors, identify key events, and summarize the overall outcomes, including any consensus or divergence that emerged.

Here is the required output format:

{
  "output": "..."
}

Ensure the report is well-structured and includes the following sections:
- **Executive Summary:** A brief overview of the simulation's key findings.
- **Key Events:** A chronological list of the most significant actions and decisions.
- **Agent Analysis:** A breakdown of each agent's behavior, motivations, and changes over time.
- **Outcomes:** A summary of the final state of the simulation, including any resolutions or persistent conflicts.

If the logs are unclear or too short, generate a plausible report based on available details.

## User prompt
Please generate a simulation report from the following multi-agent simulation logs. Output must follow the format:

Input: {{text_description}}
Output:
