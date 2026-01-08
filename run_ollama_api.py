import requests
import json

# Configuration
model_id = "gpt-oss:20b"
url = "http://localhost:11434/api/generate"

print(f"Connecting to Ollama via API to run {model_id}...")

prompt = "Explain quantum dynamics in 2 sentences."
data = {
    "model": model_id,
    "prompt": prompt,
    "stream": False
}

try:
    print("Sending request...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("\nResponse from Ollama:")
        print("-" * 40)
        print(result.get("response"))
        print("-" * 40)
        print(f"Duration: {result.get('total_duration') / 1e9:.2f} seconds")
    else:
        print(f"Error: {response.status_code} - {response.text}")

except Exception as e:
    print(f"\nConnection failed: {e}")
    print("Ensure Ollama is running (`ollama serve` or just having the app open).")
