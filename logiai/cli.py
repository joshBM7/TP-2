"""Commande en ligne de commande pour prédire le risque de retard."""

import argparse
import json
import sys
from pathlib import Path

from logiai.config import ALERT_THRESHOLD
from logiai.predict import Predictor


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="logiai-predict")
    parser.add_argument("fichier", help="fichier JSON d'une livraison")
    args = parser.parse_args(argv)

    chemin = Path(args.fichier)
    if not chemin.is_file():
        print(f"Fichier introuvable : {chemin}", file=sys.stderr)
        return 1

    try:
        livraison = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"Lecture du fichier impossible : {exc}", file=sys.stderr)
        return 1

    if not isinstance(livraison, dict):
        print("Le fichier JSON doit contenir un objet livraison.", file=sys.stderr)
        return 1

    try:
        prediction = Predictor().predict(livraison)
    except FileNotFoundError as exc:
        print(
            "Modèle ou données introuvables. Générez les données et entraînez "
            "le modèle, ou définissez LOGIAI_HOME vers leur dossier. "
            f"Détail : {exc}",
            file=sys.stderr,
        )
        return 1

    probabilite = prediction["probabilite_retard"]
    alerte = prediction["alerte"]
    seuil = prediction["seuil"] if prediction.get("seuil") is not None else ALERT_THRESHOLD
    mention = "ALERTE" if alerte else "pas d'alerte"
    print(f"Probabilité de retard : {round(probabilite * 100)} % ({mention})")
    print(f"Seuil d'alerte : {seuil:.0%}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
