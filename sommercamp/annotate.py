import json


class AnnotationService():
    def __init__(self):
        self.sentiws = 'data/sentiws.json'
        self.sentimental_value = 0

    def annotate(self, text: list):
        with open(self.sentiws, 'r', encoding='utf-8') as f:
            sentiws = json.load(f)
            for word in text:
                if word in sentiws:
                    self.sentimental_value += sentiws[word]
        return self.sentimental_value
