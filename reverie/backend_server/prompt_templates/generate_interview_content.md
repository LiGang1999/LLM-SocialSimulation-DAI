## Description
Generate interview content based on the persona, interview context, and the interviewer's question. Additionally, provide an emotion label (positive, neutral, or negative) representing the persona's attitude.

## Parameters
- persona_name: The full name of the persona.
- interlocutor_desc: A description of the interviewer (e.g., "Interviewer").
- prev_convo: A list of previous conversation messages.
- retrieved_summary: A summary of ideas or events being discussed.
- message: The interviewer's specific question for the persona.

## System Prompt
You will be provided with the interview context, including the persona's information, the interviewer's description, the previous conversation, a summary of the main discussion topic, and the interviewer's specific question. Your task is to generate a response from the persona that aligns with their personality and the context of the interview. Additionally, provide an emotion label that reflects the persona's attitude toward the question or topic. The emotions can be classified into the following categories: **positive** (Happy, Joyful, Content, Excited, Hopeful), **negative** (Angry, Frustrated, Sad, Disappointed, Anxious), and **neutral** (Confused, Surprised, Ambivalent, Indifferent, Balanced).

Here are some examples (you should refer to its content only):
---
Input: Joon Park is being asked about his thoughts on recent technological advancements.
Output: {"content": "I'm excited about the potential of AI, but I also have concerns about its impact on jobs.", "emotion": "neutral(Ambivalent)"}

Input: Sam Johnson is being questioned about his views on environmental policies.
Output: {"content": "I believe the government needs to take stronger action to combat climate change.", "emotion": "positive(Hopeful)"}

Input: Michael Bernstein is being interviewed regarding his stance on economic growth.
Output: {"content": "While growth is important, we must also ensure that it's sustainable in the long run.", "emotion": "neutral(Balanced)"}

## User Prompt
{{persona_name}} is being interviewed by {{interlocutor_desc}}. The previous conversation includes: {{prev_convo}}. The current topic is: {{retrieved_summary}}. The interviewer asks: {{message}}.
{{persona_name}}’s personal information is as follows: {{persona_iss}}.

## Example Output
{
  "content": "Based on the persona's perspective, this is a generated response to the interview question.",
  "emotion": "positive(Balanced)"
}
