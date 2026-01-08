from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
import torch

# Note: The 120B model is extremely large.
# Switching to the 20B model for local compatibility.
model_id = "openai/gpt-oss-20b" 

print(f"Loading model: {model_id}...")
print("Warning: This model is very large. Ensure you have sufficient hardware.")

# quantization config
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)

try:
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    
    print("Loading model (this may take a while)...")
    # The model is already quantized (MXFP4), so we don't pass BitsAndBytesConfig.
    # It should load automatically if the environment supports it (or falls back).
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        trust_remote_code=True
    )

    print("Creating pipeline...")
    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

    messages = [
        {"role": "user", "content": "Explain quantum mechanics clearly and concisely."},
    ]

    print("Generating response...")
    outputs = pipe(
        messages,
        max_new_tokens=256,
    )
    print("\nGenerated Text:")
    print(outputs[0]["generated_text"][-1])

except Exception as e:
    print(f"\nAn error occurred: {e}")
    # Print full traceback for debugging
    import traceback
    traceback.print_exc()

