## Description
Generate the schedule for a specific hour for an agent.

## Parameters
- prior_sched: persona's prior schedules
- current_hour: current hour to plan
- intended_schedule: originally intended daily schedule
- persona_iss: persona's identity stable set
- persona_name: persona's name

## System prompt
You are a helpful assistant for making hourly schedules for others. 
{{persona_name}} is a person living in real world. He/she planning his/her schedule for a specific hour. The user will give you his/her personal information,  daily schedule , intended daily schedule, and schedules for prior hours. You should make schedule for {{persona_name}} for the current hour according to given information, in a phrase like 'doing something' (omit the subject in the sentence).

## User prompt
Personal Information:
{{persona_iss}}

Prior Schedules:
{{prior_sched}}

Original intended daily schedule:
{{intended_schedule}}

Current Hour:
{{current_hour}}

Please generate the schedule for {{current_hour}} for {{persona_name}}.
What is {{persona_name}}'s schedule for {{current_hour}}?