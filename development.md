# 开发文档

## llm_function

### 1. 什么是llm_function

llm_function 是一个装饰器，被llm_function装饰的函数会在被调用时会自动地根据参数生成prompt、调用大模型、并从大模型中解析出返回值。实际上，我们可以将大模型看作一个任意的函数，我们想让这个函数计算什么，他就能计算什么。比如在本项目中：

- 给定 `agent的名称、状态`,计算 `agent 当天的计划列表`
- 给定 `一段对于某个活动的描述`,计算`这个活动的主语、谓语、宾语`
- 给定 `agent的描述、公共事件的内容`,计算`agent是否要就此事件发言`
- 给定 `一个Task`,计算`要调用的tools 以及 input`

一个最简单的示例，假如我们已经编写好了 `llm_calculator.md` 这个 prompt模板：
```python
from llm_function import llm_function

@llm_function(is_chat=True, prompt_file="llm_calculator.md")
def llm_calculator(input: str) -> str:
    return {
        "result" : 30 # This is only an example return value. Its format matters, but its content does not.
    }
```

那么我们就可以直接调用这个函数，并传入参数，得到返回值：
```python
val = llm_calculator("What is the result of (3 + 3) * 4 ")["result"]
print(val) # 24
```

这样设计的好处是：

1. 提供了方便的prompt生成、返回值解析，你只需要关注函数的功能、参数本身
2. 提供了错误处理、超时处理、日志、统计等等功能，便于调试
3. 可以单独配置llm，也可以使用统一的配置
4. 减少开发的代码量

### 2. llm_function 的使用

1. 编写prompt

prompt文件采用`markdown`格式，统一的模板如下：

```md
## description

<prompt description>

parameters:
- persona_name: the name of persona
- param2: explanation of param2

## system prompt

You are {persona_name}. You should introduce yourself using the information given by the user.

## user prompt

Information: {param2}
```

格式为：
1. system prompt 需要在 `## system prompt` 小节中指定， 不区分大小写
2. user prompt 需要在 `## user prompt` 小节中指定， 不区分大小写
3. 其余的小节、节自由编写。建议编写 `description` 小节， 介绍prompt的功能以及参数
4. 要插入的参数请使用`{param}`格式，与python的`f-string`的格式相同
5. 要插入的参数的名称要和函数参数名称相同

2. 编写函数

```python
from llm_function import llm_function

@llm_function(
    is_chat=True, 
    prompt_file="llm_calculator.md")
def llm_calculator(input: str) -> str:
    return {
        "result" : 30 # This is only an example return value. Its format matters, but its content does not.
    }
```

```python
from llm_function import llm_function

@llm_function(is_chat=True, prompt_file="llm_calculator.md")
def llm_calculator(input: str) -> str:
    return {
    
}

### 2. llm_function 的使用

#### 2.1. prompt_path

