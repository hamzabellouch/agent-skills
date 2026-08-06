---
name: huggingface-transformers-nlp
metadata:
  category: NLP Audio and Speech AI
description: >-
  Build, fine-tune, and deploy enterprise NLP solutions using Hugging Face transformers, datasets, accelerate, and peft.
  Triggers when implementing QLoRA / LoRA fine-tuning, sequence classification, token classification (NER), SFTTrainer, DPO,
  vLLM serving, FlashAttention-2, or model quantization (BitsAndBytes, AWQ, GPTQ).
compatibility: Python (>= 3.9), PyTorch (>= 2.1), transformers (>= 4.38.0), peft, datasets, accelerate, vLLM
---

# Hugging Face Transformers & Enterprise NLP

Production patterns for parameter-efficient LLM fine-tuning (QLoRA), sequence classification, named entity recognition (NER), and high-throughput inference serving.

---

## 1. NLP Architecture & Fine-Tuning Workflow

```text
+-------------------+      +----------------------------------+      +---------------------------+
| Raw Text Dataset  | ---> | HF Datasets & Tokenizer          | ---> | 4-bit Quantized Base Model|
| (JSONL / Parquet) |      | (Dynamic Padding & Chunking)     |      | (BitsAndBytes NF4 Config) |
+-------------------+      +----------------------------------+      +---------------------------+
                                                                                  |
                                                                                  v
+-------------------+      +----------------------------------+      +---------------------------+
| Deployed LLM API  | <--- | Merge LoRA Adapters              | <--- | PEFT LoRA Fine-Tuning     |
| (vLLM / TGI Engine|      | (Base Model + Adapter Weights)   |      | (SFTTrainer / Accelerate) |
+-------------------+      +----------------------------------+      +---------------------------+
```

---

## 2. QLoRA Parameter-Efficient LLM Fine-Tuning (`qlora_finetune.py`)

Memory-efficient 4-bit quantized fine-tuning using `peft`, `bitsandbytes`, and `trl`'s `SFTTrainer`.

```python
import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer

def train_qlora_llm():
    MODEL_ID = "meta-llama/Meta-Llama-3-8B-Instruct"
    OUTPUT_DIR = "./qlora_llama3_output"

    # 1. 4-bit Quantization Configuration
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True
    )

    # 2. Load Model & Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="flash_attention_2"
    )

    model = prepare_model_for_kbit_training(model)

    # 3. LoRA Configuration
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )

    # 4. Load Dataset
    dataset = load_dataset("jsonl", data_files={"train": "train_instructions.jsonl"})

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        logging_steps=10,
        num_train_epochs=3,
        optim="paged_adamw_8bit",
        fp16=False,
        bf16=True,
        max_grad_norm=0.3,
        warmup_ratio=0.03,
        lr_scheduler_type="cosine",
        save_strategy="epoch",
        report_to="tensorboard"
    )

    # 6. Initialize SFTTrainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset["train"],
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args
    )

    # 7. Start Fine-Tuning
    trainer.train()

    # 8. Save LoRA Adapter Weights
    trainer.model.save_pretrained(os.path.join(OUTPUT_DIR, "final_adapter"))
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "final_adapter"))
    print("QLoRA Fine-Tuning Complete.")

if __name__ == "__main__":
    train_qlora_llm()
```

---

## 3. Sequence Classification & Named Entity Recognition (NER) (`ner_pipeline.py`)

A production pipeline for extracting domain entities (e.g. PER, ORG, LOC, MEDICINE) using RoBERTa.

```python
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

class NamedEntityExtractor:
    def __init__(self, model_checkpoint: str = "dslim/bert-base-NER"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        self.model = AutoModelForTokenClassification.from_pretrained(model_checkpoint)
        self.nlp_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple",  # Groups sub-word tokens
            device=0 if torch.cuda.is_available() else -1
        )

    def extract_entities(self, text: str) -> list[dict]:
        entities = self.nlp_pipeline(text)
        formatted = []
        for ent in entities:
            formatted.append({
                "entity_group": ent["entity_group"],
                "word": ent["word"],
                "score": round(float(ent["score"]), 4),
                "start": ent["start"],
                "end": ent["end"]
            })
        return formatted

if __name__ == "__main__":
    extractor = NamedEntityExtractor()
    results = extractor.extract_entities("Acme Corp acquired Therapeutics Inc in New York for $2 Billion.")
    print(results)
```

---

## 4. High-Throughput LLM Serving via vLLM (`serve_vllm.py`)

Deploy fine-tuned or open-source LLMs using vLLM for PagedAttention key-value cache optimization.

```python
from vllm import LLM, SamplingParams

def run_vllm_batch_inference():
    prompts = [
        "System: You are an AI legal expert.\nUser: Summarize the non-disclosure agreement obligations.\nAssistant:",
        "System: You are an AI code reviewer.\nUser: Explain Python memory management GIL.\nAssistant:"
    ]

    # Initialize vLLM engine with PagedAttention and Tensor Parallelism across 2 GPUs
    llm = LLM(
        model="meta-llama/Meta-Llama-3-8B-Instruct",
        tensor_parallel_size=1,
        gpu_memory_utilization=0.90,
        max_model_len=4096
    )

    sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.95,
        max_tokens=512
    )

    outputs = llm.generate(prompts, sampling_params)

    for output in outputs:
        prompt = output.prompt
        generated_text = output.outputs[0].text
        print(f"Prompt: {prompt!r}")
        print(f"Generated: {generated_text!r}\n")

if __name__ == "__main__":
    run_vllm_batch_inference()
```

---

## 5. Best Practices & Hardware Optimization

1. **FlashAttention-2**: Always pass `attn_implementation="flash_attention_2"` during model loading on Ampere/Hopper GPUs to reduce attention memory complexity from $O(N^2)$ to $O(N)$.
2. **Gradient Accumulation**: Match hardware VRAM constraints by lowering batch size (`per_device_train_batch_size=2`) and scaling up `gradient_accumulation_steps=8`.
3. **Model Merging**: Merge LoRA adapter weights into base model weights using `model.merge_and_unload()` before serving via vLLM engines to avoid runtime adapter attachment latency.
