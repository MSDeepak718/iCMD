from transformers import AutoModelForCausalLM
from peft import PeftModel

base_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/Phi-3-mini-4k-instruct",
    trust_remote_code=True
)

model = PeftModel.from_pretrained(base_model, "phi3-lora")
model = model.merge_and_unload()
model.save_pretrained("phi3-icmd")