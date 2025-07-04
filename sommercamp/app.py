# Hier importieren wir die benötigten Softwarebibliotheken.
from datetime import datetime
from os.path import abspath, exists
from sys import argv
from streamlit import (text_input, header, title, subheader, container, markdown, link_button, divider, set_page_config)
from pyterrier import started, init
# Die PyTerrier-Bibliothek muss zuerst gestartet werden,
# um alle seine Bestandteile importieren zu können.
if not started():
    init()
from pyterrier import IndexFactory
from pyterrier.batchretrieve import BatchRetrieve
from pyterrier.text import get_text
from pyterrier.transformer import TransformerBase


class CustomScorer(TransformerBase):
    def __init__(self):
        super().__init__()

    def transform(self, run):
        if int(run['recency']) >= (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 259200:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            ) * 25
        elif int(run['recency']) >= (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 604800:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            ) * 15
        elif int(run['recency']) >= (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 1209600:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            ) * 10
        elif int(run['recency']) >= (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 2629743:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            ) * 5
        elif int(run['recency']) >= (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds() - 31556926:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            ) * 2
        else:
            run['score'] = run['score'] * (
                run['recency'].astype(float) - 1136070000
            )

        return run


# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir) -> None:

    # Konfiguriere den Titel der Web-App (wird im Browser-Tab angezeigt)
    set_page_config(
        page_title="NewsFlash!",
        layout="centered",
    )

    # Gib der App einen Titel und eine Kurzbeschreibung:
    title("NewsFlash!")
    markdown("News, wann immer, wo immer.")

    # Erstelle ein Text-Feld, mit dem die Suchanfrage (query) 
    # eingegeben werden kann.
    query = text_input(
        label="Suchanfrage",
        placeholder="Suche..."
    )

    # Wenn die Suchanfrage leer ist, dann kannst du nichts suchen.
    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return

    # Öffne den Index.
    index = IndexFactory.of(abspath(index_dir))
    # Initialisiere den Such-Algorithmus. 
    searcher = BatchRetrieve(
        index,
        # Der bekannteste Suchalgorithmus heißt "BM25".
        wmodel="BM25",
        # Und es sollen bis zu 10 Ergebnisse zurückgegeben werden.
        num_results=10,
    )
    # Initialisiere ein Modul, was den Text 
    # der gefundenen Dokumente aus dem Index lädt.
    text_getter = get_text(index, metadata=["url", "title", "text", "tags", "recency"])

    scorer = CustomScorer()
    # Baue nun die "Pipeline" für die Suche zusammen:
    # Zuerst suchen, dann Text abrufen.
    pipeline = searcher >> text_getter >> scorer
    # Führe die Such-Pipeline aus und suche nach der Suchanfrage (query).
    results = pipeline.search(query)

    # Zeige eine Unter-Überschrift vor den Suchergebnissen an.
    divider()
    header("Suchergebnisse")

    # Wenn die Ergebnisliste leer ist, gib einen Hinweis aus.
    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    # Wenn es Suchergebnisse gibt, dann zeige an, wie viele.
    markdown(f"{len(results)} Suchergebnisse.")

    # Gib nun der Reihe nach, alle Suchergebnisse aus.
    for _, row in results.iterrows():
        # Pro Suchergebnis, erstelle eine Box (container).
        with container(border=True):
            # Zeige den Titel der gefundenen Webseite an.
            subheader(row["title"])
            # Speichere den Text in einer Variablen (text).
            text = row["text"]
            # Schneide den Text nach 500 Zeichen ab.
            text = text[:500]
            # Ersetze Zeilenumbrüche durch Leerzeichen.
            text = text.replace("\n", " ")
            # Zeige den Dokument-Text an.
            markdown(text)
            # Gib Nutzern eine Schaltfläche, um die Seite zu öffnen.
            link_button("Seite öffnen", url=row["url"])


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    # Lade den Pfad zum Index aus dem ersten Kommandozeilen-Argument.
    index_dir = argv[1]

    # Wenn es noch keinen Index gibt, kannst du die Suchmaschine nicht starten.
    if not exists(index_dir):
        exit(1)

    # Rufe die App-Funktion von oben auf.
    app(index_dir)


if __name__ == "__main__":
    main()
