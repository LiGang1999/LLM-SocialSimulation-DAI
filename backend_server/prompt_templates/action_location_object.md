## Description
Determine for an agent the next place to go.

## Parameters
- persona_name: persona name
- curr_area: persona's current area ( unused )
- action_sector: persona's current sector
- arenas: target_sector's all arenas
- large_action: persona's current activity ( coarse-grained )
- small_action: persona's current activity ( fine-grained )

## System Prompt
You are {{persona_name}}. You should determine your next place to go or stay ,based on your current activities and surrounding information. You should stay in current area if the actions can be done here. You should NEVER go to other people's rooms if not necessary.
You will be given your action position, map information, and your activities. You must choose one place to go(or stay at) from given list.

## User Prompt
You are going to {{action_sector}}.
{{action_sector}} contains following areas: {{arenas}}.
You are {{large_action}}. For {{small_action}}, which area should you go to or stay at?