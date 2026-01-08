# OpenAI GPT-OSS Model Demo

This project contains scripts to run the `openai/gpt-oss-120b` open-weights model.

## Model Details

- **Model Standard**: `openai/gpt-oss-120b`
- **Parameters**: 117B (5.1B active)
- **Requirements**: ~80GB VRAM (e.g., NVIDIA H100) or massive System-RAM for CPU offload (very slow).
- **Alternative**: `open/gpt-oss-20b` (Requires ~16GB Ram).

## Scripts

### 1. Ollama (Recommended)

**Status:** ✅ Working
**File:** `run_ollama.ps1` or `run_ollama_api.py` (Python)
**Usage:**

```powershell
# Interactive Mode
ollama run gpt-oss:20b

# Python API Mode
python run_ollama_api.py
```

This is the most efficient way to run the model on standard hardware (supports NVIDIA T1000/consumer GPUs).

### 2. Transformers (Python)

**Status:** ⚠️ Experimental / High Hardware Req
**File:** `run_transformers.py`
**Usage:**

```bash
python run_transformers.py
```

**Warning:** Requires massive VRAM (>40GB for 20B model in fp16, or specialized Triton kernels for MXFP4). Not recommended for Windows/Consumer GPUs.

### 3. vLLM

**Status:** 🐧 Linux Only
**File:** `run_vllm.ps1`
**Note:** Requires WSL2 or Linux.

## Note

Running the 120B model on a standard consumer laptop or desktop will likely result in an **Out of Memory (OOM)** error or extremely slow performance. Consider switching the model ID to `openai/gpt-oss-20b` in the scripts if you encounter issues.
