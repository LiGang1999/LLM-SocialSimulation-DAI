## Description

prompt to generatea location (sector) for an agent's current task.

## Parameters

- persona_name: persona name
- all_sectors: all sectors of the maze
- living_sector: persona's living sector
- living_sector_arenas: all arenas of the persona's living secotr
- cur_sector: persona's current sector
- cur_sector_arenas:  all arenas of the persona's current secotr
- cur_action_coarse: description of the current persona's action ( coarse-grained )
- cur_action_fine: description of the current persona's action ( fine-grained )
- daily_plan_req: plan related

## system prompt

You should decide for {persona_name} which appropriate area to stay or go for a task at hand.
Stay in the current area if the activity can be done here. Only go out if the activity needs to take place in another place.
You will be given information about {persona_name}'s current area, living area, and all the avaliable area options.
You will be given the description of the task, and {persona_name}'s daily plan.
You must choose one area from the given options.


## user prompt

{persona_name} lives in {living_sector} that has {living_sector_arenas}.
{persona_name} is currently in {cur_sector} that has {cur_sector_arenas}.

{daily_plan_req}.

{persona_name} is {cur_action_coarse}.For {cur_action_fine}, choose one area from these given options that {persona_name} should stay at or go to: {all_sectors}