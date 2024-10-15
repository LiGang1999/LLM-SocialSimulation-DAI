class Event:
    def __init__(self, event_id, access_list=[], description=[]):
        self.event_id = event_id
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
        if name in self.access_list or len(self.access_list) == 0:
            # TODO improve access management
            return self.public_history
        else:
            return None

    def get_description(self, name):
        print(name)
        if name in self.access_list or len(self.access_list) == 0:
            return self.description
        else:
            return ""
