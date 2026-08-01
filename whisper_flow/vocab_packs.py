"""Niche Vocabulary Packs for WhisperFlow.

Pre-compiled domain vocabulary terms passed to whisper.cpp --prompt and RAG engine
to ensure 100% acoustic decoding fidelity for specialized industries.
"""

from __future__ import annotations

VOCAB_PACKS: dict[str, list[str]] = {
    "general": [
        "WhisperFlow", "Wispr Flow", "whisper.cpp", "llama.cpp", "GGUF",
        "Python", "VS Code", "GitHub", "pytest", "API", "Gemma 4 E2B",
        "Claude 3.5 Opus", "Gemini Flash 3.6", "Qwen3-ASR", "CrispASR",
        "Zorin OS", "WSL", "Linux", "MongoDB", "Sam Altman", "Dario Amodei",
        "Demis Hassabis", "RAG", "Convolutional Networks", "embeddings",
        "vector store", "GRMR-2B-Instruct", "prompt engineering", "quantization",
    ],
    "developer": [
        "daemon.py", "OverlayNotifier", "HotkeyManager", "load_config", "save_config",
        "build_prompt", "detect_auto_intent", "apply_smart_formatting", "Pipeline",
        "TypeScript", "JavaScript", "Python", "Rust", "Golang", "C++", "React",
        "Next.js", "Docker", "Kubernetes", "PostgreSQL", "Redis", "GraphQL",
        "REST API", "git commit", "git push", "git checkout", "pull request",
        "refactor", "CI/CD", "middleware", "asyncio", "multivariable pointer",
        "RAG", "Convolutional Networks", "embeddings", "vector store", "gRPC",
        "protobuf", "WebAssembly", "WASM", "microservices", "serverless", "AWS Lambda",
        "Kubernetes ingress", "Helm chart", "Terraform", "Ansible", "CI/CD pipeline",
        "Kafka", "RabbitMQ", "Elasticsearch", "OpenSearch", "Prometheus", "Grafana",
        "WebSockets", "OAuth2", "JWT", "CORS", "rate limiting", "load balancer",
        "sharding", "indexing", "ACID compliance", "event loop", "garbage collection",
        "concurrency", "deadlock", "race condition", "mutex", "semaphore", "ThreadPool",
    ],
    "medical": [
        "anesthesia", "arrhythmia", "biopsy", "cardiovascular", "catheter",
        "dermatology", "echocardiogram", "electrocardiogram", "endoscopy",
        "gastroenterology", "hematology", "hypertension", "immunotherapy",
        "intravenous", "laparoscopy", "lymphoma", "metastasis", "neurology",
        "oncology", "pathology", "pharmacology", "radiology", "tachycardia",
        "cardiology", "clinical trials", "dosing", "analgesic", "antibiotic",
        "anticoagulant", "antihypertensive", "arthrosynthesis", "brisk reflexes",
        "bronchoscopy", "carcinoma", "cerebrovascular", "chemotherapy",
        "cholesterol", "computed tomography", "CT scan", "MRI scan", "dialysis",
        "dyspnea", "edema", "electroencephalogram", "EEG", "embolism",
        "etiology", "exacerbation", "fibrosis", "hematoma", "hemoglobin",
        "histopathology", "hypoglycemia", "ischemia", "leukemia", "leukocytosis",
        "magnetic resonance imaging", "mammography", "melanoma", "myocardial infarction",
        "nephrology", "ophthalmology", "orthopedics", "osteoporosis", "palliative care",
        "palpation", "phlebotomy", "pneumonia", "prognosis", "psychiatry",
        "pulmonology", "radiotherapy", "sepsis", "tachycardic", "thrombosis",
        "ultrasound", "vasodilator", "vital signs",
    ],
    "legal": [
        "affidavit", "affidavits", "arbitration", "brief", "class action", "clause",
        "compliance", "confidentiality agreement", "contract", "counsel",
        "defendant", "deposition", "due diligence", "indemnity", "indemnities", "injunction",
        "intellectual property", "jurisdiction", "liability", "litigation", "litigations",
        "non-disclosure agreement", "plaintiff", "statute of limitations",
        "adjudication", "admissibility", "amicus curiae", "appellate court",
        "burden of proof", "case law", "certiorari", "civil litigation",
        "claimant", "codicil", "compensatory damages", "cross-examination",
        "decedent", "declaratory judgment", "default judgment", "discovery phase",
        "easement", "force majeure", "habeas corpus", "hearsay", "indictment",
        "interrogatories", "joinder", "judgment creditor", "jurisprudence",
        "liens", "liquidated damages", "mediation", "motion to dismiss",
        "motion for summary judgment", "negligence", "power of attorney",
        "precedent", "prima facie", "punitive damages", "subpoena", "torts",
        "trustee", "unconscionable", "venue", "verdict", "voir dire",
    ],
    "corporate": [
        "deliverable", "deliverables", "key performance indicator", "KPI", "KPIs", "OKR", "OKRs", "action item",
        "stakeholder", "alignment", "synergy", "ROI", "return on investment",
        "quarterly review", "roadmap", "go-to-market", "GTM strategy",
        "bandwidth", "bottom line", "core competency", "touchpoint", "onboarding",
        "mumbo jumbo", "corporate mumbo jumbo", "B2B sales", "B2C enterprise",
        "churn rate", "customer acquisition cost", "CAC", "lifetime value", "LTV",
        "net promoter score", "NPS", "annual recurring revenue", "ARR",
        "monthly recurring revenue", "MRR", "gross margin", "EBITDA",
        "pipeline conversion", "value proposition", "scalability", "change management",
        "cross-functional", "deliverable timeline", "executive summary",
        "headcount", "market penetration", "milestone", "pivot", "runway",
        "strategic initiative", "thought leadership", "up-selling", "workstream",
    ],
    "finance": [
        "amortization", "asset allocation", "balance sheet", "basis points", "bps",
        "capital expenditure", "CapEx", "operating expenditure", "OpEx",
        "cash flow statement", "collateral", "compound interest", "credit default swap",
        "derivatives", "discounted cash flow", "DCF", "dividend yield", "equity",
        "hedge fund", "initial public offering", "IPO", "liquidity", "margin call",
        "mutual fund", "net present value", "NPV", "portfolio diversification",
        "private equity", "quantitative easing", "return on equity", "ROE",
        "risk tolerance", "securities", "sovereign debt", "valuation", "yield curve",
    ],
    "academic": [
        "abstract", "acknowledgments", "annotated bibliography", "citation",
        "control group", "correlation coefficient", "data synthesis",
        "empirical evidence", "ethnography", "epistemology", "hypothesis",
        "literature review", "methodology", "meta-analysis", "null hypothesis",
        "p-value", "peer review", "qualitative research", "quantitative analysis",
        "randomized controlled trial", "sample size", "standard deviation",
        "statistical significance", "systematic review", "theoretical framework",
    ],
}


def get_vocab_pack(name: str) -> list[str]:
    """Retrieve vocabulary terms for the specified domain pack."""
    return VOCAB_PACKS.get(name.lower(), VOCAB_PACKS["general"])


def list_vocab_packs() -> list[str]:
    """Return available vocabulary pack names."""
    return list(VOCAB_PACKS.keys())
