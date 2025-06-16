# 假设我们有8个事件
events = ["事件1: ", "事件2: ", "事件3: ", "事件4: ", "事件5: ", "事件6: ", "事件7: ", "事件8: "]

# 从 comment.txt 文件中读取发言内容
with open("comments.txt", "r", encoding="utf-8") as file:
    comments = file.readlines()

# 为每个事件创建一个列表来存储发言
event_comments = {i: [] for i in range(1, 9)}

# 假设每八条发言是同一个人对八个事件的发言
num_people = len(comments) // len(events)

# 分配发言到事件
for i, comment in enumerate(comments):
    event_number = i % len(events) + 1  # 计算事件编号
    event_comments[event_number].append(comment.strip())

# 将结果写入新的文件
with open("output.txt", "w", encoding="utf-8") as output_file:
    for i, event in enumerate(events, 1):
        output_file.write(f"{event}:\n")
        for comment in event_comments[i]:
            output_file.write(f"  - {comment}\n")
        output_file.write("\n")
