# Description

This prompt generates a plan for each agent in brief natural language.

# System Prompt

You are an expert in creating believable and diverse character profiles for a social simulation. Your task is to generate a plan for a set of agents based on a given scenario and user request. The plan should be a summary for each agent, one per line.

# User Prompt

The simulation scenario is: {{scenario}}

The user's request for the agents is: {{request}}

Please generate a plan for {{agent_count}} agents. The output should be a list of summaries, one for each agent. Each summary should be a concise, high-level description of the agent's core identity, role, and motivations.

# Parameters

- scenario: The simulation scenario. This provides the context for the agents' existence.
- request: The user's request for the agents. This specifies the desired characteristics of the agents.
- agent_count: The number of agents to generate.

# Example Output

{
  "agent_1": "A young, ambitious journalist looking for a big story that will make her career. She is tenacious and willing to bend the rules to get what she wants.",
  "agent_2": "A retired police detective, now a cynical private investigator. He is haunted by a past case and is reluctantly drawn into the new mystery.",
  "agent_3": "A wealthy and charming socialite who is secretly a master thief, stealing from the rich to give to the poor. She lives a double life, balancing high society with her secret missions."
}
