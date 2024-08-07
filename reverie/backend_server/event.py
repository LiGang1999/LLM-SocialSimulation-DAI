class Event:
    def __init__(self, name = ""):
        self.public_memory = []
        self.access_name = name
        self.description = ""

    def add_memory(self, memory_node):
        self.public_memory.append(memory_node)
        if memory_node.get_name() == "public":
            self.description = memory_node.get_description()

    def get_memories(self, name):
        print(name)
        if name in self.access_name:
            return self.public_memory
        else:
            return None
        
    def get_desc(self, name):
        print(name)
        if name in self.access_name:
            return self.description
        else:
            return ""