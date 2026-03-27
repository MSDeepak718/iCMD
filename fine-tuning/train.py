import os
from pathlib import Path

os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

import torch
from datasets import load_dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
DATASET_PATH = Path(__file__).with_name("complex_linux_commands_million.json")
OFFLOAD_DIR = Path(__file__).with_name("offload")

OFFLOAD_DIR.mkdir(exist_ok=True)

if not torch.cuda.is_available():
    raise RuntimeError(
        "CUDA is not available. Fix the NVIDIA driver/CUDA setup first, then rerun this script."
    )

gpu_name = torch.cuda.get_device_name(0)
total_memory_gib = torch.cuda.get_device_properties(0).total_memory / 1024**3
gpu_budget_gib = max(1, int(total_memory_gib - 2))
use_bf16 = torch.cuda.is_bf16_supported()
compute_dtype = torch.bfloat16 if use_bf16 else torch.float16

print(f"Using GPU: {gpu_name}")
print(f"Total VRAM: {total_memory_gib:.2f} GiB")
print(f"Compute dtype: {'bfloat16' if use_bf16 else 'float16'}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

config = AutoConfig.from_pretrained(MODEL_NAME, trust_remote_code=True)

if config.model_type == "phi3" and config.rope_scaling:
    rope_scaling = dict(config.rope_scaling)
    rope_type = rope_scaling.get("rope_type")
    if rope_type == "default":
        config.rope_scaling = None
    else:
        if rope_type and "type" not in rope_scaling:
            rope_scaling["type"] = rope_type
        config.rope_scaling = rope_scaling

config._attn_implementation = "eager"

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=False,
    bnb_4bit_compute_dtype=compute_dtype,
)

max_memory = {
    0: f"{gpu_budget_gib}GiB",
    "cpu": "48GiB",
}

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    config=config,
    quantization_config=quantization_config,
    device_map="auto",
    max_memory=max_memory,
    offload_folder=str(OFFLOAD_DIR),
    offload_state_dict=True,
    low_cpu_mem_usage=True,
    dtype=compute_dtype,
    attn_implementation="eager",
    trust_remote_code=True,
)

model.config.use_cache = False
model.gradient_checkpointing_enable()

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.05,
    bias="none",
    task_type="CAUSAL_LM",
)

model = get_peft_model(model, lora_config)


def format_example(example):
    return {
        "text": f"<|user|>\n{example['input']}\n<|assistant|>\n{example['output']}"
    }


dataset = load_dataset("json", data_files=str(DATASET_PATH))
dataset = dataset.map(format_example)

training_args = TrainingArguments(
    output_dir="./phi3-qlora",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=not use_bf16,
    bf16=use_bf16,
    optim="paged_adamw_8bit",
    gradient_checkpointing=True,
    logging_steps=10,
    save_total_limit=2,
    report_to="none",
)

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset["train"],
    processing_class=tokenizer,
    args=training_args,
)

trainer.train()

model.save_pretrained("phi3-lora")
tokenizer.save_pretrained("phi3-lora")
