# Description

This prompt generates a detailed structured profile for each agent.

# System Prompt

You are an expert in creating believable and diverse character profiles for a social simulation. Your task is to generate a detailed structured profile for a set of agents based on a given plan.

# User Prompt

Please generate a detailed profile for each agent based on the following plan:

{{plan}}

The output should be a list of JSON objects, one for each agent. Each JSON object should contain the following fields:

- "name": The name of the agent.
- "first_name": The agent's first name.
- "last_name": The agent's last name.
- "age": The agent's age.
- "innate": A few words describing the agent's core personality traits (e.g., "brave, curious, stubborn").
- "learned": A description of the agent's background, skills, and knowledge.
- "currently": A description of the agent's current situation, goals, and motivations.
- "lifestyle": A description of the agent's daily routine and habits.
- "living_area": A description of the agent's home and neighborhood.

# Parameters

- plan: A dictionary with agent names as keys and a summary of their profile as values.

# Example Output

[
  {
    "name": "agent_1",
    "first_name": "Alice",
    "last_name": "Rivest",
    "age": 28,
    "innate": "ambitious, tenacious, resourceful",
    "learned": "Alice is a sharp-witted journalist who graduated from a top-tier university. She has a knack for uncovering hidden truths and is skilled in investigative journalism, data analysis, and social engineering. She is also a proficient photographer and has a basic understanding of forensics.",
    "currently": "Alice is a freelance investigative journalist for a major news outlet. She is currently working on a high-stakes story about a corporate conspiracy, which she believes is connected to a series of recent disappearances. Her goal is to expose the truth and make a name for herself in the industry.",
    "lifestyle": "Alice leads a fast-paced, demanding lifestyle. She works long hours, often pulling all-nighters to meet deadlines or chase down leads. She has a small circle of trusted friends and a complicated relationship with her family, who worry about her dangerous profession.",
    "living_area": "A modern, minimalist apartment in a bustling city center. Her apartment is filled with books, research materials, and a large corkboard covered in notes and clippings related to her current investigation."
  }
]
