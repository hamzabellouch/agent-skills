# Google Gemma Models & Ecosystem

This sub-specialty provides production-grade agent skills for developing, deploying, adapting, and fine-tuning **Google Gemma** models (Gemma 4 with Thinking Mode, Gemma 3, ShieldGemma, and EmbeddingGemma).

---

## Skills in This Directory

| Skill | Focus & Capabilities |
| :--- | :--- |
| [`gemma-dev`](gemma-dev/) | Application development, model selection (Gemma 4 31B, 26B A4B MoE, 12B Audio/Vision, E2B/E4B on-device), Gradio prototypes, WebGPU with `transformers.js`, Vertex AI cloud deployment, Apple Silicon MLX, Multi-Token Prediction (MTP), and Quantization-Aware Training (QAT). |
| [`gemma-trainer`](gemma-trainer/) | Local fine-tuning and alignment (SFT, DPO, RLHF, Reward Modeling) using Unsloth (up to 70% less VRAM on single GPUs) or Hugging Face TRL + PEFT + QLoRA (4-bit), dataset preparation, student-teacher distillation, and conversion to GGUF / LiteRT. |

---

## Quick Start

### 1. Gemma App Development (`gemma-dev`)
```bash
cd gemma-dev
pip install -r requirements.txt
python assets/gradio-app.py
```

### 2. Gemma Fine-Tuning (`gemma-trainer`)
```bash
cd gemma-trainer
pip install -r requirements.txt

# Validate your SFT / DPO dataset:
python assets/dataset_prep.py --file path/to/dataset.jsonl --type sft

# Launch QLoRA fine-tuning:
python assets/sft_train.py --model_name google/gemma-4-E2B-it --dataset_path path/to/dataset.jsonl
```
