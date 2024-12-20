from datetime import datetime

class Challenge:
    def __init__(self, data):
        self.id = data.get('id')
        self.type = data.get('type')
        self.name = data.get('name')
        self.value = data.get('value')
        self.solves = data.get('solves')
        self.solved_by_me = data.get('solved_by_me')
        self.category = data.get('category')
        self.tags = data.get('tags', [])
        self.template = data.get('template')
        self.script = data.get('script')
        self.created_at = datetime.now()

    def __repr__(self):
        return f"Challenge(id={self.id}, type='{self.type}', name='{self.name}', value={self.value}, template='{self.template}', script='{self.script}')"