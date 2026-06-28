# Model Architecture Comparison & LLM Implementation Strategies
## Lecture Notes

> *This module is your practical guide to the major AI models you'll encounter in the real world — what they are, how they differ, and how to choose and use them wisely. No deep math required. Think of this as your "field guide" to the LLM landscape.*

---

# Table of Contents

**Part I — Model Architecture Comparison**
1. [GPT Family — GPT-3.5, GPT-4, GPT-4 Turbo](#1-gpt-family--gpt-35-gpt-4-gpt-4-turbo)
2. [BERT and Variants](#2-bert-and-variants)
3. [Claude Models](#3-claude-models)
4. [Meta LLaMA Models](#4-meta-llama-models)

**Part II — LLM Implementation Strategies**

5. [Use Cases for LLMs](#5-use-cases-for-llms)
6. [LLM Best Practices](#6-llm-best-practices)

---

# PART I — MODEL ARCHITECTURE COMPARISON

---

## A Quick Orientation Before We Dive In

With so many AI models in the news — GPT-4, Claude, Gemini, LLaMA — it's easy to feel overwhelmed. Here's a simple mental map before we look at each one:

```
All these models are Large Language Models (LLMs).
They differ in:

├── WHO made them (OpenAI, Anthropic, Meta, Google...)
├── WHAT they're best at (generating text, understanding text, coding...)
├── HOW you access them (API, web interface, self-hosted...)
└── COST (paid API, free tier, fully free/open-source)
```

Think of LLMs like cars: they all get you from A to B, but a sports car, a family SUV, and a pickup truck are designed for different purposes at different price points. Knowing the differences helps you pick the right tool.

---

# 1. GPT Family — GPT-3.5, GPT-4, GPT-4 Turbo

## 1.1 Who Makes Them?

The GPT (Generative Pre-trained Transformer) family is made by **OpenAI**, a San Francisco-based AI company founded in 2015. OpenAI also makes ChatGPT — the consumer product that brought LLMs into mainstream awareness in late 2022.

## 1.2 The Big Idea Behind GPT Models

All GPT models follow the same core recipe:

1. **Pre-train** on a massive amount of text from the internet, books, and other sources
2. **Fine-tune** to follow instructions and be helpful (using RLHF — human feedback)
3. **Deploy** via an API that developers can build products on, and via ChatGPT for consumers

GPT models are **decoder-only** Transformers. This means they generate text one word (token) at a time, left to right. They are optimized for *generation* — producing new text in response to an input.

## 1.3 GPT-3.5

**Released:** March 2022 (ChatGPT version: November 2022)

**What it is:** The model that made AI assistants go mainstream. GPT-3.5 was the engine behind the original ChatGPT and shocked the world with how naturally it could hold conversations, write essays, and answer questions.

**Key characteristics:**
- Fast and cost-effective to run
- Good at everyday language tasks: writing, summarizing, answering questions, basic coding
- Not as accurate or capable on complex reasoning tasks as newer models
- 4,096 token context window (about 3,000 words — enough for a few pages)

**Where it's still used:**
- High-volume, cost-sensitive applications where speed matters
- Simple chatbots and FAQ bots
- Applications where GPT-4 level quality isn't needed (and the cost savings are worth it)

**Analogy:** A reliable economy car. Gets you where you need to go, fuel-efficient, but don't expect sports car performance.

## 1.4 GPT-4

**Released:** March 2023

**What it is:** A major leap over GPT-3.5 in reasoning, accuracy, and nuance. OpenAI hasn't published the parameter count, but it is substantially larger and more capable than GPT-3.5.

**Key improvements over GPT-3.5:**
- **Significantly better reasoning:** Can solve harder math problems, logic puzzles, and multi-step tasks
- **Longer context:** Up to 128,000 tokens in some versions (about 96,000 words — nearly a full novel)
- **Multimodal (GPT-4V):** Can understand and reason about images, not just text
- **More reliable instruction-following:** Better at sticking to constraints and output formats
- **Less hallucination:** More likely to say "I don't know" rather than confidently make something up

**Where it excels:**
- Complex document analysis and legal/financial review
- Advanced coding assistance and code review
- Research synthesis
- Tasks requiring nuanced judgment

**Trade-offs:**
- Slower than GPT-3.5
- More expensive per token
- Overkill for simple tasks

**Analogy:** A luxury sedan. More powerful, more refined, costs more to run.

## 1.5 GPT-4 Turbo

**Released:** November 2023

**What it is:** OpenAI's attempt to give you most of GPT-4's power at lower cost and higher speed. "Turbo" means optimized for practical deployment.

**Key improvements over standard GPT-4:**
- **Cheaper:** Lower cost per token than GPT-4
- **Faster:** Quicker response times
- **Longer context:** 128K token context window as standard
- **Knowledge cutoff:** More recent training data than early GPT-4 versions
- **Better instruction following:** Improved performance on following complex multi-part instructions

**In practice:** For most applications that need GPT-4 level quality, GPT-4 Turbo is the better practical choice — you get similar quality at lower cost and latency.

**Analogy:** The same luxury sedan but with a more fuel-efficient engine. Better value without giving up much performance.

## 1.6 GPT-4o ("Omni")

**Released:** May 2024

While not in the original list, it's worth noting briefly: GPT-4o is OpenAI's current flagship model as of 2024-2025. It's **natively multimodal** — processes text, images, and audio in a unified model rather than as separate components bolted together. It's faster than GPT-4 Turbo and cheaper.

## 1.7 Comparing the GPT Family

| Model | Speed | Cost | Quality | Context | Best For |
|-------|-------|------|---------|---------|----------|
| GPT-3.5 | ⚡⚡⚡ Fast | 💰 Cheapest | ★★★ Good | 16K | Simple tasks, high volume |
| GPT-4 | ⚡ Slower | 💰💰💰 Expensive | ★★★★★ Excellent | 128K | Complex reasoning, quality matters |
| GPT-4 Turbo | ⚡⚡ Fast | 💰💰 Moderate | ★★★★★ Excellent | 128K | Best balance for most use cases |

## 1.8 How You Access GPT Models

- **ChatGPT (chat.openai.com):** Consumer web interface. Free tier uses GPT-3.5; Plus subscription ($20/month) gives GPT-4 access.
- **OpenAI API:** For developers building applications. Pay per token.
- **Microsoft Azure OpenAI Service:** Enterprise version of the same models with enterprise security and compliance.
- **Microsoft Copilot:** GPT-4 embedded in Microsoft 365, Bing, and Windows.

---

# 2. BERT and Variants

## 2.1 Who Makes BERT?

**BERT** (Bidirectional Encoder Representations from Transformers) was created by **Google** and released in October 2018. It was a landmark moment in NLP — the paper describing it has been cited over 100,000 times.

## 2.2 BERT Is Fundamentally Different From GPT

This is the most important thing to understand about BERT: **it is not designed to generate text**. It is designed to *understand* text.

```
GPT Family:    READ → GENERATE
               (text in, new text out)

BERT Family:   READ → UNDERSTAND
               (text in, meaning/classification/answer out)
```

**The key technical difference:**
- GPT reads text **left to right only** (because it's generating the next word, it can't "cheat" and look ahead)
- BERT reads text **in both directions simultaneously** (it can see the full sentence at once and understand each word in its full context)

Reading bidirectionally makes BERT much better at understanding — when you read "The bank by the river was steep," seeing both "bank" and "river" together helps you know it's a river bank, not a financial institution.

## 2.3 What BERT Is Good At

BERT-family models excel at **understanding tasks**:

| Task | Example |
|------|---------|
| **Text classification** | "Is this review positive or negative?" |
| **Named entity recognition** | "Which words in this sentence are person names?" |
| **Question answering** | "Based on this paragraph, when did the event happen?" |
| **Semantic similarity** | "Do these two sentences mean the same thing?" |
| **Sentence embeddings** | Converting sentences to vectors for search/comparison |

**Where BERT does NOT work:**
- Generating new text (essays, stories, responses) — use GPT for this
- Open-ended conversation — use a generative model
- Tasks that require producing paragraphs of output

## 2.4 How BERT Is Trained

BERT uses two clever training tasks on unlabeled text:

**Masked Language Modeling (MLM):**
Take a sentence, randomly hide 15% of the words, ask the model to predict them:
```
Input:  "The cat sat on the [MASK]."
Target: "The cat sat on the mat."
```
This forces the model to understand context from both sides of each word.

**Next Sentence Prediction (NSP):**
Show two sentences, ask "Is sentence B a natural follow-up to sentence A?"
```
A: "She went to the store."
B: "She bought some milk."       → TRUE
B: "Penguins live in Antarctica."  → FALSE
```
This teaches the model to understand relationships between sentences.

## 2.5 BERT Variants — The Family Tree

BERT sparked a wave of variants, each improving on some aspect:

### RoBERTa (Robustly Optimized BERT, Facebook 2019)
"What if we just trained BERT better?" RoBERTa kept BERT's architecture but:
- Removed Next Sentence Prediction (turned out to hurt more than help)
- Trained on 10× more data
- Used larger batches and longer training
- Result: Consistently outperformed original BERT on benchmarks

**Think of it as:** BERT that went to the gym more and ate better.

### DistilBERT (Hugging Face 2019)
"What if we made BERT smaller and faster?" DistilBERT uses **knowledge distillation** — a technique where a smaller model (the "student") is trained to mimic a larger model (the "teacher"):
- 40% smaller than BERT
- 60% faster
- Retains ~97% of BERT's performance

**Best for:** Applications where you need BERT-like understanding but have latency or cost constraints (e.g., real-time classification in a mobile app).

### ALBERT (A Lite BERT, Google 2019)
Another efficiency-focused variant:
- Dramatically fewer parameters than BERT (by sharing weights across layers)
- Maintains strong performance despite being smaller
- Scales better to larger sizes than original BERT

### Domain-Specific BERT Variants
One of the best uses of BERT: fine-tune it on domain-specific text to create specialized models.

| Model | Domain | Use |
|-------|--------|-----|
| BioBERT | Biomedical literature | Medical text mining |
| LegalBERT | Legal documents | Contract analysis |
| FinBERT | Financial news | Sentiment in financial text |
| SciBERT | Scientific papers | Research text understanding |
| ClinicalBERT | Clinical notes | Patient record analysis |

These models understand domain vocabulary and conventions far better than a general-purpose BERT.

## 2.6 When to Use BERT vs. GPT

| Need | Use |
|------|-----|
| Classify text (sentiment, topic, intent) | BERT family |
| Extract information from a document | BERT family |
| Find similar documents/sentences | BERT embeddings |
| Generate a response or write content | GPT family |
| Answer a specific question from a document | BERT family |
| Have a conversation | GPT family |
| Label entities in text (names, dates, places) | BERT family |
| Summarize a document | GPT family |

**Simple rule:** If the output is a *label*, *score*, or *span of existing text* → BERT. If the output is *new text* → GPT.

---

# 3. Claude Models

## 3.1 Who Makes Claude?

**Claude** is made by **Anthropic**, an AI safety company founded in 2021 by Dario Amodei, Daniela Amodei, and several colleagues who previously worked at OpenAI. Anthropic's core focus is building AI that is safe, honest, and helpful — in that order.

The name "Claude" has no official explanation from Anthropic, but is widely believed to be a reference to Claude Shannon, the father of information theory.

## 3.2 What Makes Claude Different

Claude is a direct competitor to GPT-4 in the "large, capable, instruction-following LLM" category. The key differentiators:

### Constitutional AI (CAI)
Anthropic developed a unique approach to safety training called **Constitutional AI**. Instead of relying solely on human raters to evaluate every response, they:

1. Give the model a set of principles (the "constitution") — values like "be helpful," "be harmless," "don't be deceptive"
2. Train the model to critique its own responses against these principles
3. Train it to revise its responses to better align with the principles

This makes safety training more scalable and consistent — the model learns *why* certain responses are problematic, not just *that* they are.

### Emphasis on Honesty
Claude is specifically trained to:
- Admit when it doesn't know something
- Avoid stating uncertain things as facts
- Be resistant to sycophancy (telling users what they want to hear)
- Disagree with users when it has good reason to

### Long Context
Claude models have historically prioritized long context windows, enabling use cases like:
- Analyzing entire codebases
- Reading and reasoning about book-length documents
- Processing lengthy legal contracts or research papers

## 3.3 Claude Model Generations

### Claude 1 (March 2023)
The first public release. Demonstrated strong writing quality, honesty, and a distinctive "voice" — thoughtful, nuanced, and careful. Less capable than GPT-4 on some benchmarks but already showing the characteristics Anthropic aimed for.

### Claude 2 (July 2023)
Major upgrade in context window (100K tokens — one of the largest at the time) and capability. Improved performance on coding, math, and following complex instructions.

### Claude 3 Family (March 2024)
Three models with different capability/speed/cost trade-offs:

| Model | Speed | Cost | Capability | Best For |
|-------|-------|------|-----------|----------|
| **Claude 3 Haiku** | ⚡⚡⚡ Very Fast | 💰 Cheapest | ★★★ Good | High-volume, simple tasks |
| **Claude 3 Sonnet** | ⚡⚡ Moderate | 💰💰 Moderate | ★★★★ Very Good | Balanced everyday tasks |
| **Claude 3 Opus** | ⚡ Slower | 💰💰💰 Expensive | ★★★★★ Best | Complex research, deep reasoning |

This three-tier naming convention (Haiku → Sonnet → Opus, in increasing capability) has become Claude's signature naming system.

**Claude 3 Opus** was the most capable model available in early 2024, matching or exceeding GPT-4 on many benchmarks — particularly for reading comprehension, reasoning, and nuanced writing.

### Claude 3.5 Family (2024–2025)
**Claude 3.5 Sonnet** (June 2024) was a significant release that achieved Opus-level performance at Sonnet-level price and speed — reshuffling the competitive landscape. At release, it was arguably the best coding model available.

**Claude 3.5 Haiku** followed, bringing improved capabilities to the fast/cheap tier.

## 3.4 What Claude Is Particularly Good At

- **Long document analysis:** Consistently strong at reasoning across very long contexts without losing track of details
- **Writing quality:** Many users find Claude's prose style more natural and nuanced than GPT-4
- **Following complex instructions:** Strong adherence to detailed, multi-part formatting requirements
- **Coding:** Especially Claude 3.5 Sonnet, which became a top choice for software engineering tasks
- **Honesty and calibration:** More likely to express appropriate uncertainty and less likely to confabulate

## 3.5 How You Access Claude

- **Claude.ai:** Anthropic's consumer web and mobile interface (free tier + Pro subscription)
- **Anthropic API:** For developers. Pay per token.
- **Amazon Bedrock:** Claude models available through AWS's managed AI platform
- **Google Cloud Vertex AI:** Claude also available through Google's enterprise cloud

---

# 4. Meta LLaMA Models

## 4.1 Who Makes LLaMA?

**LLaMA** (Large Language Model Meta AI) is made by **Meta** (the parent company of Facebook, Instagram, and WhatsApp). Meta's AI research team (FAIR — Fundamental AI Research) has been one of the most prolific research groups in AI.

Unlike OpenAI and Anthropic, Meta has taken a primarily **open-source strategy**: releasing model weights publicly so anyone can download, run, study, and modify them.

## 4.2 Why Open-Source Models Matter

Before LLaMA, frontier-quality LLMs were only available through paid APIs from OpenAI or Anthropic. You could use them but couldn't see the weights, modify them, or run them yourself.

LLaMA changed this. When Meta released model weights publicly, developers could:
- **Run models locally** on their own hardware (no API costs, no data leaving their servers)
- **Fine-tune** models on private proprietary data without sharing that data with any company
- **Study** how models work internally
- **Build** products without ongoing API cost dependency
- **Deploy** in air-gapped environments (hospitals, defense, banking) where sending data to external APIs isn't possible

> **The analogy:** Before LLaMA, cloud AI was like renting a car — convenient, but you don't own it and someone else can see where you go. After LLaMA, you could buy your own car, modify the engine, and drive wherever you want without anyone tracking you.

## 4.3 LLaMA 1 (February 2023)

**Released as a research model** — available to researchers (and very quickly, to anyone, after a leak).

**Key innovation:** Meta demonstrated that a smaller, carefully trained model could outperform much larger models. LLaMA-13B (13 billion parameters) outperformed GPT-3 (175 billion parameters) on many benchmarks.

**How?** Data quality over data quantity, and longer training on better data. This challenged the assumption that you always need a bigger model for better performance.

## 4.4 LLaMA 2 (July 2023)

Released as **truly open-source** (downloadable for commercial use, not just research).

**Key additions:**
- Released in sizes: 7B, 13B, 34B, 70B parameters
- Released both base models (raw pre-trained) AND chat-tuned versions (instruction-following)
- Strong performance, especially the 70B model, which approached GPT-3.5 quality

**What makes size matter?**
```
Smaller models (7B):
├── Run on consumer hardware (16GB RAM laptop or gaming GPU)
├── Faster inference
├── Less capable on complex reasoning
└── Good for simple, well-defined tasks

Larger models (70B):
├── Require dedicated GPU server (80GB+ VRAM)
├── Slower inference
├── Much better reasoning and instruction-following
└── Competitive with GPT-3.5 / GPT-4 on many tasks
```

## 4.5 LLaMA 3 (April 2024)

A major generational leap. Released in 8B and 70B sizes initially, with a 405B model following.

**Key improvements:**
- Dramatically better instruction-following than LLaMA 2
- Larger vocabulary (128K tokens vs. 32K) — better multilingual support and more efficient encoding
- 8K context window standard (later extended versions go much further)
- LLaMA 3 70B became competitive with GPT-4 class models on many benchmarks

**LLaMA 3.1 (July 2024)** expanded context to 128K tokens and released the 405B parameter model — the largest open-weight model available, competitive with frontier closed models.

## 4.6 The LLaMA Ecosystem

One of LLaMA's most important contributions is the ecosystem it spawned. Because the weights are open, hundreds of derived models and tools have been built:

**Fine-tuned derivatives:**
- **Vicuna:** Fine-tuned on ChatGPT conversations; early strong chat model
- **Alpaca:** Stanford's fine-tune of LLaMA 1 on instruction data
- **Code Llama:** Meta's own fine-tune of LLaMA 2 specialized for coding
- **Mistral, Mixtral:** French startup Mistral AI's highly efficient models built in the LLaMA tradition

**Tools for running LLaMA locally:**
- **Ollama:** Run LLaMA and other open models with a single command on your laptop
- **LM Studio:** Desktop app for running local LLMs with a chat interface
- **llama.cpp:** Extremely efficient C++ implementation; run LLaMA on CPU

## 4.7 Comparing the Four Model Families

| | GPT Family | BERT Family | Claude | LLaMA |
|--|-----------|------------|--------|-------|
| **Made by** | OpenAI | Google | Anthropic | Meta |
| **Primary use** | Generation | Understanding | Generation | Generation |
| **Access** | Paid API | Open-source | Paid API | Open-source |
| **Run locally?** | No | Yes | No | Yes |
| **Best at** | Reasoning, coding, breadth | Classification, search, NLP tasks | Long context, honesty, writing | Flexibility, privacy, cost control |
| **Context window** | Up to 128K | Up to 512 tokens (standard BERT) | Up to 200K | Up to 128K (LLaMA 3.1) |
| **Cost** | Pay-per-token | Free (self-hosted) | Pay-per-token | Free (self-hosted) |
| **Key strength** | Breadth and ecosystem | Specialized NLP tasks | Safety and long context | Privacy and customization |

---

# PART II — LLM IMPLEMENTATION STRATEGIES

---

# 5. Use Cases for LLMs

## 5.1 How to Think About LLM Use Cases

Before diving into specific applications, here's a simple framework for deciding whether an LLM is the right tool:

```
✅ LLMs ARE good for:
├── Tasks involving natural language (reading, writing, understanding)
├── Tasks with flexible, subjective outputs (drafting, summarizing)
├── Tasks where "pretty good" is sufficient (brainstorming, first drafts)
└── Tasks that previously required expensive human expertise at scale

❌ LLMs are NOT good for:
├── Precise calculations (use a calculator or code)
├── Looking up real-time or very recent information (use search/APIs)
├── Tasks requiring 100% accuracy (medical dosing, financial transactions)
└── Tasks with no language component (image compression, sorting algorithms)
```

## 5.2 The Major Use Case Categories

### Category 1: Content Creation and Writing Assistance

**What it is:** Using LLMs to draft, edit, rewrite, or improve text.

**Examples:**
- Marketing copy and ad variations
- Email drafts and professional communications
- Blog posts, articles, and social media content
- Product descriptions at scale (e-commerce)
- Job descriptions and HR documents
- Reports and executive summaries

**Why LLMs excel here:** Writing is exactly what LLMs were trained on. They've seen countless examples of every genre and style.

**Real-world example:** An e-commerce company uses GPT-4 to generate unique product descriptions for 50,000 SKUs — a task that would have required a team of copywriters working for months.

**What to watch out for:** Generic, "AI-sounding" output; factual errors in product details; brand voice inconsistency. Always review AI-generated content before publishing.

---

### Category 2: Question Answering and Knowledge Retrieval

**What it is:** Using LLMs to answer questions, often grounded in a company's own documents.

**Examples:**
- Internal knowledge base chatbot ("How do I submit an expense report?")
- Customer support FAQ automation
- Legal document Q&A ("What does clause 4.2 say about termination?")
- Technical documentation assistant
- Policy and compliance lookup

**Architecture typically used:** RAG (Retrieval-Augmented Generation) — the model retrieves relevant document sections and answers based on them.

**Why it works:** Employees or customers have natural language questions. LLMs can match those questions to relevant document content and synthesize answers far faster than manual search.

**Real-world example:** A law firm deploys a Claude-powered assistant on their contract library. Lawyers can ask "Which contracts have unlimited liability clauses?" and get answers in seconds rather than hours of manual review.

---

### Category 3: Code Generation and Developer Assistance

**What it is:** Using LLMs to write, explain, debug, or review code.

**Examples:**
- Autocomplete and code generation (GitHub Copilot)
- Explaining what a complex function does
- Translating code between languages (Python → JavaScript)
- Writing unit tests for existing functions
- Debugging — "Why is this code throwing a NullPointerException?"
- Code review and identifying security vulnerabilities
- Generating SQL queries from plain English descriptions

**Why LLMs excel here:** Code is text. Billions of lines of open-source code across every language were in the training data. LLMs have seen countless patterns of problems and solutions.

**Real-world impact:** GitHub Copilot users complete tasks up to 55% faster (GitHub, 2023). For boilerplate and repetitive code, productivity gains are even larger.

**What to watch out for:** Security vulnerabilities in generated code; subtly incorrect logic that compiles and runs but gives wrong answers; outdated API usage.

---

### Category 4: Data Extraction and Transformation

**What it is:** Using LLMs to pull structured information out of unstructured text.

**Examples:**
- Extracting invoice details (date, amount, vendor) from scanned documents
- Pulling key data from contracts (parties, dates, obligations)
- Converting free-text customer feedback into structured categories
- Extracting medical information from clinical notes
- Parsing resumes into structured fields
- Normalizing inconsistently formatted data

**Why LLMs excel here:** This task is easy for a human but hard for traditional software — it requires understanding context, handling variability, and using judgment. LLMs handle this naturally.

**Real-world example:** An insurance company processes thousands of claims letters per day. An LLM extracts: claim date, policy number, claimant name, incident description, and estimated loss amount — feeding them directly into a structured database.

---

### Category 5: Summarization and Synthesis

**What it is:** Condensing long content into shorter, actionable summaries.

**Examples:**
- Meeting transcript → action items and summary
- Long research report → executive summary
- Dozens of customer reviews → key themes and sentiment
- Legal brief → plain-language summary for non-lawyers
- News articles → daily briefing
- Academic paper → accessible explanation

**Why LLMs excel here:** Understanding what matters and how to express it concisely requires the kind of language comprehension LLMs are built for.

**Real-world example:** A consulting firm uses Claude to process 200-page due diligence reports and produce 2-page summaries with key findings, risks, and recommendations — giving partners a head start before diving into the full document.

---

### Category 6: Classification and Routing

**What it is:** Using LLMs to categorize text into predefined (or discovered) categories.

**Examples:**
- Customer support ticket routing ("This is a billing issue" → billing team)
- Content moderation (safe/unsafe/borderline)
- Sentiment analysis (positive/negative/neutral)
- Email classification and prioritization
- Lead qualification from sales inquiries
- Medical symptom triage

**Why LLMs excel here:** They understand nuance and context that keyword-based systems miss. "The product is not as terrible as I expected" — a keyword system might flag "terrible" as negative, but an LLM correctly identifies the positive sentiment.

**Note:** For simple, high-volume classification, fine-tuned BERT models are often more efficient and just as accurate as large generative models. Use the right tool.

---

### Category 7: Conversational AI and Chatbots

**What it is:** Multi-turn dialogue systems that help users accomplish goals.

**Examples:**
- Customer service chatbots (handling tier-1 support)
- Sales assistants (answering product questions, guiding purchasing decisions)
- HR assistants (answering employee policy questions)
- Onboarding assistants (guiding new users through a product)
- Health information chatbots
- Educational tutors

**Why LLMs are better than old-style chatbots:** Traditional rule-based chatbots required manually scripted conversation flows. Users had to phrase things exactly right. LLMs understand natural, imperfect human language and can handle unanticipated questions gracefully.

**Real-world example:** A bank deploys an LLM-powered chat assistant. Customers can ask "What's the difference between a savings account and a money market account?" or "Can I add my daughter to my account?" in their own words. The AI handles 70% of queries without human intervention.

---

### Category 8: Agentic Tasks and Automation

**What it is:** LLMs not just answering questions, but taking actions — browsing the web, calling APIs, writing files, executing code.

**Examples:**
- Research agent: "Research the top 5 competitors and summarize their pricing"
- Data agent: "Pull this week's sales data, calculate growth vs. last week, and email the report to the team"
- Coding agent: "Fix the failing tests in this repository"
- Scheduling agent: "Find a time next week when all three executives are free and book a meeting"

**Why it's the frontier:** Combining LLM reasoning with the ability to take actions creates systems that can autonomously complete multi-step tasks. This is where the biggest productivity gains are being unlocked.

**What to watch out for:** This is also where the most can go wrong. Autonomous systems need careful design: what actions require human approval? What happens if the agent misunderstands the request? (See Best Practices, Section 6.)

---

## 5.3 Use Case Selection Framework

When evaluating whether to use an LLM for a use case:

```
Question 1: Is there a language component?
If No → LLM probably wrong tool
If Yes → Continue

Question 2: Can you tolerate occasional errors?
If No (medical dosing, financial transactions) → Add robust human review
If Yes → Continue

Question 3: Do you need current/real-time information?
If Yes → Need RAG or tool use (LLMs can't browse by default)
If No → Continue

Question 4: How much does volume matter?
High volume + simple task → Smaller, cheaper model (GPT-3.5, Claude Haiku)
Lower volume + complex task → Larger, more capable model (GPT-4, Claude Opus)

Question 5: Is data privacy critical?
Yes, data cannot leave your servers → Open-source, self-hosted (LLaMA)
No, API acceptable → Commercial API (GPT, Claude)
```

---

# 6. LLM Best Practices

## 6.1 Start Simple, Then Add Complexity

One of the most common mistakes: over-engineering from day one.

**The right progression:**
```
1. Zero-shot prompt → does it work?
   If yes: done. If no →
   
2. Add more context and better instructions → does it work?
   If yes: done. If no →
   
3. Add few-shot examples → does it work?
   If yes: done. If no →
   
4. Try chain-of-thought → does it work?
   If yes: done. If no →
   
5. Consider fine-tuning (only if you have good data and a clear need)
```

Each step adds complexity and cost. Stop at the simplest step that works. A prompt that solves your problem in 5 minutes is better than fine-tuning that takes 5 days if they produce the same output quality.

## 6.2 Always Evaluate Before You Deploy

Sending a prompt to an LLM and seeing a good response is not validation. One response proves nothing — LLMs are probabilistic and will produce different outputs on different runs.

**Build an evaluation set:**
1. Collect 50-200 representative examples of inputs you expect to receive
2. Write or collect the correct/ideal outputs for each
3. Run your prompt on all of them
4. Measure: what % are correct? What kinds of errors occur?

**Only move to production when your eval results are acceptable.** "Acceptable" depends on the stakes — a marketing copy generator might be fine at 80% usable output; a medical information tool might require 99%+.

## 6.3 Design for Failure

LLMs will sometimes produce wrong, unhelpful, or unexpected output. This is not a bug to be fixed but a property to be designed around.

**Design patterns for graceful failure:**

**Confidence thresholds:** If using a classification model, don't just take the top prediction — check the confidence score. Low confidence → route to human review.

**Fallback responses:** If the model's output doesn't pass validation (e.g., invalid JSON, unexpected category), have a fallback: retry with a different prompt, route to a human, or return a safe default.

**Human-in-the-loop:** For high-stakes decisions, always include a step where a human reviews AI output before it has real-world consequences. AI suggests; human approves.

**Graceful degradation:** Design your system so that if the AI component fails, the system degrades gracefully (e.g., shows a "request a human agent" option) rather than crashing.

## 6.4 Use the Right Model for the Job

Choosing the most powerful model is not always the right choice. Match model capability to task requirements:

| Task Complexity | Right Model Tier | Why |
|----------------|-----------------|-----|
| Simple classification, short summaries | Small/fast (GPT-3.5, Haiku, LLaMA 7B) | Cheaper, faster, sufficient |
| Everyday writing, coding assistance | Medium (GPT-4 Turbo, Claude Sonnet) | Good balance |
| Complex reasoning, deep analysis | Large (GPT-4, Claude Opus) | Worth the cost for quality |
| Privacy-critical, self-hosted | Open-source (LLaMA, Mistral) | Data control |
| High-volume production | Smallest model that meets quality bar | Cost at scale is real |

**Example:** A company uses Claude Opus for analyzing complex legal contracts (high stakes, quality critical) but uses Claude Haiku for the much simpler task of classifying support tickets (high volume, simple task). Smart resource allocation.

## 6.5 Manage Your Costs

API costs can scale quickly in production. Key levers:

**Token efficiency:**
- Keep prompts as concise as possible without losing necessary information
- Set `max_tokens` to the minimum you need — don't let the model ramble
- Use shorter few-shot examples

**Caching:**
- Cache responses for identical or highly similar inputs
- For FAQ-style use cases, caching hit rates can be very high

**Model selection:**
- Default to cheaper models; escalate to expensive ones only when needed
- "Cascading" approach: try cheap model first; if confidence is low, escalate to expensive model

**Monitoring:**
- Track token usage per feature, per user, per day
- Set cost alerts before they become budget surprises

## 6.6 Handle Sensitive Data Carefully

When building with commercial LLM APIs, be aware of what you're sending:

**Do not send through commercial APIs:**
- Customer PII (names, email addresses, phone numbers) unless you've reviewed the provider's data processing agreement
- Financial account details
- Health information (potential HIPAA implications)
- Proprietary trade secrets if the provider trains on your data

**Best practices:**
- Read your provider's data usage policy carefully (OpenAI, Anthropic, and others have different policies for API vs. consumer products)
- Use anonymization/pseudonymization before sending sensitive data
- For highly sensitive data, use a self-hosted open-source model (LLaMA)
- Consider enterprise API tiers, which typically have stricter data-handling commitments

## 6.7 Version Control Your Prompts

Prompts are code. Treat them as such.

- Store prompts in version control (Git)
- Write meaningful commit messages when you change a prompt ("Added few-shot examples to improve date extraction accuracy")
- Never modify a production prompt without testing on your eval set first
- Keep old versions — you may need to roll back

**Why it matters:** You modify a prompt and it works better on the cases you tested. Two weeks later, a customer reports weird behavior on a case you didn't test. Without version history, you don't know what changed or when.

## 6.8 Monitor in Production

Deploying is not the end — it's the beginning. Production monitoring is essential:

**What to monitor:**
- **Response quality:** Sample outputs regularly; human-review a % of production responses
- **Latency:** Response time — are users waiting too long?
- **Error rates:** How often does the model output something invalid or that triggers fallbacks?
- **Cost:** Token consumption over time — is it growing as expected?
- **User feedback:** Thumbs up/down, explicit feedback, escalation to human agents

**Drift detection:** Models can drift in behavior — either because you changed the prompt, the model provider updated the underlying model, or the distribution of user inputs shifted. Monitor for unexpected changes in output patterns.

## 6.9 Be Transparent With Users

When deploying AI-facing products:

- **Tell users they're talking to AI.** This is increasingly a legal requirement in many jurisdictions and always the ethical choice.
- **Be clear about AI limitations.** "This is AI-generated and may contain errors. Please verify important information."
- **Provide escalation paths.** Users who want to speak with a human should always have that option.
- **Don't use AI to deceive.** Impersonating a human, creating fake reviews, or generating misleading content are misuses that can carry legal and reputational consequences.

## 6.10 Security Basics for LLM Applications

(Full detail in the Security section of the Prompt Engineering notes — here's the quick summary)

- **Validate all outputs** before acting on them, especially in agentic systems
- **Never put secrets** (passwords, API keys) in system prompts
- **Limit what your AI can do** — minimal privilege for agents
- **Watch for prompt injection** — especially if your model processes user-submitted content
- **Rate limit** your API endpoints to prevent abuse and runaway costs

---

## Summary: The Practitioner's Quick Reference

### Model Selection at a Glance

```
Need to GENERATE text, code, or content?
├── Quality + safety + long context → Claude (Anthropic API)
├── Breadth + ecosystem + multimodal → GPT-4/4o (OpenAI API)
├── Privacy + self-hosted → LLaMA 3 (run yourself)
└── Fast + cheap + high volume → GPT-3.5 / Claude Haiku / LLaMA 7B

Need to UNDERSTAND/CLASSIFY text?
├── General purpose → RoBERTa or DistilBERT
├── Domain-specific (medical, legal, financial) → Domain-specific BERT variant
└── Need generation too? → Use a generative model with classification prompt
```

### Use Case Fit at a Glance

| Use Case | Good LLM Fit? | Key Consideration |
|----------|--------------|-------------------|
| Content writing | ✅ Excellent | Always review before publishing |
| Document Q&A | ✅ Excellent | Use RAG for grounding |
| Code assistance | ✅ Excellent | Review for security issues |
| Data extraction | ✅ Very Good | Validate output structure |
| Summarization | ✅ Excellent | Check for omissions |
| Real-time info | ⚠️ Needs tool use | Add search/retrieval |
| Precise math | ❌ Poor | Use code execution |
| 100% accuracy | ⚠️ Needs human review | Never fully autonomous |

### The Five Golden Rules

1. **Start simple** — don't fine-tune when a good prompt will do
2. **Always evaluate** — one good response proves nothing; test on many
3. **Design for failure** — assume errors will happen; plan for them
4. **Match model to task** — don't use a sledgehammer when a tack hammer will do
5. **Monitor in production** — deployment is the beginning, not the end

---

*The LLM landscape is changing fast — models that are state-of-the-art today will be superseded in months. What doesn't change is the judgment required to choose the right model, the right approach, and the right safeguards for each problem. That judgment is what this module has been building toward.*