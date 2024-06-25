class MemoryNode:
    def __init__(self, Name, s, p, o, description, new_or_old):
      self.name = Name
      self.subject = s
      self.predicate = p
      self.object = o
      self.description = description
      self.new_or_old = new_or_old

    def spo_summary(self):
      return (self.subject, self.predicate, self.object)
  
    def get_description(self):
      return (self.description)
    
    def get_name(self):
      return (self.name)