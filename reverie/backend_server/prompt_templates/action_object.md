## description

let gpt to pick a most relevant object from a list.

parameters:
- action: current action
- objects: objects avaliable

## system prompt

You should pick ONE most relevant object from the objects avaliable, provided by the user.

Here are some examples (you should refer to its content rather than format):

---
Current activity: sleep in bed
Objects available: {bed, easel, closet, painting}
Pick ONE most relevant object from the objects available: bed
---
Current activity: painting
Objects available: {easel, closet, sink, microwave}
Pick ONE most relevant object from the objects available: easel
---
Current activity: cooking
Objects available: {stove, sink, fridge, counter}
Pick ONE most relevant object from the objects available: stove
---
Current activity: watch TV
Objects available: {couch, TV, remote, coffee table}
Pick ONE most relevant object from the objects available: TV
---
Current activity: study
Objects available: {desk, computer, chair, bookshelf}
Pick ONE most relevant object from the objects available: desk
---

## user prompt

Current activity: {action}
Objects avaliable: {objects}
Pick ONE most relevant object from the objects available.