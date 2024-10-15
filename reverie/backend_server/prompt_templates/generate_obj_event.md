## description
describe the state of an object.

## Parameters
- obj_name: object name
- persona_name: persona name
- action: persona action event description

## system prompt
You will be given a sentence that describes an activity on an object. Your task is to generate a sentence that describes the state of a specific object.If the object is not being used, answer "<object_name> is idle".
Here are some examples:
---
Activity: Sam Johnson is eating breakfast at the oven. 
Object: oven 
State: is being heated to cook breakfast.
---
Activity: Michael Bernstein is writing an email at the computer.  
object: computer
State: is being used to write an email.
---
Activity: Tom Kane is washing his face at the sink. 
Object: sink 
State: is running with water.

## user prompt
{{persona_name}} is {{action}}.
describe the state of {{obj_name}}.