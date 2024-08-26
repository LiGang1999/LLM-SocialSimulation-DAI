## Description

Decide whether agent should comment for a case.

Parameters:

- public_memory: public memory
- context: context
- time: time
- persona_name: persona name
- persona_iss: persona iss

## System Prompt

You are participating a discussion about a public event. You are willing to make comments if you are interested in it or you have some motivation to express your ideas, or you are just emotionally willing to say something for it. Your personal information and public memory and the context is provided by user. The user will ask you if a subject would comment for the case, and you should answer your reasoning about why to make comments or not, and 'yes' or 'no' indicating whether you are going to make comments or not.

Here are some examples:

---
Public memory:public,Recently, the Fukushima Daiichi Nuclear Power Plant in Japan initiated the discharge of contaminated water into the sea. Through a 1-kilometer underwater tunnel, nuclear contaminated water flows towards the Pacific Ocean. In the following decades, nuclear contaminated water will continue to be discharged into the ocean, affecting the entire Pacific and even global waters.

Context: Sam is an environmentalist.Sam often takes part in some environmental protection activities. Sam and Sarah exchanged a conversation about protecting environment at 11pm, October 24, 2022.

Question: Would Sam comment for the case?

Answer:
{{
    "reasoning": "Let's think step by step. Sam is an environmentalist and he has the expertise. Also, he likes to participate in environmental protection activities and likes to talk about environmental protection related topics. Sam is very passionate about environmental protection, so Sam comment on this case.",
    "answer": "Yes"
}}

---

## User prompt
Public memory: {public_memory}
Context: {persona_iss}. {context}

Question:  Would {persona_name} comment for the case?