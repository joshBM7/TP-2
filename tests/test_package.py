import json
from importlib.metadata import entry_points, version

from logiai import cli


def test_package_installe():
    assert version("logiai")


def test_commande_declaree():
    noms = {point.name for point in entry_points(group="console_scripts")}
    assert "logiai-predict" in noms


def test_cli_fichier_absent(capsys):
    assert cli.main(["fichier_inexistant.json"]) == 1
    assert "Fichier introuvable" in capsys.readouterr().err


def test_cli_affiche_prediction(tmp_path, monkeypatch, capsys):
    chemin = tmp_path / "livraison.json"
    chemin.write_text(json.dumps({"distance_km": 10}), encoding="utf-8")

    class FauxPredictor:
        def predict(self, livraison):
            assert livraison == {"distance_km": 10}
            return {
                "probabilite_retard": 0.87,
                "alerte": True,
                "seuil": 0.4,
            }

    monkeypatch.setattr(cli, "Predictor", FauxPredictor)

    assert cli.main([str(chemin)]) == 0
    assert capsys.readouterr().out.splitlines() == [
        "Probabilité de retard : 87 % (ALERTE)",
        "Seuil d'alerte : 40%",
    ]
