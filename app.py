import json
import logging
import os
import time
from collections import deque
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

MODEL_PATH = os.getenv("MODEL_PATH", "artifacts/model.joblib")
COLUMNS_PATH = os.getenv("COLUMNS_PATH", "artifacts/columns.json")
APP_ENV = os.getenv("APP_ENV", "dev")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


@st.cache_resource
def load_model():
    """Load model and feature columns once per container."""
    model = joblib.load(MODEL_PATH)
    with open(COLUMNS_PATH, "r") as f:
        cols = json.load(f)["features"]
    return model, cols


@st.cache_resource
def init_metrics():
    """Shared metrics across all users/sessions in this container."""
    return {
        "latencies_ms": deque(maxlen=500),
        "request_count": 0,
        "error_count": 0
    }


model, FEATURES = load_model()
metrics = init_metrics()

st.title("Titanic Survival Predictor 🚢")
st.caption(
    f"Environment: `{APP_ENV}` | "
    f"Model: `{Path(MODEL_PATH).name}`"
)

# Input form
col1, col2, col3 = st.columns(3)
with col1:
    pclass = st.selectbox("Passenger Class (Pclass)", [1, 2, 3], index=2)
    age = st.number_input(
        "Age", min_value=0, max_value=100, value=30
    )
    sibsp = st.number_input(
        "Siblings/Spouses (SibSp)", min_value=0, max_value=8, value=0
    )
with col2:
    parch = st.number_input(
        "Parents/Children (Parch)", min_value=0, max_value=6, value=0
    )
    fare = st.number_input(
        "Fare", min_value=0.0, value=7.25, step=0.5
    )
    sex = st.selectbox(
        "Sex", ["male", "female"]
    )
with col3:
    embarked = st.selectbox(
        "Embarked", ["S", "C", "Q"], index=0
    )

# Prediction
if st.button("Predict"):
    start = time.time()
    try:
        row = pd.DataFrame(
            [{
                "Pclass": pclass,
                "Sex": sex,
                "Age": age,
                "SibSp": sibsp,
                "Parch": parch,
                "Fare": fare,
                "Embarked": embarked,
            }]
        )[FEATURES]

        proba = model.predict_proba(row)[0][1]
        pred = int(proba >= 0.5)
        latency = (time.time() - start) * 1000.0

        # Update metrics
        metrics["latencies_ms"].append(latency)
        metrics["request_count"] += 1

        st.success(
            f"Predicted Survived: **{pred}** "
            f"(probability: {proba:.2f})"
        )
        st.write(f"Latency: {latency:.1f} ms")

        logging.info(
            "prediction_ok latency_ms=%.1f proba=%.3f",
            latency,
            proba,
        )

    except Exception as e:
        metrics["error_count"] += 1
        logging.exception("prediction_error")
        st.error(f"Error: {e}")

# Sidebar metrics
st.sidebar.header("Live Metrics")
if metrics["latencies_ms"]:
    p95 = float(np.percentile(metrics["latencies_ms"], 95))
    st.sidebar.write(f"p95 latency: **{p95:.1f} ms**")
    st.sidebar.write(
        f"Total requests: **{metrics['request_count']}**"
    )
    st.sidebar.write(
        f"Errors: **{metrics['error_count']}**"
    )
else:
    st.sidebar.write("No requests yet.")
st.sidebar.caption(
    "For production metrics, also use Azure Monitor & container logs."
)
