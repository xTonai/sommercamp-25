# Hier importieren wir die benötigten Softwarebibliotheken.
from datetime import datetime
from os.path import abspath, exists
from sys import argv
from streamlit import (
    text_input, header, title, subheader, container,
    markdown, link_button, divider, set_page_config
)
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
        now = datetime.now().timestamp()

        def score_row(row):
            recency = float(row["recency"])
            score = row["score"]

            if recency >= now - 259200:         # letzte 3 Tage
                factor = 25
            elif recency >= now - 604800:       # letzte Woche
                factor = 15
            elif recency >= now - 1209600:      # letzte 2 Wochen
                factor = 10
            elif recency >= now - 2629743:      # letzter Monat
                factor = 5
            elif recency >= now - 31556926:     # letztes Jahr
                factor = 2
            else:
                factor = 1 // 10**9  # alles ältere

            return score * factor

        # Scoring anwenden
        run["score"] = run.apply(score_row, axis=1)

        # Nur Ergebnisse mit Score > 0
        run = run[run["score"] > 0]

        # Sortiere absteigend nach Score
        run = run.sort_values("score", ascending=False)

        return run


# Diese Funktion baut die App für die Suche im gegebenen Index auf.
def app(index_dir) -> None:
    set_page_config(
        page_title="NewsFlash!",
        layout="centered",
    )

    title("NewsFlash!")
    markdown("News, wann immer, wo immer.")

    query = text_input(
        label="Suchanfrage",
        placeholder="Suche..."
    )

    if query == "":
        markdown("Bitte gib eine Suchanfrage ein.")
        return

    index = IndexFactory.of(abspath(index_dir))

    searcher = BatchRetrieve(
        index,
        wmodel="BM25",
        num_results=1000,  # hole mehr Kandidaten
    )

    text_getter = get_text(
        index,
        metadata=["url", "title", "text", "tags", "recency"]
    )
    scorer = CustomScorer()
    pipeline = searcher >> text_getter >> scorer
    results = pipeline.search(query)

    divider()
    header("Suchergebnisse")

    if len(results) == 0:
        markdown("Keine Suchergebnisse.")
        return

    # Zeige maximal 15 Ergebnisse
    max_results = min(len(results), 15)
    markdown(
        f"{max_results} Ergebnisse angezeigt (von {len(results)} gefunden)."
    )

    for _, row in results.head(max_results).iterrows():
        with container(border=True):
            title_text = row["title"] if isinstance(row["title"], str) else (
                "(Kein Titel vorhanden)"
            )
            text = row["text"] if isinstance(row["text"], str) else (
                "(Kein Text verfügbar)"
            )
            url = row["url"] if isinstance(row["url"], str) else "#"

            text = text[:500].replace("\n", " ")

            subheader(title_text)
            markdown(text)
            link_button("Seite öffnen", url=url)


# Die Hauptfunktion, die beim Ausführen der Datei aufgerufen wird.
def main():
    index_dir = argv[1]

    if not exists(index_dir):
        print(f"Index nicht gefunden unter: {index_dir}")
        exit(1)

    app(index_dir)


if __name__ == "__main__":
    main()
