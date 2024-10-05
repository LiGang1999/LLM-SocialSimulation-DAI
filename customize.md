# 如何基于本框架进行开发

基于我们的框架进行开发时,需要在不同的文件中进行修改和添加。以下是详细的开发指南:

## 1. Prompt开发

a. 在 `reverie/backend_server/prompt_templates/` 目录下创建新的 `.md` 文件作为prompt模板。例如 `new_prompt.md`:

```markdown
## description

This is a new prompt for [specific purpose].

parameters:
- param1: explanation of param1
- param2: explanation of param2

## system prompt

You are an AI assistant tasked with [specific task].

## human prompt

Given the following information:
{param1}
{param2}

Please [specific instruction].

## ai prompt

I understand. Based on the provided information, I will [specific task].

[Output format or additional instructions]
```

b. 在 `reverie/backend_server/persona/prompt_template/run_gpt_structure.py` 文件中添加新的函数来调用这个prompt:

```python
@llm_function(prompt_file="new_prompt.md", is_chat=True)
def new_prompt_function(param1: str, param2: str) -> Dict[str, Any]:
    return {
        "result": "Example result"  # 实际返回值将由LLM生成
    }
```

## 2. Persona, Workflow, Behavior开发

a. 在 `reverie/backend_server/persona/persona.py` 中创建新的Persona类:

```python
from reverie.backend_server.persona.persona import Persona

class NewPersona(Persona):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 添加新的属性

    def custom_method(self):
        # 实现新的方法
        pass
```

b. 在 `reverie/backend_server/persona/workflow.py` 中为新的Persona类定义工作流:

```python
def new_persona_workflow(persona):
    # 实现新的工作流程
    persona.perceive()
    persona.retrieve()
    persona.reflect()
    persona.plan()
    persona.execute()
    persona.custom_method()  # 调用新增的方法
```

c. 在 `reverie/backend_server/persona/action.py` 中添加新的行为:

```python
def new_behavior(persona):
    # 实现新的行为
    pass
```

d. 如果需要新的记忆模块,在 `reverie/backend_server/persona/memory_structures/` 目录下创建新文件,例如 `new_memory.py`:

```python
class NewMemory:
    def __init__(self):
        self.data = {}

    def add(self, key, value):
        self.data[key] = value

    def retrieve(self, key):
        return self.data.get(key)
```

e. 在 `reverie/backend_server/persona/cognitive_modules/` 目录下修改或添加新的认知模块:

* 修改 `perceive.py`:
```python
def perceive_new(persona):
    # 实现新的感知逻辑
    pass
```

* 修改 `retrieve.py`:
```python
def retrieve_new(persona):
    # 实现新的检索逻辑
    pass
```

* 修改 `reflect.py`:
```python
def reflect(persona):
    # 添加新的反思逻辑
    pass
```

* 修改 `plan.py`:

```python
def plan_dai(persona, retrieved):
   # 实现新的规划逻辑
   pass
```

* 修改 `execute.py`:
```python
def execute_new(persona):
    # 实现新的执行逻辑
    pass
```

## 3. 集成新的Persona

在 `reverie/backend_server/reverie.py` 文件中,修改 `__init__` 方法以支持新的Persona类型:

```python
if sim_config.persona_type == "new_persona":
    self.personas[persona_name] = NewPersona(
        name=persona_name,
        # 其他必要的参数
    )
```

## 4. 地图开发 
在 `reverie/backend_server/maze.py` 文件中,我们可以扩展现有的 `OnlineMaze` 类或创建一个新的类。例如,我们可以创建一个新的 `DynamicMaze` 类:

```python
from reverie.backend_server.maze import OnlineMaze
from reverie.backend_server.utils.logs import L

class DynamicMaze(OnlineMaze):
    def __init__(self, maze_name):
        super().__init__(maze_name)
        self.dynamic_elements = {}
        L.info(f"Created DynamicMaze: {maze_name}")

    def add_dynamic_element(self, element_id, position):
        self.dynamic_elements[element_id] = position
        L.debug(f"Added dynamic element {element_id} at position {position}")

    def move_dynamic_element(self, element_id, new_position):
        if element_id in self.dynamic_elements:
            old_position = self.dynamic_elements[element_id]
            self.dynamic_elements[element_id] = new_position
            L.info(f"Moved element {element_id} from {old_position} to {new_position}")
        else:
            L.warning(f"Attempted to move non-existent element: {element_id}")

    def get_dynamic_elements(self):
        return self.dynamic_elements
```

这个新类添加了动态元素的功能,允许我们在地图中添加和移动元素。

## 5. 后端接口开发 
在 `reverie/backend_server/server.py` 文件中,我们可以添加新的 FastAPI 路由来支持 `DynamicMaze` 的功能:

```python
from fastapi import FastAPI, HTTPException
from reverie.backend_server.maze import DynamicMaze

app = FastAPI()

@app.post("/create_dynamic_maze")
async def create_dynamic_maze(maze_name: str):
    try:
        maze = DynamicMaze(maze_name)
        # 假设我们将maze存储在某个全局变量或数据库中
        return {"message": f"Dynamic maze '{maze_name}' created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add_dynamic_element")
async def add_dynamic_element(maze_name: str, element_id: str, x: int, y: int):
    try:
        maze = get_maze(maze_name)  # 假设有一个函数来获取指定的迷宫
        maze.add_dynamic_element(element_id, (x, y))
        return {"message": f"Dynamic element '{element_id}' added to maze '{maze_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/move_dynamic_element")
async def move_dynamic_element(maze_name: str, element_id: str, new_x: int, new_y: int):
    try:
        maze = get_maze(maze_name)
        maze.move_dynamic_element(element_id, (new_x, new_y))
        return {"message": f"Dynamic element '{element_id}' moved in maze '{maze_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/get_dynamic_elements")
async def get_dynamic_elements(maze_name: str):
    try:
        maze = get_maze(maze_name)
        return {"dynamic_elements": maze.get_dynamic_elements()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

这些新的路由允许我们通过 API 创建动态迷宫、添加动态元素、移动元素和获取所有动态元素。

## 6. 如何使用日志进行调试 
基于我们的框架进行开发时，使用日志进行调试是一个重要的步骤。以下是如何使用日志进行调试的指南：

a. 导入日志模块：
在需要使用日志的文件顶部，添加以下导入语句：

```python
from utils.logs import L
```

b. 使用日志：
在代码中适当的位置添加日志语句。根据信息的重要性和详细程度，选择合适的日志级别：

- 调试信息：
```python
L.debug(f"Debug message: {variable}")
```

- 一般信息：
```python
L.info("Information message")
```

- 警告信息：
```python
L.warning("Warning message")
```

- 错误信息：
```python
L.error("Error message")
```

- 严重错误：
```python
L.critical("Critical error message")
```


通过这些修改和添加,你可以扩展现有的框架,添加新的prompt、persona类型、行为和认知模块，扩展地图功能,添加新的 API 接口,并增强日志记录以便于调试。这些更改使得系统更加灵活,能够处理动态元素,并提供了更好的调试能力。

