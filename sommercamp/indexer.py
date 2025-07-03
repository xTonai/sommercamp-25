import json
import re

from sommercamp.annotate import AnnotationService


class Indexer():
    def __init__(self, documents):
        self.documents = documents
        self.documents_list = []

    def index(self):
        with open(self.documents, "r") as f:
            for line in f:
                document = json.loads(line)
                self.documents_list.append(document)
        for document in self.documents_list:
            print(f"Indexing document: {document['docno']}")
            text = re.split(r'[\s\t\n]+', document["text"])
            score = AnnotationService().annotate(text)
            document["score"] = score
            print(f"Document {document['docno']} has score: {score}")


Indexer = Indexer("data/documents.jsonl")
Indexer.index()
