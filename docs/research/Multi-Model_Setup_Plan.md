# Local AI Multi-Model Setup Plan
**Goal:** Set up DeepSeek-R1-Distill-Qwen-7B and Llama 3.2 for side-by-side comparison with persistent conversation management

## Overview
This plan sets up a dual-model local AI environment using Ollama with:
- **DeepSeek-R1-Distill-Qwen-7B**: Pre-merged model combining DeepSeek reasoning + Qwen architecture
- **Llama 3.2**: Meta's latest general-purpose model
- **Open WebUI**: ChatGPT-like interface for persistent conversations and model switching

## Phase 1: Pull Required Models

### 1.1 DeepSeek-R1-Distill-Qwen-7B
```powershell
ollama pull deepseek-r1:7b
```
- Size: ~4.7GB
- Strengths: Strong reasoning, math problem-solving
- Already integrates DeepSeek + Qwen architecture

### 1.2 Llama 3.2
```powershell
ollama pull llama3.2:latest
```
- Size: ~2GB (3B params) or ~5GB (if 8B variant available)
- Strengths: General purpose, strong instruction following
- Good baseline comparison

### 1.3 Qwen2.5-Coder-7B (Already Pulling)
```powershell
ollama pull qwen2.5-coder:7b
```
- Size: ~4.7GB
- Strengths: Best-in-class coding (84% HumanEval)

## Phase 2: Verify Models Are Running

### 2.1 Test Each Model via CLI
```powershell
# Test DeepSeek-R1
ollama run deepseek-r1:7b

# Test Llama 3.2
ollama run llama3.2:latest

# Test Qwen Coder
ollama run qwen2.5-coder:7b
```

### 2.2 Quick Benchmark Test
Ask each model the same question to compare:
- Coding task: "Write a Python function to find prime numbers using the Sieve of Eratosthenes"
- Reasoning task: "If a train leaves NYC at 60mph and another leaves Boston at 80mph, 220 miles apart, when do they meet?"
- General knowledge: "Explain how transformers work in neural networks"

## Phase 3: Install Open WebUI for Persistent Conversations

### 3.1 Pull and Run Open WebUI Container
```powershell
docker run -d -p 3000:8080 --add-host=host.docker.internal:host-gateway -v open-webui:/app/backend/data --name open-webui ghcr.io/open-webui/open-webui:main
```

### 3.2 Access Interface
- Navigate to `http://localhost:3000`
- Create account (local only, no cloud)
- All three models will auto-appear in the dropdown

### 3.3 Configure Model Preferences
- Set default model (recommend DeepSeek-R1 for reasoning)
- Enable conversation history
- Configure system prompts per model if needed

## Phase 4: Create Comparison Workflow

### 4.1 Model Selection Strategy
Create mental (or documented) routing rules:
- **Coding tasks** → Qwen2.5-Coder-7B
- **Math/reasoning** → DeepSeek-R1-Distill-Qwen-7B
- **General chat/writing** → Llama 3.2
- **Comparison testing** → Ask all three the same question

### 4.2 Document First Impressions
After testing, create notes in `LocalAI_Project/`:
- Which model feels most "Claude-like" in conversation?
- Speed comparison (tokens/second)
- Quality differences for your specific use cases

## Phase 5: Documentation and Next Steps

### 5.1 Create Quick Reference Guide
Document in `LocalAI_Project/model_usage_guide.md`:
- How to start/stop models
- Open WebUI access URL
- Model strengths matrix
- Common commands

### 5.2 Future Enhancements
- Set up Continue.dev in VSCode with Qwen2.5-Coder
- Experiment with model parameters (temperature, context length)
- Create custom system prompts for each model
- Explore RAG integration with your documents

## Critical Files & Locations
- **Ollama models**: `%USERPROFILE%\.ollama\models\`
- **Open WebUI data**: Docker volume `open-webui`
- **Project docs**: `C:\Users\dread\Documents\LocalAI_Project\`

## Success Criteria
✅ All three models pulled and tested
✅ Open WebUI running with persistent conversations
✅ Clear understanding of which model excels at which tasks
✅ Documentation created for future reference
✅ Can switch between models seamlessly in Open WebUI

## Estimated Time
- Model downloads: 10-15 minutes (depending on connection)
- Testing: 15-20 minutes
- Open WebUI setup: 5-10 minutes
- Documentation: 10-15 minutes
- **Total: ~45-60 minutes**

## Notes
- All models run locally - no cloud dependency once pulled
- Open WebUI provides the "evolving conversation" experience similar to Claude Desktop
- Docker Desktop must remain running for Open WebUI
- Models persist after download - only need to pull once
