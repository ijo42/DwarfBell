from datetime import datetime

class Challenge:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.value = data.get('value')
        self.description = data.get('description')
        self.source_url = data.get('source')
        self.attribution = data.get('attribution')
        self.connection_info = data.get('connection_info')
        self.next_id = data.get('next_id')
        self.category = data.get('category')
        self.state = data.get('state')
        self.max_attempts = data.get('max_attempts')
        self.type = data.get('type')
        self.type_data = data.get('type_data')
        self.solves = data.get('solves')
        self.solved_by_me = data.get('solved_by_me')
        self.attempts = data.get('attempts')
        self.files = data.get('files', [])
        self.tags = data.get('tags', [])
        self.hints = data.get('hints', [])
        self.created_at = datetime.now()

    def __repr__(self):
        return f"Challenge(id={self.id}, name='{self.name}', value={self.value}, description='{self.description}')"