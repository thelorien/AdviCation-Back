class Subject():

    def __init__(self, id, name, description) -> None:
        self.id = id
        self.name = name
        self.description = description

    def to_JSON(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
        }


class SubjectJoin():
    def __init__(self, name, description) -> None:
        self.name = name
        self.description = description

    def to_JSON(self):
        return {
            'name': self.name,
            'description': self.description,
        }
