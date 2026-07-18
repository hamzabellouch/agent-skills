---
name: local-model-finetuning-unsloth-axolotl
description: High-performance local LLM fine-tuning, DPO/ORPO preference alignment, and QLoRA/LoRA optimization using Unsloth and Axolotl. Covers VRAM footprint minimization, FlashAttention-2, gradient checkpointing, FSDP/DeepSpeed multi-GPU scaling, dataset formatting, and GGUF/vLLM export.
---

# Local LLM Fine-Tuning Architect Skill: Unsloth & Axolotl

## 1. Framework Architectural Comparison

| Dimension | Unsloth | Axolotl |
| :--- | :--- | :--- |
| **Primary Target** | Single-GPU extreme speed & VRAM optimization | Multi-GPU / Multi-Node enterprise scale |
| **Backend Implementation** | Custom C++/CUDA & Triton kernels (manual backprop) | HuggingFace Transformers, PyTorch FSDP, DeepSpeed |
| **Interface** | Python API (Extends `trl` & `peft`) | YAML Configuration Driven CLI |
| **Speedup vs Standard** | 2x – 5x faster training | Standard PyTorch + FlashAttention-2 optimizations |
| **Memory Footprint** | Up to 80% VRAM reduction | Standard QLoRA/LoRA VRAM scaling |
| **Alignment Algorithms** | SFT, DPO, ORPO, GRPO | SFT, DPO, ORPO, KTO, PPO, ReFT |
| **Model Architectures** | Llama 3/3.1/3.2, Qwen 2.5, Mistral, Gemma 2, Phi-4 | Broad HF ecosystem support (Llama, Qwen, Mistral, etc.) |

---

## 2. Memory Optimization & Hardware Configurations

### VRAM Budgeting Matrix (8B Model @ 4096 Sequence Length)

| Method | Quantization | Batch Size (per GPU) | Min VRAM Required | Optimal Hardware |
| :--- | :--- | :--- | :--- | :--- |
| **Unsloth QLoRA** | 4-bit (NF4) | 2 – 4 | 7 GB – 10 GB | RTX 3090 / RTX 4090 / A10G |
| **Unsloth LoRA** | 16-bit (BF16) | 1 – 2 | 16 GB – 20 GB | RTX 4090 / A100 (40GB) |
| **Axolotl QLoRA (FSDP)** | 4-bit (NF4) | 4 – 8 (across 4 GPUs) | 12 GB per GPU | 4x RTX 3090 / 4x A10G |
| **Axolotl Full Params (DeepSpeed Z3)**| 16-bit (BF16) | 2 – 4 (across 8 GPUs) | 40 GB per GPU | 8x A100 (80GB) / H100 |

### Key Optimization Knobs
- **NF4 & Double Quantization**: Uses 4-bit NormalFloat data type with quantized quantization constants to save ~0.5 bit per parameter.
- **Paged AdamW 8-bit**: Offloads optimizer state spikes to CPU memory during peak backpropagation passes.
- **Gradient Checkpointing (Unsloth Offloading)**: Recomputes activations during backpass instead of storing them all in RAM. Unsloth reduces activation memory footprint by 50-70%.
- **Sample Packing / Multipack**: Concatenates short samples into a single sequence up to max token length, eliminating padding token waste and accelerating training by 2x-4x.

---

## 3. Best Practices & Anti-Patterns

### Best Practices
- **Target All Linear Modules**: Always apply LoRA matrices to all linear projections (`q_proj`, `k_proj`, `v_proj`, `o_proj`, `gate_proj`, `up_proj`, `down_proj`) rather than just Attention vectors to maintain model reasoning quality.
- **Set $\alpha = 2 \times r$ or $\alpha = r$**: Maintain stable scaling ratio for LoRA rank ($r=16, \alpha=32$ or $r=32, \alpha=32$).
- **Use Warmup & Cosine Decay**: Start with a small learning rate warmup (5–10% of total steps) with `learning_rate = 2e-4` for QLoRA and `2e-5` for full tuning.
- **Proper EOS / ChatML Formatting**: Ensure prompt templates append exact `<|end_of_text|>` or system end tokens to prevent runaway model generation during inference.

### Anti-Patterns
- ❌ **Over-tuning on Small Datasets**: Setting `epochs > 3` on small instruction datasets (<2,000 samples), causing severe catastrophic forgetting.
- ❌ **Padding Without Packing**: Batching sequences with heavy zero-padding without sequence packing enabled, wasting up to 60% of GPU compute on padding tokens.
- ❌ **Mixing Precision Types**: Training in FP16 on older Ampere/Hopper GPUs when BF16 is natively supported, leading to numerical underflow/overflow NaN loss values.
- ❌ **Saving Full Unmerged Model**: Saving 4-bit adapter weights without exporting GGUF or merging 16-bit base weights for inference deployments.

---

## 4. Production Code Implementations

### A. Unsloth (Python) - 4-bit QLoRA SFT Training & GGUF Export

```python
import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments

MAX_SEQ_LENGTH = 4096
DTYPE = None  # None for auto detection (Float16 for Tesla T4/V100, Bfloat16 for Ampere+)
LOAD_IN_4BIT = True  # Enable 4bit NF4 quantization

# 1. Load Model & Tokenizer
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen2.5-7B-Instruct",
    max_seq_length=MAX_SEQ_LENGTH,
    dtype=DTYPE,
    load_in_4bit=LOAD_IN_4BIT,
)

# 2. Add Fast LoRA Adapters
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA Rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    lora_alpha=32,
    lora_dropout=0,  # Optimized to 0 in Unsloth
    bias="none",
    use_gradient_checkpointing="unsloth",  # Unsloth smart checkpointing
    random_state=3407,
)

# 3. Format Dataset (ChatML Format)
dataset = load_dataset("philschmid/dolly-15k-oai-style", split="train")

def format_prompts(examples):
    texts = [tokenizer.apply_chat_template(convo, tokenize=False) for convo in examples["messages"]]
    return {"text": texts}

dataset = dataset.map(format_prompts, batched=True)

# 4. Configure Trainer
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=MAX_SEQ_LENGTH,
    dataset_num_proc=4,
    packing=True,  # Pack multiple sequences into max_seq_length
    args=TrainingArguments(
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_ratio=0.05,
        max_steps=60,
        learning_rate=2e-4,
        fp16=not torch.cuda.is_bf16_supported(),
        bf16=torch.cuda.is_bf16_supported(),
        logging_steps=10,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        output_dir="outputs",
    ),
)

# 5. Execute Fast Training & Export to GGUF
trainer.train()

# Save merged 16bit model or GGUF for Ollama/vLLM
model.save_pretrained_gguf("model_q4_k_m", tokenizer, quantization_method="q4_k_m")
```

### B. Axolotl (YAML Config & Multi-GPU Launch Command)

#### `axolotl_config.yaml`
```yaml
base_model: meta-llama/Meta-Llama-3.1-8B-Instruct
model_type: AutoModelForCausalLM
tokenizer_type: AutoTokenizer

load_in_8bit: false
load_in_4bit: true
strict: false

datasets:
  - path: vicgalle/alpaca-gpt4
    type: alpaca

dataset_prepared_path: last_run_prepared
val_set_size: 0.05
output_dir: ./completed-llama3-qlora

sequence_len: 4096
sample_packing: true
pad_to_sequence_len: true

adapter: qlora
lora_r: 32
lora_alpha: 64
lora_dropout: 0.05
lora_target_linear: true

gradient_accumulation_steps: 4
micro_batch_size: 2
num_epochs: 3
optimizer: paged_adamw_8bit
lr_scheduler: cosine
learning_rate: 0.0002

train_on_inputs: false
group_by_length: false
bf16: auto
fp16: false

gradient_checkpointing: true
early_stopping_patience:
local_rank:
logging_steps: 10
xformers_attention:
flash_attention: true

warmup_steps: 50
evals_per_epoch: 1
saves_per_epoch: 1
debug:
deepspeed: deepspeed_configs/zero2.json
```

#### Multi-GPU Execution Command:
```bash
accelerate launch -m axolotl.cli.train axolotl_config.yaml
```
