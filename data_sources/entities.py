import json


class EntityIntake:
    def __init__(self):
        pass
    
    def load_entities(self):
        with open("entities.json", "r") as f:
            entities_data = json.load(f)

            return entities_data["entities"]
