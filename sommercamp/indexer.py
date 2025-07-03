import json
import re


class Indexer():
    def __init__(self, documents):
        self.documents = documents
        with open('data/stopwords.json', "r") as f:
            self.stopwords = json.load(f)
        self.documents_list = []

    def index(self):
        with open(self.documents, "r") as f:
            for line in f:
                document = json.loads(line)
                self.documents_list.append(document)
        for document in self.documents_list:
            text = document["text"]
            text = re.split(r'[\s\t\n]+', text)
            for word in text:
                if word.lower().strip('.,;:!?()"[]{}<>') in self.stopwords:
                    text.remove(word)
                else:
                    text[text.index(word)] = word.lower().strip('.,;:!?()"[]{}<>')
            print(text)


Indexer = Indexer("data/documents.jsonl")
Indexer.index()
