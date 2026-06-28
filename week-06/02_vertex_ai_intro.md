# Vertex AI: A Practitioner's Guide for Beginners
### Professional Training Program — Lecture Notes

---

> **NOTE:** In several years of working with AI platforms, the most expensive mistake I've seen teams make isn't a bad model — it's building a brilliant model and having no coherent system around it. Vertex AI exists to prevent exactly that. By the end of these notes, you'll understand not just *what* each service does, but *why* it was built and *when* you'll reach for it.

---

## Table of Contents

1. [Vertex AI Services Architecture](#1-vertex-ai-services-architecture)
   - [Vertex AI Overview](#11-vertex-ai-overview)
   - [Vertex AI Studio](#12-vertex-ai-studio)
   - [Model Garden](#13-model-garden)
   - [Notebooks: Colab Enterprise and Workbench](#14-notebooks-colab-enterprise-and-workbench)
2. [Vertex AI Data](#2-vertex-ai-data)
   - [Datasets](#21-datasets)
3. [Vertex AI Model Development](#3-vertex-ai-model-development)
   - [Model Training](#31-model-training)
   - [AutoML](#32-automl)
4. [Vertex AI Testing](#4-vertex-ai-testing)
   - [Experiments](#41-experiments)
   - [Logs, Metrics, and Artifacts](#42-logs-metrics-and-artifacts)
   - [Metadata](#43-metadata)
   - [Model Registry](#44-model-registry)
5. [Vertex AI Model Deployment and Use](#5-vertex-ai-model-deployment-and-use)
   - [Online Prediction](#51-online-prediction)
   - [Batch Predictions](#52-batch-predictions)
6. [Vertex AI Cost Management](#6-vertex-ai-cost-management)
   - [Cost Considerations](#61-cost-considerations)
7. [Vertex AI Security Controls](#7-vertex-ai-security-controls)
   - [Security Considerations](#71-security-considerations)
8. [Summary / Quick Reference](#8-summary--quick-reference)

---

## 1. Vertex AI Services Architecture

Before we go feature by feature, let's establish the big picture — because without it, individual tools look like scattered puzzle pieces.

Machine learning projects used to be brutally fragmented. Your data scientists would wrangle data in one tool, train a model in another, hand it off to engineers who deployed it in a third system, and then nobody quite owned the monitoring. Bugs were nobody's fault and everybody's problem.

**Vertex AI** is Google Cloud's answer to that chaos. It's a unified, end-to-end machine learning platform that brings together every stage of the ML lifecycle — from raw data to a live, monitored model — into a single environment with a consistent set of tools, permissions, and billing.

Think of it like a well-designed kitchen versus a collection of mismatched appliances. The individual components still matter, but the system is designed to work together.

> **Important 2026 context:** Google rebranded Vertex AI to *Gemini Enterprise Agent Platform* in April 2026, though the underlying ML services (Pipelines, Model Registry, Training, Prediction, etc.) kept their names. Throughout these notes, we'll use "Vertex AI" as most practitioners still do — and because the concepts map directly to what you'll encounter in documentation and on the job.

---

### 1.1 Vertex AI Overview

At its core, Vertex AI is organized around the idea of the **ML lifecycle** — the repeatable process every machine learning project goes through:

```
Collect Data → Prepare Data → Train Model → Evaluate → Deploy → Monitor → Retrain
      ↑                                                                        |
      └────────────────────────────────────────────────────────────────────────┘
```

Every service in Vertex AI maps to one or more phases of this cycle. No phase is optional in production — teams that skip evaluation or skip monitoring almost always regret it within three months.

Vertex AI sits on Google Cloud Platform (GCP) alongside services you may already know — BigQuery for data warehousing, Cloud Storage for files, and IAM for access control. Critically, Vertex AI integrates natively with all of them, which eliminates entire categories of data-pipeline headaches.

**Why this matters for you:** You don't need to set up Kubernetes clusters or manage GPU drivers. Vertex AI provisions the infrastructure you need and tears it down when you're done. You pay for the compute you actually use.

---

### 1.2 Vertex AI Studio

**Vertex AI Studio** is the fastest on-ramp to working with AI on Google Cloud. It's a browser-based interface — no code required — where you can immediately begin experimenting with Google's foundation models (like Gemini) and your own custom models.

Think of it as the "playground" of Vertex AI. You show up, type a prompt, and see a response. But it's a professional-grade playground with real capabilities.

Here's what makes Studio valuable in practice:

**Prompt design and testing.** You can write, iterate on, and compare prompts side by side. Studio stores versions of your prompts, which is more valuable than it sounds — it means you can roll back a prompt that degraded performance, just like rolling back code. The Prompt Optimizer, now generally available, can even suggest improved prompts automatically.

**Model comparison.** Need to know whether Gemini 2.5 Flash or Gemini 2.5 Pro is better for your specific use case? Studio lets you run both on the same input and compare outputs and costs simultaneously.

**Tuning and customization.** Studio is where you kick off fine-tuning jobs — the process of taking a pre-trained foundation model and training it further on your company's specific data. We'll discuss this more in Section 3.

> **Practitioner warning:** Studio is a great starting point, but resist the temptation to stay there forever. The prompts you craft in Studio's UI need to eventually live in code — versioned, tested, and deployed properly. The Studio-to-production gap is where many pilots die.

---

### 1.3 Model Garden

**Model Garden** is exactly what it sounds like: a curated library of AI models you can browse, test, and deploy directly from Vertex AI. As of mid-2026, it contains over 200 models from multiple sources.

This is genuinely significant. In the early days of ML, if you wanted to use a state-of-the-art natural language model, you'd spend weeks just figuring out how to run it. Model Garden collapses that to minutes.

The models available fall into three broad categories:

| Source | Examples | Best For |
|---|---|---|
| Google's own models | Gemini 2.5 Pro/Flash, Gemma 3, Imagen 4, Veo 3 | Multimodal tasks, text, images, video |
| Third-party partners | Anthropic Claude, Mistral, DeepSeek-R1 | Model comparison, specialized domains |
| Open-source community | Llama 4, Qwen 3, Gemma 3n | Fine-tuning, self-hosting, research |

For each model, Garden provides a consistent experience: you can test it interactively, view pricing, see deployment options (managed API versus self-hosted), and launch fine-tuning jobs if supported.

**The self-hosted versus managed API distinction matters for cost.** A managed API means Google runs the model and you pay per token or per request — simple, but potentially expensive at scale. Self-hosted means you deploy the model on your own VM/GPU and pay for the compute — more complex, but often cheaper for high-volume workloads.

> **Practitioner insight:** Don't automatically reach for the biggest model. In my experience, Gemini 2.5 Flash solves 80% of real business problems at a fraction of the cost of 2.5 Pro. Always establish a performance baseline with the smaller model before upgrading.

---

### 1.4 Notebooks: Colab Enterprise and Workbench

If Vertex AI Studio is the playground, **notebooks** are the workshop. This is where data scientists and ML engineers actually write code, explore datasets, build features, and run experiments.

Vertex AI offers two notebook environments:

**Colab Enterprise** is Google's managed version of Colab (the same environment behind Google Colab, which you may already know from tutorials). It lives directly in your Google Cloud project, meaning it has native access to BigQuery, Cloud Storage, and all other GCP services without any extra authentication setup. You can also write SQL queries directly in notebook cells (a recently added feature), which is a quality-of-life improvement that saves real time. It's excellent for collaborative, exploratory work.

**Vertex AI Workbench** is a more configurable Jupyter-based environment designed for production-grade workflows. It supports custom machine types (choose your CPU, RAM, and GPU), private networking, and integration with enterprise security controls. If you're working on a sensitive project with strict data residency requirements, Workbench gives you the control you need.

```
Colab Enterprise          Workbench
──────────────────        ──────────────────────
Great for:                Great for:
• Exploration             • Production pipelines
• Collaboration           • Custom hardware configs
• Quick iteration         • Strict security policies
• Learning               • Long-running jobs
```

Both environments are pre-integrated with the Vertex AI Python SDK, BigQuery connectors, and popular ML frameworks like TensorFlow, PyTorch, and scikit-learn. You don't waste an hour on setup — you get to the actual work.

> **Practitioner tip:** Always shut down notebook instances when you're not using them. An idle Workbench instance costs the same as an active one. I've seen teams accumulate hundreds of dollars per month in forgotten notebook charges.

---

## 2. Vertex AI Data

### 2.1 Datasets

You cannot build a good model without good data. This sounds obvious, but the industry consistently underestimates data work. In real projects, I've seen teams spend 70-80% of their time on data preparation — not model building.

A **Vertex AI Dataset** is a managed, structured container for your training data. Rather than scattering CSV files across Cloud Storage buckets and losing track of which version was used for which model, a managed dataset gives you a central, auditable record.

**Why managed datasets matter:** When a model underperforms three months after deployment, your first question is "has the training data changed?" If your data isn't tracked with your model, you can't answer that question. Managed datasets create that link automatically.

Vertex AI supports several dataset types:

**Tabular datasets** contain rows and columns — think spreadsheets, database exports, or CSV files. This is the data type most business AI projects start with: customer records, transaction logs, product attributes.

**Image datasets** contain labeled images for computer vision tasks. You might have thousands of product photos labeled as "defective" or "acceptable" for a quality-control system.

**Text datasets** contain labeled text samples for natural language tasks — customer reviews labeled by sentiment, support tickets labeled by category, and so on.

**Video datasets** and **multimodal datasets** (newly available in preview) extend these capabilities to moving images and mixed-format content.

**Data splitting** is a critical concept you'll encounter immediately. Vertex AI automatically divides your dataset into three portions:

```
Your Full Dataset
├── Training set (~80%)    → The model "studies" this
├── Validation set (~10%)  → Used to tune model settings during training
└── Test set (~10%)        → Used ONLY at the end to evaluate final performance
```

The test set is sacred. If you evaluate your model on data it's already "seen" in any way, you'll get falsely optimistic results. Vertex AI enforces this separation for you, but you should understand why it exists.

> **Practitioner warning:** The most common data mistake I see from beginners is **class imbalance**. If 95% of your examples are "normal" and 5% are "fraud," a model can achieve 95% accuracy by always predicting "normal." That's useless. When building datasets, aim for roughly equal representation of each category. If your real data is imbalanced, ask about techniques like oversampling — but first, just make sure your dataset is as balanced as possible.

**A note on data quality over quantity.** Vertex AI's AutoML documentation suggests aiming for at least 1,000 labeled examples per category. But 1,000 high-quality, accurately labeled examples beats 10,000 hastily labeled ones every time. Data labeling is painstaking work — Vertex AI even offers a human-labeling service if you need it — but it's the investment that makes everything else possible.

---

## 3. Vertex AI Model Development

### 3.1 Model Training

**Training** is the process of taking your dataset and using it to configure a model's internal parameters — essentially, teaching the model to recognize patterns. In Vertex AI, training is a **managed service**: you define what you want to train and on what data, and Google Cloud handles provisioning the compute, running the job, and shutting things down when complete.

There are two fundamental approaches to training on Vertex AI:

**AutoML** — you bring data, Vertex AI figures out the rest (covered in the next section).

**Custom training** — you bring data *and* code. Your training script can use any framework: TensorFlow, PyTorch, scikit-learn, XGBoost. Vertex AI runs that script on the infrastructure you specify, including GPU and TPU accelerators for large-scale jobs.

Custom training is more powerful but requires more ML expertise. You're responsible for the model architecture, the training loop, and hyperparameter choices. Vertex AI handles the infrastructure so you can focus on the ML.

```python
# A simplified example of launching a custom training job via the Python SDK
from google.cloud import aiplatform

aiplatform.init(project="my-project", location="us-central1")

job = aiplatform.CustomTrainingJob(
    display_name="churn-model-v2",
    script_path="trainer/task.py",   # Your training code
    container_uri="us-docker.pkg.dev/vertex-ai/training/pytorch-gpu.2-1:latest",
    requirements=["scikit-learn", "pandas"],
)

model = job.run(
    dataset=my_dataset,
    replica_count=1,
    machine_type="n1-standard-8",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
)
```

Vertex AI supports **distributed training** for very large models — spreading the work across multiple machines — and **hyperparameter tuning** via Vertex AI Vizier, which systematically searches for the best combination of training settings.

> **Practitioner note:** GPU time is the most expensive line on your Vertex AI bill. Always run a small "sanity check" job on cheap CPU hardware to make sure your training script works before launching an expensive GPU run. I can't count how many GPU-hours I've seen burned on code that had a typo in the last line.

---

### 3.2 AutoML

**AutoML** (Automated Machine Learning) is one of Vertex AI's most powerful ideas, and it's often misunderstood.

Here's the analogy I use: building a machine learning model from scratch is like building a car from raw metal. Custom training is like assembling a car from parts — you still need to know what you're doing. AutoML is like ordering a car to your specifications — you describe what you need, and a highly automated system figures out the engineering.

Specifically, AutoML handles the parts of ML that are tedious even for experts: trying multiple algorithms, tuning hyperparameters, preprocessing your data appropriately, and selecting the best resulting model. You provide labeled data and tell it what you want to predict. It does the rest.

**What AutoML can train:**

| Data Type | Task | Example |
|---|---|---|
| Tabular | Classification | "Will this customer churn: yes/no?" |
| Tabular | Regression | "What price will this house sell for?" |
| Tabular | Forecasting | "How many units will we sell next month?" |
| Image | Classification | "Is this photo a cat or a dog?" |
| Image | Object Detection | "Where are the defects in this image?" |
| Text | Classification | "Is this review positive or negative?" |
| Video | Classification | "Is this clip an action scene or dialogue?" |

**The AutoML workflow always follows the same steps:**

1. Upload your dataset to a Vertex AI managed dataset
2. Select your target column (what you want to predict)
3. Set a training budget (in node-hours — this directly controls cost)
4. Click "Train" and wait (hours, not days)
5. Review evaluation metrics
6. Deploy if satisfied

```python
# AutoML example: training a customer churn model
from google.cloud import aiplatform as ai

ai.init(project="my-project", location="us-central1")

dataset = ai.TabularDataset.create(
    display_name="customer-churn",
    bq_source="bq://my-project.dataset.customers",
)

job = ai.AutoMLTabularTrainingJob(
    display_name="churn-model",
    optimization_prediction_type="classification",
)

model = job.run(
    dataset=dataset,
    target_column="churned",
    budget_milli_node_hours=1000,  # 1 node-hour
)
```

**When to choose AutoML vs. Custom Training:**

| Situation | Recommendation |
|---|---|
| You have labeled data and need results fast | AutoML |
| You don't have deep ML expertise on your team | AutoML |
| You need a baseline to compare against | AutoML first |
| You need a specific algorithm (e.g., XGBoost for compliance reasons) | Custom Training |
| You need full control over the training process | Custom Training |
| You're working with proprietary architectures | Custom Training |

> **Practitioner insight:** AutoML is not "cheating." It uses the same neural architecture search and ensembling techniques that world-class ML teams use manually. The models it produces are genuinely good. Many production systems at well-known companies run on AutoML models. Use it when it fits — don't let ego push you toward complexity you don't need.

---

## 4. Vertex AI Testing

Testing in ML is different from testing in software engineering, and this section is often where beginners feel the most lost. In traditional software, a test either passes or fails. In ML, you're evaluating *degree of correctness* and watching for *things that change over time*.

### 4.1 Experiments

**Vertex AI Experiments** is a tracking system for your ML trials. Here's why you need it.

Imagine you spend two weeks trying different training approaches. You change the learning rate, try two different model architectures, add some new features to your dataset, and tweak the training duration. After all that, you have a model that performs well — but can you remember exactly which combination of choices produced it? Probably not.

Experiments solves this. Every training run is logged as an **experiment run**, capturing the parameters you chose and the metrics that resulted. The "experiment" is the container (think: "churn-model-project"), and each "run" is a specific attempt within it.

```
Experiment: "customer-churn-q3"
├── Run 001: learning_rate=0.01, epochs=10  → AUC: 0.82
├── Run 002: learning_rate=0.001, epochs=20 → AUC: 0.87
├── Run 003: learning_rate=0.001, epochs=30 → AUC: 0.89  ← best
└── Run 004: learning_rate=0.0001, epochs=30 → AUC: 0.85
```

You can then compare runs visually in the Vertex AI console or programmatically through the SDK. This turns the otherwise chaotic process of model development into a reproducible, auditable record.

**You do not need to run training on Vertex AI to use Experiments.** You can log runs from any Python script that can authenticate to Google Cloud. Teams often use Experiments to track local experiments as well as cloud ones.

> **Practitioner tip:** Log *everything* — not just accuracy metrics but also training time, machine type, dataset version, and even cost estimates. The model that achieves 89% AUC in 3 hours on a $10 budget is often more valuable in practice than 90% AUC achieved in 20 hours at $150.

---

### 4.2 Logs, Metrics, and Artifacts

When a model trains or when a deployed model serves predictions, it generates three kinds of outputs: **logs**, **metrics**, and **artifacts**. Understanding the difference is essential.

**Logs** are timestamped records of events — what happened, when, and sometimes why. A log might say "Training job started at 14:32:07" or "Warning: 4% of rows dropped due to missing values." Logs are your debugging trail. In Vertex AI, logs flow into Google Cloud Logging, where you can search, filter, and set alerts.

**Metrics** are quantitative measurements of performance. During training, metrics might include training loss, validation accuracy, and AUC-ROC. After deployment, metrics shift to latency, throughput, and prediction drift. Metrics tell you *how well* something is working, while logs tell you *what happened*.

**Artifacts** are files produced by an ML pipeline: the trained model weights, evaluation reports, data splits, and so on. Vertex AI tracks these artifacts in its **ML Metadata** store (covered next), so you know exactly which artifact came from which training run.

Think of it this way: if you're a chef, the dish is the artifact, the cooking time and temperature are the metrics, and your notes scribbled during cooking are the logs.

---

### 4.3 Metadata

**Vertex ML Metadata** is the "paper trail" of your entire ML system. It automatically records which datasets produced which models, which models were deployed to which endpoints, and what parameters were used at each step.

Why does this matter so much? Consider a scenario any seasoned ML practitioner has lived through: a model that's been in production for four months suddenly starts making worse predictions. You need to investigate. The questions you'll ask are: Has the training data changed? Did something change in the preprocessing pipeline? Are we using the same feature engineering as when the model was trained?

Without metadata tracking, answering these questions means digging through old emails, Slack messages, and memory. With ML Metadata, every artifact and execution in your pipeline is linked — you can trace backwards from a deployed model to the exact dataset version and training code that created it.

Vertex AI populates metadata automatically when you use managed services like Pipelines and Training. For custom scripts, you add a few lines of SDK code to register your own artifacts and executions.

> **This is foundational for regulated industries.** Healthcare, finance, and insurance applications often require demonstrating *exactly* how a model was built — which data it saw, how it was evaluated, and who approved it for deployment. ML Metadata provides the audit trail that makes this possible.

---

### 4.4 Model Registry

The **Vertex AI Model Registry** is the centralized catalog for all your trained models. Think of it as a library, but instead of books, it stores model files — along with all the metadata that makes those models understandable and deployable.

Every model in the Registry has versions. Version 1 is your first production model. Version 2 is the one trained after you collected more data. Version 3 is the experimental variant you haven't approved for production yet. The Registry keeps all of them organized and accessible.

This matters for several practical reasons:

**Deployment clarity.** When you deploy a model to a prediction endpoint, you deploy a *specific version* from the Registry. Engineers can see exactly which version is live, and rolling back to a previous version is a matter of clicking a button rather than hunting down old files.

**Collaboration.** Data scientists can upload models they've trained in notebooks. ML engineers can then review them, add evaluation metadata, and promote them to production. The Registry is the handoff point.

**Governance.** In enterprise settings, you often need approval workflows before a model can serve live traffic. The Registry supports staging models through states like "Staging," "Champion," and "Archived," creating a clear governance structure.

```
Model Registry: "customer-churn-classifier"
├── v1 (Archived)  — Trained Jan 2025, AUC: 0.82, Deployed Jan-Mar 2025
├── v2 (Champion)  — Trained Apr 2025, AUC: 0.89, Currently in production
└── v3 (Staging)   — Trained Jun 2025, AUC: 0.91, Awaiting approval
```

> **Practitioner warning:** Never deploy a model by pointing to a raw file path in Cloud Storage. Always go through the Registry. Teams that skip this step consistently run into situations where nobody knows which model version is in production, or the file gets overwritten accidentally.

---

## 5. Vertex AI Model Deployment and Use

### 5.1 Online Prediction

**Online prediction** is what most people picture when they imagine a "deployed AI model": a live service that accepts a request, runs it through the model, and returns a response — fast, in real time.

When you deploy a model to a Vertex AI **endpoint**, the platform:
1. Containerizes your model automatically (or uses your custom container)
2. Spins up the specified machine type(s) to serve it
3. Puts a load balancer in front to handle traffic
4. Sets up autoscaling to add more machines when traffic increases
5. Gives you an HTTPS URL you can call from any application

From your application's perspective, calling the model is as simple as making an API call:

```python
from google.cloud import aiplatform

endpoint = aiplatform.Endpoint("projects/my-project/locations/us-central1/endpoints/123")

prediction = endpoint.predict(
    instances=[{"age": 35, "tenure_months": 24, "plan": "premium"}]
)
print(prediction.predictions)
# → [{"churned": 0, "churn_probability": 0.12}]
```

**Traffic splitting** is a particularly powerful feature. You can deploy two model versions to the same endpoint and split traffic between them — for example, 90% to your proven version 2 and 10% to your experimental version 3. This lets you safely test new models on real traffic before fully committing to them.

**What does "online" cost?** Online prediction endpoints charge **by the hour** — whether or not they're receiving requests. This is the most important cost nuance in Vertex AI deployment. An endpoint sitting idle at 3 AM costs the same as one at peak load. Starting price is around $0.06/node-hour for basic hardware.

> **Practitioner warning:** The single most common source of runaway Vertex AI costs I encounter is forgotten development endpoints. You spun up an endpoint to test something, got pulled into another meeting, and it sat there for three weeks billing you every hour. Set up billing alerts, and build a habit of cleaning up endpoints when experiments conclude.

---

### 5.2 Batch Predictions

Not every prediction needs to happen in real time. If you're scoring 5 million customer records overnight, or running monthly churn predictions, you don't need a live endpoint — you need **batch prediction**.

Here's the analogy: online prediction is like a restaurant that serves customers one table at a time as they arrive. Batch prediction is like a catering company that prepares 10,000 meals at once for a scheduled event.

Batch prediction in Vertex AI works like this:

1. You store your input data in Cloud Storage or BigQuery (typically thousands to millions of records)
2. You submit a batch prediction job referencing a model in your Registry
3. Vertex AI provisions the compute, processes all records, and writes results back to Cloud Storage or BigQuery
4. The compute shuts down completely — you pay only for the duration of the job

```python
batch_job = model.batch_predict(
    job_display_name="monthly-churn-scoring",
    gcs_source=["gs://my-bucket/customers-july-2026.jsonl"],
    gcs_destination_prefix="gs://my-bucket/predictions/july-2026/",
    machine_type="n1-standard-4",
    starting_replica_count=1,
    max_replica_count=5,
)
batch_job.wait()
```

**Choosing between online and batch:**

| Situation | Use Online Prediction | Use Batch Prediction |
|---|---|---|
| Response needed immediately | ✓ | |
| User is waiting for answer | ✓ | |
| Scoring millions of records overnight | | ✓ |
| Periodic report generation | | ✓ |
| Cost-sensitive, non-urgent workload | | ✓ |
| Requires < 100ms latency | ✓ | |

> **Practitioner insight:** Batch prediction is significantly cheaper than maintaining an always-on endpoint. If your use case doesn't require real-time responses, default to batch. I've seen teams spend 10x more than necessary by reflexively deploying online endpoints for workloads that run once a day.

---

## 6. Vertex AI Cost Management

### 6.1 Cost Considerations

Vertex AI pricing follows a **pay-as-you-go** model with no fixed monthly fee. This is liberating for experimentation but requires discipline for production. Here's a practical map of where the money goes.

**The major cost categories:**

**Training costs** are charged per node-hour — the combination of machine type and time. Custom training starts around $0.49/node-hour on a standard CPU machine; GPU machines are significantly more. AutoML training costs more per node-hour (~$3.15/node-hour for image classification) but often requires fewer hours because the process is automated. A typical small AutoML job runs 2-8 node-hours.

**Prediction costs:**
- *Online endpoints:* ~$0.06/node-hour for basic hardware, billed continuously while the endpoint is deployed
- *Batch prediction:* billed only for the duration of the job — much more economical for non-real-time workloads

**Storage costs** are modest but accumulate: models in the Registry, datasets in Cloud Storage, and experiment artifacts all have storage charges (~$0.02/GB-month for standard storage).

**Data transfer (egress):** Moving data out of Google Cloud incurs fees (~$0.12/GB to most destinations). This surprises teams that export large datasets or model files frequently.

**The most impactful cost optimizations:**

Use **preemptible VMs** for training. These are significantly cheaper (often 60-70% savings) but can be interrupted by Google if the capacity is needed. For training jobs, this is usually acceptable because Vertex AI can checkpoint and resume automatically.

Choose **batch over online** for workloads that can tolerate a delay of minutes or hours. The cost difference is often 5-10x.

**Set budget alerts.** In the Google Cloud Console, you can set billing alerts at thresholds like $50, $100, and $500. These send you an email before a problem becomes a crisis.

```
Real cost scenario: Monthly churn scoring for 1M customers

Option A — Online Endpoint (always on):
  1 n1-standard-4 machine × 720 hours/month × $0.30/hr = ~$216/month
  (regardless of whether predictions are requested)

Option B — Batch Prediction (runs 1 hour/month):
  1 hour × n1-standard-4 × $0.30/hr = ~$0.30/month
  
Savings: $215.70/month = $2,588/year
```

> **Practitioner principle:** "The fastest way to get your cloud AI budget canceled is to let a forgotten endpoint bill $500 in a single weekend." Build cost monitoring into your workflow from day one, not as an afterthought.

**Committed Use Discounts (CUDs)** are available for predictable, steady-state workloads — you commit to a certain resource level for 1 or 3 years in exchange for significant discounts. These make sense once you understand your production usage patterns. Don't commit before you have real data on your actual consumption.

---

## 7. Vertex AI Security Controls

### 7.1 Security Considerations

Security in AI systems has two dimensions that beginners often conflate: *access security* (who can touch your AI platform) and *model security* (whether your AI can be manipulated or misused). Vertex AI provides tools for both.

**Access security** on Vertex AI uses the same system as all of Google Cloud: **Identity and Access Management (IAM)**. IAM lets you define exactly who (or what service) can perform which actions on which resources. For example:

- Data scientists might have permissions to create training jobs and read datasets
- Production systems might have a service account that can only call prediction endpoints
- Security auditors might have read-only access to logs and metadata

The principle to apply here is **least privilege**: each person or service should have exactly the permissions needed for their job — nothing more. This is especially important for AI systems because they often process sensitive data.

**VPC Service Controls** let you create a security perimeter around your Vertex AI resources. Data inside the perimeter cannot leave — preventing accidental or malicious exfiltration. This is frequently required in healthcare (HIPAA), finance (PCI-DSS), and government contexts.

**Data encryption** is handled automatically. Data at rest in Google Cloud Storage and in-transit to Vertex AI services is encrypted by default using Google-managed keys. For organizations with stricter requirements, **Customer-Managed Encryption Keys (CMEK)** allow you to supply and control your own keys.

**Model security** is a newer but increasingly critical concern. As AI systems become more powerful, they become targets for **prompt injection attacks** — attempts by malicious input to hijack the model's behavior. Vertex AI's **Model Armor** (introduced in 2025) can inspect inputs to AI models and block prompt injection attempts before they reach the model.

**Audit logging** through Cloud Audit Logs records who made what API calls to your Vertex AI resources, and when. This is essential for compliance and for investigating security incidents.

```
Security layers in a Vertex AI deployment:

[User/Application]
      ↓
[IAM — Are you allowed to call this endpoint?]
      ↓
[Model Armor — Is this input attempting a prompt injection?]
      ↓
[VPC Service Controls — Is this request from within the secure perimeter?]
      ↓
[Vertex AI Endpoint — Model processes input]
      ↓
[Audit Log — This call was made by X at time Y]
```

**Service accounts for automated pipelines.** When a Vertex AI Pipeline runs automatically (scheduled retraining, for example), it needs credentials to access data, write models, and deploy endpoints. The right approach is to create a dedicated **service account** with only the permissions that pipeline needs. Never hard-code credentials in code or notebooks.

> **Practitioner warning:** The most common security mistake I see in AI projects is over-broad permissions during development that never get tightened before production. "I'll fix the permissions later" almost always means they never get fixed. Define your IAM roles correctly from the start — changing them after production deployment is much harder and more disruptive.

---

## 8. Summary / Quick Reference

Congratulations — you've just mapped the entire Vertex AI ecosystem. Here's a distilled reference you can return to as you start working with the platform.

---

### The Vertex AI Services Map

```
┌─────────────────── VERTEX AI PLATFORM ───────────────────────┐
│                                                               │
│  EXPLORE & BUILD                                              │
│  ├── Vertex AI Studio     → Prompt testing, GenAI playground  │
│  ├── Model Garden         → 200+ models to browse & deploy    │
│  └── Notebooks            → Colab Enterprise & Workbench      │
│                                                               │
│  DATA                                                         │
│  └── Managed Datasets     → Tabular, image, text, video       │
│                                                               │
│  TRAIN                                                        │
│  ├── AutoML               → No-code, automated training       │
│  └── Custom Training      → Bring-your-own code + framework   │
│                                                               │
│  TEST & TRACK                                                 │
│  ├── Experiments          → Compare training runs             │
│  ├── Logs & Metrics       → Debug & measure performance       │
│  ├── ML Metadata          → Full lineage & audit trail        │
│  └── Model Registry       → Versioned model catalog           │
│                                                               │
│  DEPLOY & SERVE                                               │
│  ├── Online Prediction    → Real-time, always-on endpoints    │
│  └── Batch Prediction     → Bulk, scheduled, cost-efficient   │
│                                                               │
│  OPERATE                                                      │
│  ├── Cost Management      → Alerts, CUDs, batch vs. online    │
│  └── Security Controls    → IAM, VPC, Model Armor, CMEK       │
└───────────────────────────────────────────────────────────────┘
```

---

### Key Decision Guide

| Question | Answer |
|---|---|
| "Do I need to write ML code?" | Start with AutoML. Add custom training when you hit its limits. |
| "Which model should I use?" | Start with Gemini 2.5 Flash. Upgrade to Pro if quality is insufficient. |
| "Online or batch prediction?" | Batch unless users are waiting for the response in real time. |
| "How do I save money on training?" | Use preemptible VMs. Run sanity checks on CPU before GPU. |
| "How do I avoid surprise bills?" | Set billing alerts. Undeploy unused endpoints. |
| "How do I know which model is in production?" | Always use Model Registry. Never deploy from raw file paths. |

---

### The Golden Rules of Vertex AI (Practitioner Edition)

1. **Track everything.** Use Experiments and ML Metadata from day one. The time you save debugging later is worth 10x the setup time.

2. **Shut things down.** Idle endpoints and notebooks are pure waste. Build a habit of cleanup.

3. **Start small.** Test your training script on cheap hardware. Validate your data pipeline before touching a GPU.

4. **Separate environments.** Have distinct GCP projects (or at minimum, distinct service accounts) for development, staging, and production. What happens in dev should never directly impact prod.

5. **Security by default.** Least-privilege IAM from the start. Don't defer security to "later."

6. **Batch over online.** Unless real-time response is genuinely required, batch prediction is almost always the right choice economically.

7. **The model is never done.** Production models drift over time as the world changes. Plan for monitoring and retraining before you deploy.

---

### Quick Terminology Reference

| Term | Plain-English Definition |
|---|---|
| Endpoint | A live URL that serves predictions from a deployed model |
| Node-hour | One machine running for one hour — the basic unit of Vertex AI billing |
| Fine-tuning | Taking an existing pre-trained model and training it further on your data |
| Data drift | When real-world inputs start looking different from your training data |
| AutoML | Automated ML that handles algorithm selection and tuning for you |
| Model Registry | The versioned catalog of all your trained models |
| Experiment / Run | A container for trials / a single trial within that container |
| Artifact | A file produced by an ML step (trained model, dataset, evaluation report) |
| IAM | Identity and Access Management — Google Cloud's permission system |
| CMEK | Customer-Managed Encryption Keys — you control the encryption keys |

---

*These notes reflect the Vertex AI / Gemini Enterprise Agent Platform state as of mid-2026. The platform evolves rapidly — always verify current pricing at cloud.google.com/vertex-ai/pricing and check release notes for the latest feature availability.*