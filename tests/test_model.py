from pathlib import Path
import joblib
import pandas as pd


def test_model_predicts():
    model_path = Path("artifacts/model.joblib")
    assert model_path.exists(), (
        "model not found, run `python train.py` first"
    )
    model = joblib.load(model_path)
    row = pd.DataFrame(
        [
            {
                "Pclass": 3,
                "Sex": "male",
                "Age": 30,
                "SibSp": 0,
                "Parch": 0,
                "Fare": 7.25,
                "Embarked": "S",
            }
        ]
    )
    proba = model.predict_proba(row)[0][1]
    assert 0.0 <= proba <= 1.0
