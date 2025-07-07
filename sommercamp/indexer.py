# Hier importieren wir die benötigten Softwarebibliotheken.
from datetime import timezone
from os.path import exists, abspath
from json import loads
from shutil import rmtree
from sys import argv
from pyterrier import started, init
from dateutil import parser
# Die PyTerrier-Bibliothek muss zuerst gestartet werden,
# um alle seine Bestandteile importieren zu können.
if not started():
    init()
from pyterrier.index import IterDictIndexer


# Diese Funktion liest jedes Dokument aus der Dokumenten-Sammlung ein
# und gibt es als Python-Objekt zurück.
def parse_date_to_unix(date_str):
    try:
        dt = parser.isoparse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    except Exception as e:
        print(f"⚠️ Ungültiges Datum '{date_str}': {e}")
        return None


def iterate_documents(documents_file):
    with open(documents_file, "rt") as lines:
        for line in lines:
            document = loads(line)
            unix_time = parse_date_to_unix(document.get("date", ""))
            if unix_time is None:
                unix_time = 0  # Default, kannst anpassen
            document["recency"] = str(unix_time)
            print(document.get("url", "Keine URL"))
            yield document


# Diese Funktion indiziert die Dokumente aus der Dokumenten-Sammlung
# und speichert den Index an der angegebenen Stelle ab.
def index(documents_file, index_dir):
    # Erzeuge hier den Indexer von PyTerrier.
    indexer = IterDictIndexer(
        # Der Pfad, wo der Index gespeichert werden soll.
        abspath(index_dir),
        # Die maximale Länge in Buchstaben für jedes Feld im Index.
        # (Die Werte unten sollten locker reichen.)
        meta={
            "docno": 100,
            "url": 1000,
            "title": 1000,
            "text": 100_000,
            "tags": 1000,
            "recency": 10
        },
    )
    # Starte das Indizieren.
    indexer.index(iterate_documents(documents_file))


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    # Lade den Pfad zur Dokumenten-Sammlung aus dem
    # ersten Kommandozeilen-Argument.
    documents_file = argv[1]
    # Lade den Pfad zum Index aus dem zweiten Kommandozeilen-Argument.
    index_dir = argv[2]

    # Wenn du schon vorher etwas indiziert hattest, lösche den alten Index.
    if exists(index_dir):
        rmtree(index_dir)

    # Rufe die Index-Funktion von oben auf.
    index(documents_file, index_dir)


if __name__ == "__main__":
    main()
