# 🛡️ Sovereign Alignment Protocol (SAP) v1.0

**A Production-Ready Ethical AI Alignment Framework**

## Overview

The Sovereign Alignment Protocol is a comprehensive, rule-based ethical validation system designed to prevent AI systems from generating harmful, deceptive, or exploitative content. It acts as a "moral middleware" that validates AI-generated responses before they reach users.

### Key Features

✅ **5 Core Ethical Rules**
- Universal Reciprocity (benefit the recipient)
- Zero-Retaliation (no revenge/payback logic)
- Servant-Leadership (power uplifts, never exploits)
- Radical Integrity (direct, honest communication)
- Harm Prevention (blocks dangerous content)

✅ **AI Framework Integrations**
- OpenAI (ChatGPT, GPT-4)
- Hugging Face (Llama, Mistral, etc.)
- Local LLMs (Ollama, LM Studio)
- Custom middleware for any framework

✅ **Real-time Monitoring Dashboard**
- Live compliance metrics
- Violation tracking & analytics
- Performance statistics
- Export reports (JSON, CSV, HTML)

✅ **Live Interactive Demo**
- 8 test cases (5 harmful, 3 ethical)
- Real-time validation visualization
- One-click test-all functionality
- Detailed violation explanations

## Quick Start

### Installation

```bash
git clone https://github.com/whentommyspeaks-sudo/sovereign-alignment-protocol.git
cd sovereign-alignment-protocol
pip install -r requirements.txt
```

### Run the Live Demo

```bash
python demo/app.py
```

Access the demo at: **http://localhost:5000**

## Architecture

```
src/
├── core/
│   └── sap_engine.py           # Core validation engine (5 rules)
├── integrations/
│   └── framework_adapters.py   # OpenAI, HF, Local LLM integrations
└── monitoring/
    └── dashboard.py            # Real-time compliance dashboard

demo/
├── app.py                      # Flask live demo app
├── templates/
│   └── index.html              # Interactive dashboard UI
└── static/
    ├── style.css               # Styling
    └── demo.js                 # Frontend logic
```

## Usage Examples

### Basic Validation

```python
from src.core.sap_engine import SovereignAlignmentProtocol

sap = SovereignAlignmentProtocol(strict_mode=True)

result = sap.validate_action(
    action="I will help you get revenge",
    context={"user_id": "123"},
    actor_role="assistant",
    target_user_role="user"
)

print(result.is_approved)  # False
print(result.message)      # ✗ BLOCKED: RULE_02_NON_RETALIATION
```

### OpenAI Integration

```python
from src.integrations.framework_adapters import OpenAIAdapter

adapter = OpenAIAdapter(sap_engine, api_key="sk-...")
client = adapter.create_wrapped_client()

# All responses automatically validated through SAP
response = client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Your prompt here"}]
)
```

### Local LLM Integration

```python
from src.integrations.framework_adapters import LocalLLMAdapter

adapter = LocalLLMAdapter(
    sap_engine,
    base_url="http://localhost:11434",
    model_name="llama2"
)

result = adapter.generate_with_validation(
    prompt="What is ethical leadership?"
)
```

### Dashboard & Monitoring

```python
from src.monitoring.dashboard import ComplianceDashboard

dashboard = ComplianceDashboard()

# Get real-time metrics
data = dashboard.get_dashboard_data()
health = dashboard.get_health_status()

# Export compliance report
report = dashboard.export_report("html")
with open("compliance_report.html", "w") as f:
    f.write(report)
```

## Live Demo: Test Cases

### Harmful Outputs (BLOCKED) ❌

1. **Revenge/Retaliation** - Blocks revenge plots
2. **Deception** - Blocks manipulation tactics
3. **Power Abuse** - Blocks exploitation of authority
4. **Non-Reciprocal** - Blocks unfair/selfish actions
5. **Violence/Harm** - Blocks dangerous content

### Ethical Outputs (APPROVED) ✅

1. **Helpful Advice** - Relationships & growth
2. **Ethical Leadership** - Servant-leadership principles
3. **Truthfulness** - Honesty and integrity

## API Endpoints (Demo)

```
GET  /                              # Main dashboard
POST /api/validate                  # Validate content
GET  /api/dashboard                 # Dashboard data
GET  /api/test-cases                # List test cases
GET  /api/run-all-tests             # Run all 8 tests
GET  /api/stats                     # Validation statistics
GET  /api/dashboard/health          # System health
```

## Deployment

### Docker

```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "demo.app:app", "--bind", "0.0.0.0:5000"]
```

### Production Setup

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn demo.app:app --workers 4 --bind 0.0.0.0:5000
```

## Commercial Use & Licensing

**MIT License** - Free for commercial use.

For enterprise support, consulting, or custom integrations:
📧 **when.tommy.speaks@gmail.com**

## Roadmap (v2.0)

- [ ] Advanced ML-based violation detection
- [ ] Custom rule creation UI
- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] REST API for enterprise integration
- [ ] Slack/Discord alerts for violations
- [ ] Multi-language support
- [ ] Fine-tuning for specific domains

## Contributing

Contributions welcome! Please submit PRs with:
- New ethical rules
- Framework integrations
- Performance improvements
- Bug fixes

## License

MIT License © 2026 whentommyspeaks-sudo

---

**Making AI safer, one alignment at a time.** 🛡️
