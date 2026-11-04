"""Charge le modèle sauvegardé et prédit pour une livraison."""

import json
import pickle
from pathlib import Path

import joblib
import pandas as pd

from logiai.config import ALERT_THRESHOLD, FEATURES, INFO_PATH, MODEL_PATH


class Predictor:
    def __init__(self, model_path: Path = MODEL_PATH, info_path: Path = INFO_PATH):
        self.model_path = Path(model_path)
        self.info_path = Path(info_path)
        self.model = self._load_model()
        info = {}
        if self.info_path.exists():
            info = json.loads(self.info_path.read_text(encoding="utf-8"))
        self.version = info.get("version", "inconnue")
        self.threshold = info.get("seuil", ALERT_THRESHOLD)

    def _load_model(self):
        if not self.model_path.exists():
            from logiai.train import train

            train()

        try:
            model = joblib.load(self.model_path)
            self._validate_model(model)
        except (
            AttributeError,
            EOFError,
            ImportError,
            ModuleNotFoundError,
            OSError,
            pickle.UnpicklingError,
            TypeError,
            ValueError,
        ):
            from logiai.train import train

            train()
            model = joblib.load(self.model_path)
            self._validate_model(model)
        return model

    @staticmethod
    def _validate_model(model):
        if not callable(getattr(model, "predict_proba", None)):
            raise TypeError("Le modèle chargé ne sait pas calculer predict_proba().")

        exemple = {
            "distance_km": 120.0,
            "poids_kg": 450.0,
            "heure_depart": 17,
            "pluie_mm": 8.0,
            "trafic_index": 7.5,
            "nb_arrets": 4,
            "type_vehicule": "camion",
        }
        probabilites = model.predict_proba(pd.DataFrame([exemple], columns=FEATURES))
        if len(probabilites) != 1 or len(probabilites[0]) < 2:
            raise ValueError("Le modèle doit fournir les probabilités des deux classes.")

    def predict(self, features: dict) -> dict:
        """features : un dictionnaire avec les 7 variables du contrat."""
        df = pd.DataFrame([features], columns=FEATURES)
        proba = float(self.model.predict_proba(df)[0, 1])
        return {
            "probabilite_retard": round(proba, 4),
            "alerte": proba >= self.threshold,
            "seuil": self.threshold,
            "model_version": self.version,
        }
