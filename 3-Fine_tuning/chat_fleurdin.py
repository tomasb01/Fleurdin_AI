#!/usr/bin/env python3
"""
🌿 Fleurdin AI - Chat CLI
Povídej si s fine-tuned modelem přímo z terminálu!
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import AutoPeftModelForCausalLM
import torch

print("🌿 Načítám Fleurdin AI model...")
print("(První spuštění může trvat ~5 min - stahování modelu)")
print("-" * 60)

# Load model with LoRA adapters
model = AutoPeftModelForCausalLM.from_pretrained(
    "TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter",
    torch_dtype=torch.float16,
    device_map="auto",
    low_cpu_mem_usage=True
)

tokenizer = AutoTokenizer.from_pretrained(
    "TomasBo/Essention_oils-Mistral-7B-Instruct-v0.3-lora-adapter"
)

print("✅ Model načten!")
print("\n🌿 Fleurdin AI Chat")
print("Zeptej se na esenciální oleje (Ctrl+C pro ukončení)")
print("-" * 60)

conversation_history = []

while True:
    try:
        # Get user input
        user_input = input("\n💬 Ty: ")

        if not user_input.strip():
            continue

        # Build prompt with conversation history
        messages = conversation_history + [
            {"role": "user", "content": user_input}
        ]

        # Format with chat template
        prompt = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=300,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )

        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's response
        if "[/INST]" in response:
            assistant_response = response.split("[/INST]")[-1].strip()
        else:
            assistant_response = response[len(prompt):].strip()

        print(f"\n🤖 Fleurdin AI: {assistant_response}")

        # Update conversation history (keep last 3 exchanges)
        conversation_history.append({"role": "user", "content": user_input})
        conversation_history.append({"role": "assistant", "content": assistant_response})

        if len(conversation_history) > 6:  # Keep last 3 exchanges
            conversation_history = conversation_history[-6:]

    except KeyboardInterrupt:
        print("\n\n👋 Nashledanou!")
        break
    except Exception as e:
        print(f"\n❌ Chyba: {e}")
        continue
