import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path("data/titanic.csv")
ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# Column names
FEATURES = [
    "Pclass", "Sex", "Age", "SibSp",
    "Parch", "Fare", "Embarked"
]
TARGET = "Survived"


def main():
    df = pd.read_csv(DATA_PATH)
    df = df.dropna(subset=[TARGET])

    X = df[FEATURES].copy()
    y = df[TARGET].astype(int)

    num_features = ["Age", "SibSp", "Parch", "Fare", "Pclass"]
    cat_features = ["Sex", "Embarked"]

    num_pipe = Pipeline(
        [("imputer", SimpleImputer(strategy="median"))]
    )
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ohe", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    pre = ColumnTransformer(
        [
            ("num", num_pipe, num_features),
            ("cat", cat_pipe, cat_features),
        ]
    )

    model = LogisticRegression(max_iter=1000)
    clf = Pipeline([("pre", pre), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Test Accuracy: {acc:.3f}")

    joblib.dump(clf, ARTIFACT_DIR / "model.joblib")
    with open(ARTIFACT_DIR / "columns.json", "w") as f:
        json.dump({"features": FEATURES}, f)
    with open(ARTIFACT_DIR / "version.txt", "w") as f:
        f.write("v1\n")


if __name__ == "__main__":
    main()
