# Run vLLM with openai/gpt-oss-120b
# Note: vLLM is typically recommended for Linux/WSL.
# Ensure 'uv' is installed: pip install uv

uv pip install --pre vllm==0.10.1+gptoss `
  --extra-index-url https://wheels.vllm.ai/gpt-oss/ `
  --extra-index-url https://download.pytorch.org/whl/nightly/cu128 `
  --index-strategy unsafe-best-match

vllm serve openai/gpt-oss-120b
