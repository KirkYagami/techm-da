# Dataflow ML

> **Level:** Intermediate (Python basics assumed)
> **Time:** ~45 minutes
> **Goal:** Train a model locally, then run batch predictions at scale using Apache Beam on Google Cloud Dataflow.

---

## 🖥️ Local vs Cloud — What do I need?

| | Local (DirectRunner) | Cloud (DataflowRunner) |
|---|---|---|
| **GCP account needed?** | ❌ No | ✅ Yes |
| **Cost** | Free | Uses $300 credit (~$1–3/job) |
| **Setup time** | `pip install` only | GCP project + APIs + GCS bucket |
| **Best for** | Learning, testing, all demos in this guide | Production, large datasets |

**Recommendation for students:** Run every step in this guide locally first using `DirectRunner`. Only swap to `DataflowRunner` in Step 5 once the pipeline works end-to-end. All code in Steps 1–4 works with zero GCP setup.

---

---

## What Is Dataflow ML?

Google Cloud Dataflow is a fully managed Apache Beam runner. When combined with ML, it lets you:

- Run **batch inference** on millions of records in parallel
- Deploy **streaming predictions** on live data (e.g., fraud detection)
- Use models from **TensorFlow, PyTorch, scikit-learn, or Hugging Face**

The core idea: your ML model becomes a **transform** in a data pipeline.

```
Input Data  →  [Preprocess]  →  [RunInference]  →  [Postprocess]  →  Output
```

---

## Prerequisites

```bash
# Install required packages
pip install apache-beam[gcp] \
            apache-beam[ml] \
            scikit-learn \
            pandas
```

Make sure you have a Google Cloud project with Dataflow API enabled, or run locally with the DirectRunner for this demo.

---

## Step 1 — Train & Save a Simple Model

We'll train a small scikit-learn classifier and save it so Beam can load it.

```python
# train_model.py
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Load dataset
iris = load_iris()
X, y = iris.data, iris.target

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# Train
model = LogisticRegression(max_iter=200)
model.fit(X_train, y_train)

print(f"Test accuracy: {model.score(X_test, y_test):.3f}")

# Save model + scaler together
artifact = {"model": model, "scaler": scaler}
with open("iris_model.pkl", "wb") as f:
    pickle.dump(artifact, f)

print("Model saved to iris_model.pkl")
```

Run it:

```bash
python train_model.py
# Test accuracy: 0.967
# Model saved to iris_model.pkl
```

---

## Step 2 — Prepare Inference Data

Create a CSV of records to run predictions on.

```python
# generate_data.py
import pandas as pd
import numpy as np

# Simulate 1000 flower measurement records
np.random.seed(0)
df = pd.DataFrame({
    "sepal_length": np.random.uniform(4.0, 8.0, 1000),
    "sepal_width":  np.random.uniform(2.0, 4.5, 1000),
    "petal_length": np.random.uniform(1.0, 7.0, 1000),
    "petal_width":  np.random.uniform(0.1, 2.5, 1000),
})
df.to_csv("flowers_to_predict.csv", index=False)
print("Generated 1000 records → flowers_to_predict.csv")
```

---

## Step 3 — Write the Beam ML Pipeline

This is the core of Dataflow ML. We define transforms that:
1. Read records
2. Convert to feature vectors
3. Run model inference
4. Write results

```python
# pipeline_ml.py
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
import pickle
import pandas as pd
import numpy as np
import json

# ── Custom DoFn: loads model once per worker, predicts per element ──
class PredictSpecies(beam.DoFn):
    """
    A Beam DoFn that loads the pickled model on startup
    and produces a prediction for each input row.
    """

    def __init__(self, model_path: str):
        self.model_path = model_path

    def setup(self):
        # setup() is called once per worker — ideal for model loading
        with open(self.model_path, "rb") as f:
            artifact = pickle.load(f)
        self.model  = artifact["model"]
        self.scaler = artifact["scaler"]
        self.labels = ["setosa", "versicolor", "virginica"]

    def process(self, element):
        # element is a single CSV line (string)
        parts = element.strip().split(",")
        if parts[0] == "sepal_length":
            return  # skip header

        features = np.array([[float(p) for p in parts]])
        features_scaled = self.scaler.transform(features)

        pred_index = self.model.predict(features_scaled)[0]
        confidence = self.model.predict_proba(features_scaled)[0].max()

        result = {
            "sepal_length": parts[0],
            "sepal_width":  parts[1],
            "petal_length": parts[2],
            "petal_width":  parts[3],
            "predicted_species": self.labels[pred_index],
            "confidence": round(float(confidence), 4),
        }
        yield json.dumps(result)


# ── Pipeline definition ──
def run():
    options = PipelineOptions(
        runner="DirectRunner",   # Change to "DataflowRunner" for GCP
        # project="your-gcp-project",
        # region="us-central1",
        # temp_location="gs://your-bucket/temp",
    )

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read CSV"        >> beam.io.ReadFromText("flowers_to_predict.csv")
            | "Run Inference"   >> beam.ParDo(PredictSpecies("iris_model.pkl"))
            | "Write Results"   >> beam.io.WriteToText(
                                        "predictions_output",
                                        file_name_suffix=".jsonl"
                                    )
        )

    print("Pipeline complete! Check predictions_output-*.jsonl")


if __name__ == "__main__":
    run()
```

Run the pipeline:

```bash
python pipeline_ml.py
```

---

## Step 4 — Inspect the Output

```python
# inspect_results.py
import json

with open("predictions_output-00000-of-00001.jsonl") as f:
    lines = f.readlines()

results = [json.loads(l) for l in lines]

# Show first 5
for r in results[:5]:
    print(f"  [{r['predicted_species']:12}] confidence={r['confidence']}  "
          f"petal_length={r['petal_length']}")
```

Example output:

```
  [virginica   ] confidence=0.9821  petal_length=6.31
  [setosa      ] confidence=0.9994  petal_length=1.47
  [versicolor  ] confidence=0.7813  petal_length=4.02
```

---

## Step 5 — Scale to Google Cloud Dataflow

To run the same pipeline on millions of rows across many workers, change two things:

```python
options = PipelineOptions(
    runner="DataflowRunner",
    project="your-gcp-project-id",
    region="us-central1",
    temp_location="gs://your-bucket/temp",
    staging_location="gs://your-bucket/staging",
    job_name="iris-inference-demo",
    num_workers=4,
    machine_type="n1-standard-4",
)
```

And swap file paths for GCS paths:

```python
| "Read CSV"      >> beam.io.ReadFromText("gs://your-bucket/flowers.csv")
| "Write Results" >> beam.io.WriteToText("gs://your-bucket/output/predictions")
```

Dataflow will automatically:
- Spin up workers
- Distribute the data
- Run inference in parallel
- Shut down and bill only for what you used

---

## Key Concepts Recap

| Concept | What it does |
|---|---|
| `beam.DoFn` | A single transform unit; `setup()` runs once per worker |
| `beam.ParDo` | Applies a DoFn in parallel across all elements |
| `DirectRunner` | Runs locally for testing |
| `DataflowRunner` | Runs on GCP at scale |
| `setup()` method | Perfect place to load ML models — avoids reloading per row |

---

## Common Mistakes to Avoid

- **Loading the model inside `process()`** — this reloads the model for every single row. Always use `setup()`.
- **Not handling the CSV header** — check for header rows and skip them.
- **Forgetting to apply the same scaler** used during training — mismatched scaling destroys accuracy.

---

## What to Try Next

- Swap scikit-learn for a TensorFlow `SavedModel` — Beam's `RunInference` transform supports it natively
- Add a streaming source (Pub/Sub) for real-time predictions
- Use `apache_beam.ml.inference.base.RunInference` for production-grade inference with batching built in
