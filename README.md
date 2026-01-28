# Explainable Phishing Email Scanner with Controlled LLM Escalation

## Overview

A two-tier phishing email detection system that combines fast Machine Learning classification with selective Large Language Model (LLM) escalation for borderline cases and high-impact users. The system provides explainable risk scores and actionable guidance for non-technical users.

## System Architecture

```
Email Input
    ↓
[ML Classifier] → Risk Score (0-100) + Classification (Safe/Suspicious/Phishing)
    ↓
[Escalation Logic] → Triggers: Borderline (45-70) OR High-Impact User
    ↓ (if triggered)
[LLM Agent] → Structured Analysis + Refined Verdict + User Advice
    ↓
Final Verdict with Explanation
```

## Key Features

- **Fast ML Screening**: TF-IDF + Logistic Regression classifier (99.39% accuracy)
- **Controlled LLM Usage**: Only escalates when needed (cost-efficient)
- **Explainability**: Every decision includes reasoning and actionable advice
- **Real Dataset**: Trained on 39,154 emails from CEAS 2008 Phishing Dataset
- **High Performance**: Precision 99.29%, Recall 99.61%, F1-Score 99.45%

## Installation

### Requirements
- Python 3.13+
- UV package manager (recommended) or pip

### Setup

```bash
# Clone or download the project
cd task_email

# Install dependencies using uv
uv sync

# Or using pip
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your GEMINI_API_KEY to .env file
```

### Dataset Setup

Download the CEAS_08.csv dataset and place it in the project root:
- Dataset: https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset
- File: `CEAS_08.csv` (39,154 emails)

## Usage

### Training the Model

```python
from src.ml_classifier import PhishingClassifier

# Train on CEAS_08.csv dataset
classifier = PhishingClassifier()
classifier.train(test_size=0.2)
classifier.save_model('phishing_model.pkl')
```

### Scanning Emails

```python
from src.scanner import ScannerOrchestrator
import asyncio

async def scan():
    scanner = ScannerOrchestrator(use_pretrained=True)

    result = await scanner.scan_email(
        email_text="Urgent: Verify your account immediately",
        user_role="finance"  # Triggers LLM escalation
    )

    print(f"Classification: {result['classification']}")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Explanation: {result['explanation']}")

asyncio.run(scan())
```

### Quick Test

```bash
# Test with your own email
uv run python3 test_my_email.py

# Generate example analyses
cd Example
uv run python3 generate_examples.py
```

## Escalation Triggers

The system escalates to LLM analysis when:

1. **Borderline Score (45-70)**: Uncertain cases need deeper analysis
2. **High-Impact User Roles**:
   - Finance department
   - HR department
   - Executive level

## Model Performance

**Dataset:** CEAS_08.csv (39,154 emails)
- Training: 31,323 emails (80%)
- Testing: 7,831 emails (20%)

**Metrics:**
- Accuracy: 99.39%
- Precision: 99.29%
- Recall: 99.61%
- F1-Score: 99.45%

**Confusion Matrix:**
```
                Predicted
                Safe    Phishing
Actual Safe     3,431   31
       Phishing 17      4,352
```

## Components

### 1. ML Classifier (`src/ml_classifier.py`)
- TF-IDF vectorization (5,000 max features)
- Logistic Regression classifier
- Returns risk score, classification, and top signal words
- Train/test evaluation with metrics

### 2. LLM Agent (`src/llm_agent.py`)
- Uses Google Gemini 2.0 Flash via OpenAI-compatible API
- Structured output (PhishingVerdict schema)
- Context-aware analysis combining email text + ML signals
- Does not blindly override ML score

### 3. Scanner Orchestrator (`src/scanner.py`)
- Coordinates ML + LLM pipeline
- Implements escalation logic
- Merges results into final verdict
- Async/await support for LLM calls

## Output Format

```python
{
    "source": "HYBRID (ML + LLM)",  # or "ML_ONLY"
    "risk_score": 76.0,
    "classification": "Phishing",
    "explanation": "The email has urgency phrases and domain mismatch...",
    "signals": [
        {"word": "urgent", "impact": 0.421},
        {"word": "verify", "impact": 0.318}
    ],
    "advice": "Do not click links. Report to IT security.",
    "llm_analysis": {  # Only if escalated
        "verdict": "Phishing",
        "reasoning": "Pressures quick action, sender mismatch...",
        "final_risk_score": 78.0
    }
}
```

## Project Structure

```
task_email/
├── src/                          # Source code
│   ├── __init__.py              # Package initialization
│   ├── scanner.py               # Main orchestrator
│   ├── ml_classifier.py         # ML model (TF-IDF + LogReg)
│   └── llm_agent.py             # LLM agent (Gemini)
│
├── documentation/                # Documentation
│   ├── EXAMPLES.md              # 3 example analyses
│   ├── REFLECTION.md            # Approach & future work
│   └── PROJECT_COMPLETION_SUMMARY.md
│
├── Example/                      # Example scripts
│   ├── generate_examples.py     # Example generator
│   └── example_outputs.json     # Generated results
│
├── README.md                     # Project overview (this file)
├── test_my_email.py              # Quick test script
├── CEAS_08.csv                   # Dataset (39K emails)
├── phishing_model.pkl            # Trained model
├── .env                          # API keys
└── pyproject.toml                # Dependencies
```

## Example Analyses

See `documentation/EXAMPLES.md` for detailed analysis of 3 test emails showing:
- ML-only decisions (clear safe/phishing)
- LLM escalation cases (borderline or high-impact users)
- Complete output with explanations

## Limitations & Future Work

See `documentation/REFLECTION.md` for:
- Approach justification
- Known failure modes
- Future improvement directions

## Complete Project Documentation

- **README.md** (this file) - Project overview and setup
- **documentation/EXAMPLES.md** - 3 detailed test cases
- **documentation/REFLECTION.md** - Technical analysis
- **documentation/PROJECT_COMPLETION_SUMMARY.md** - Completion checklist

## License

MIT License - Educational/Research Project
