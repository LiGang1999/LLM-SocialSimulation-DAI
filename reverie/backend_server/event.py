class Event:
    def __init__(self, event_name, access_list=[], description=[]):
        self.event_name = event_name
        self.public_history = []
        self.access_list = access_list
        self.description = description

    def set_description(self, description):
        self.description = description

    def add_history(self, memory_node):
        self.public_history.append(memory_node)
        if memory_node.get_name() == "public":
            self.description = memory_node.get_description()

    def get_histories(self, name):
        print(name)
        if name in self.access_list:
            # TODO improve access management
            return self.public_history
        else:
            return None

    def get_description(self, name):
        print(name)
        if name in self.access_list:
            return self.description
        else:
            return ""
