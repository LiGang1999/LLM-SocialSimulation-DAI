## description

turn a sentence into (subject, predicate, object) .

parameters:
- persona_name: persona's full name
- action: current action description

## system prompt

The user will provide you a sentence that describes an activity. You should turn it into a triple (subject, predicate, object) that describes the activity.

Here are some examples ( you should refer to its content only ):

---
Input: Sam Johnson is eating breakfast. 
Output: (Dolores Murphy, eat, breakfast) 
--- 
Input: Joon Park is brewing coffee.
Output: (Joon Park, brew, coffee)
---
Input: Jane Cook is sleeping. 
Output: (Jane Cook, is, sleep)
---
Input: Michael Bernstein is writing email on a computer. 
Output: (Michael Bernstein, write, email)
---
Input: Percy Liang is teaching students in a classroom. 
Output: (Percy Liang, teach, students)
---
Input: Merrie Morris is running on a treadmill. 
Output: (Merrie Morris, run, treadmill)

## user prompt

{persona_name} is {action}.
