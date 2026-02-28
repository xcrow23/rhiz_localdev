# From Laptop to Lab: A Complete Local AI Fine-Tuning Roadmap

**Your path from Dell XPS 15 to professional workstation is entirely viable, and the current tools make this the best time to start.** As of December 2025, the open-source ecosystem has matured dramatically—Qwen2.5-Coder-32B now matches GPT-4o on coding benchmarks, QLoRA enables 7B fine-tuning on free Colab T4s, and frameworks like Unsloth and DSPy have lowered the barrier to entry substantially. Your phased approach aligns perfectly with how the community recommends learning: start with inference, progress to fine-tuning on cloud, then scale to local hardware as skills and budget grow.

---

## Laptop-scale experiments unlock real learning today

Your Dell XPS 15 without dedicated GPU can run **7B parameter models** at 5-15 tokens/second using CPU inference—slow but absolutely usable for learning and light experimentation. The key insight is that modern quantized models (Q4_K_M format) compress 7B models to ~4GB, fitting comfortably in 16GB RAM.

**Recommended first tools:**
- **Ollama** (`curl -fsSL https://ollama.com/install.sh | sh`): Best for developer workflows, provides OpenAI-compatible API, single command to run models
- **LM Studio**: GUI-based, easier for beginners, better at leveraging integrated GPUs
- **llama.cpp**: Maximum control for power users

**Best models for laptop coding work:**
| Model | Size | Command | Strength |
|-------|------|---------|----------|
| `qwen2.5-coder:7b` | ~4GB | `ollama run qwen2.5-coder:7b` | **Best-in-class coding** (84% HumanEval), 32K context |
| `deepseek-coder:6.7b` | ~4GB | `ollama run deepseek-coder:6.7b` | Strong Fill-in-Middle capability |
| `phi3:mini` | ~2GB | `ollama run phi3:mini` | Fastest, good for testing pipelines |

**Quantization matters:** The Q4_K_M format offers the best quality-to-size ratio with only +0.05 perplexity increase—nearly imperceptible quality loss while halving memory requirements.

**Laptop fine-tuning reality check:** Standard QLoRA requires GPU (bitsandbytes uses CUDA kernels). Intel Extension for Transformers enables CPU fine-tuning theoretically, but it takes days rather than hours. Your practical path forward is **Google Colab free tier**, which provides Tesla T4 (16GB VRAM) for ~12 hours/day—sufficient to fine-tune 7B models with QLoRA.

---

## Your first fine-tuning project should use Unsloth on Colab

The recommended first experiment is fine-tuning a small model on a specific task using **Unsloth**, which provides 2x faster training and 80% less VRAM than standard approaches—critical for working within Colab's constraints.

**Week 1 project: Custom coding assistant adapter**
```python
# On Google Colab (free tier)
!pip install unsloth transformers peft trl bitsandbytes

from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/llama-3.2-3b-instruct",  # Start small
    max_seq_length=2048,
    load_in_4bit=True
)
model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=32)

from trl import SFTTrainer, SFTConfig
trainer = SFTTrainer(
    model=model,
    train_dataset=your_dataset,  # 500-1000 examples
    args=SFTConfig(per_device_train_batch_size=2, gradient_accumulation_steps=4)
)
trainer.train()
trainer.save_model('my-first-adapter')  # ~50MB LoRA adapter
```

**Data preparation essentials:** Quality trumps quantity. **1,000 high-quality examples often beat 50,000 poor ones.** Use ShareGPT format for conversation data:
```json
{"conversations": [
  {"from": "human", "value": "Write a Python function to..."},
  {"from": "gpt", "value": "def solution():\n    ..."}
]}
```

**Critical hyperparameters to start:**
- Learning rate: **2e-4** (LoRA sweet spot)
- LoRA rank: **16** (balance of quality/efficiency)
- Alpha: **32** (2× rank is standard)
- Epochs: **1-2** for datasets over 5K examples
- Target modules: `"all-linear"` for best results

---

## Current fine-tuning best practices favor QLoRA and DoRA

**Parameter-efficient fine-tuning (PEFT)** has become the standard approach, with QLoRA reducing VRAM requirements by 60-80% compared to full fine-tuning.

| Method | VRAM Reduction | Quality Impact | When to Use |
|--------|---------------|----------------|-------------|
| **QLoRA** | 70-80% | Minimal | Consumer GPUs (RTX 4090 and below) |
| **LoRA** | 50-60% | None | When VRAM allows, slightly faster |
| **DoRA** | Similar to LoRA | +1-4% improvement | When you need maximum quality |
| **Full fine-tuning** | None | Best possible | Only with multi-GPU setups and 50K+ samples |

**Framework recommendations by experience level:**
- **Beginner**: **LLaMA-Factory** (web UI, zero code) or **Unsloth** (fastest setup)
- **Intermediate**: **Axolotl** (YAML configs, multi-GPU support)
- **Advanced**: **HuggingFace TRL + PEFT** (maximum customization)

**Avoiding overfitting—the #1 beginner mistake:**
- Use **1 epoch** for datasets >5K examples
- Monitor validation loss; stop if it starts increasing
- Apply dropout (0.05-0.1) in LoRA config
- Don't iterate multiple times on the same static dataset

---

## The hardware scaling path has clear capability tiers

Your $150 starting point doesn't mean waiting—cloud compute bridges the gap while you save.

### Phase 1: Cloud learning ($0-50/month)
| Platform | GPU | Free Tier | Best For |
|----------|-----|-----------|----------|
| Google Colab | T4 16GB | 12h/day | First experiments |
| Kaggle | T4/P100 | 30h/week | Larger datasets |
| Vast.ai | RTX 4090 | $0.24-0.60/hr | Production-quality training |
| RunPod | H100 | $1.99-2.79/hr | Large model experiments |

**Break-even analysis:** At $0.50/hour for RTX 4090 cloud, a $6,000 local system breaks even at ~12,000 hours. For 200 hours/month usage, that's 5 years. **Start with cloud, validate your workflows, then buy hardware.**

### Phase 2: First local GPU ($2,000-3,000)
**Best value: Used RTX 3090 ($650-750)**
- 24GB VRAM—same as RTX 4090
- Runs 70B Q4 models at 42 tok/s (vs 4090's 52 tok/s)
- Enables QLoRA fine-tuning up to 13-14B models
- NVLink support (unique to 30-series consumer cards)

Sample budget build (~$2,500):
- Used RTX 3090: $700
- Ryzen 7 7700X: $300
- 32GB DDR5: $130
- 2TB NVMe: $150
- B650 motherboard: $180
- 850W PSU: $120 (buy 1200W for future-proofing)

### Phase 3: Serious workstation ($5,000-7,000)
**Single RTX 4090 build** unlocks:
- 70B parameter inference at 52 tok/s
- QLoRA fine-tuning up to 32B models
- Full LoRA fine-tuning of 7B models
- Multiple concurrent model inference

### Phase 4: Professional setup ($12,000-15,000)
Two paths:
- **RTX A6000 (48GB)**: Unified VRAM, NVLink for 96GB combined, better for fine-tuning large models
- **Dual RTX 4090**: Higher throughput, no memory pooling (each GPU is separate)

**VRAM requirements by model size with QLoRA:**
| Model | Inference (Q4) | QLoRA Fine-tuning |
|-------|---------------|-------------------|
| 7B | 4GB | 8-12GB |
| 13B | 7GB | 10-16GB |
| 32B | 18GB | 18-24GB |
| 70B | 40GB | 46GB |

---

## The model landscape has clear winners for coding and reasoning

As of December 2025, **Qwen2.5-Coder** dominates coding benchmarks while **DeepSeek-R1** leads reasoning.

### Coding models by size tier:
| Size | Model | HumanEval | License |
|------|-------|-----------|---------|
| 7B | `Qwen/Qwen2.5-Coder-7B-Instruct` | 84.1% | Apache 2.0 |
| 14B | `Qwen/Qwen2.5-Coder-14B-Instruct` | ~86% | Apache 2.0 |
| 32B | `Qwen/Qwen2.5-Coder-32B-Instruct` | **92.7%** | Apache 2.0 |

**Qwen2.5-Coder-32B matches GPT-4o on coding benchmarks**—this is remarkable for an open-source model you can run locally.

### Reasoning models:
- **DeepSeek-R1** (671B/37B active): 97.3% MATH-500, comparable to OpenAI o1
- **DeepSeek-R1-Distill-Qwen-32B**: 94.3% MATH-500, runnable on single RTX 4090
- **DeepSeek-R1-Distill-Qwen-7B**: Strong reasoning in laptop-runnable size

### Your recommended model progression:
1. **Laptop**: `Qwen2.5-Coder-7B-Instruct` (Q4_K_M quantization)
2. **First GPU (3090)**: `Qwen2.5-Coder-14B` for inference, fine-tune 7B
3. **RTX 4090**: `Qwen2.5-Coder-32B` for inference, QLoRA on 14-32B
4. **Multi-GPU**: `DeepSeek-V3` (671B/37B active), fine-tune 70B models

**Licensing clarity:** Qwen2.5 (Apache 2.0) and DeepSeek (MIT) are fully permissive for commercial use and modification. Llama 3.x requires attribution and has a 700M MAU limit.

---

## Skill compression architecture is implementable today in stages

Your AGI-style skill compression vision has a practical pathway using current tools. The field has converged on **modular systems combining MoE, adapter composition, and retrieval-based routing**.

### What you can implement now:
| Capability | Tools | Hardware Needed |
|------------|-------|-----------------|
| MoE inference | Ollama, llama.cpp, vLLM | 24GB VRAM for Mixtral 8x7B |
| RAG with semantic search | LlamaIndex + ChromaDB | 8GB VRAM + 32GB RAM |
| LoRA fine-tuning | PEFT, Unsloth | 16GB VRAM |
| Model/LoRA merging | mergekit | CPU only (8GB RAM min) |
| Multi-agent coordination | CrewAI, AutoGen | 16GB VRAM |
| DSPy modular pipelines | DSPy | 16GB VRAM |
| Dynamic adapter loading | PEFT | 24GB VRAM |

### Implementation pathway for skill compression:

**Stage 1: Semantic skill retrieval (Weeks 1-4)**
Build a system that routes queries to appropriate skill modules:
```python
from llama_index import VectorStoreIndex, SimpleDirectoryReader
import chromadb

# Index your codebase and documentation
documents = SimpleDirectoryReader('skills/').load_data()
index = VectorStoreIndex.from_documents(documents)

# Query routes to relevant skill context
query_engine = index.as_query_engine(similarity_top_k=5)
```

**Stage 2: LoRA adapter library (Months 2-3)**
Create specialized adapters for different skills:
- Code generation adapter (fine-tuned on coding tasks)
- Documentation adapter (fine-tuned on technical writing)
- Reasoning adapter (fine-tuned on chain-of-thought examples)

Use **retrieval-based routing** to select appropriate adapter based on query embedding similarity.

**Stage 3: Adapter composition with mergekit (Months 3-4)**
Combine adapters dynamically:
```yaml
# mergekit config for skill composition
models:
  - model: base-model
  - model: coding-adapter
    parameters:
      weight: 0.7
  - model: reasoning-adapter
    parameters:
      weight: 0.3
merge_method: ties  # TIES-Merging handles interference
```

**Stage 4: Hierarchical coordination with DSPy (Months 4-6)**
DSPy provides the closest abstraction to "programmatic skill composition":
```python
import dspy

class SkillRouter(dspy.Module):
    def __init__(self):
        self.classify = dspy.Predict("query -> skill_type")
        self.coding = dspy.ChainOfThought("query -> code")
        self.reasoning = dspy.ChainOfThought("query -> analysis")
    
    def forward(self, query):
        skill = self.classify(query=query).skill_type
        if skill == "coding":
            return self.coding(query=query)
        return self.reasoning(query=query)
```

### Advanced research frontier (12+ months out):
- **Text-to-LoRA (Sakana AI)**: Hypernetwork generates task-specific adapters from text descriptions—single forward pass, no per-task training
- **Dynamic adapter generation**: Query-conditioned weight generation
- **Self-improving skill acquisition**: DSPy's MIPRO optimizer + bootstrapped examples

**Key repositories to study:**
- `github.com/stanfordnlp/dspy` - Modular AI programming
- `github.com/arcee-ai/mergekit` - Model merging (5,000+ stars)
- `github.com/SakanaAI/text-to-lora` - Hypernetwork adapter generation
- `github.com/crewAIInc/crewAI` - Multi-agent orchestration

---

## Infrastructure setup enables reproducible experimentation

**Recommended tool stack for individual researcher:**

| Category | Tool | Why |
|----------|------|-----|
| Experiment tracking | MLflow (local) | Free, self-hosted, no cloud dependency |
| Data versioning | DVC + Git | Git-like experience for datasets |
| Remote access | Tailscale | Zero-config VPN, direct device connection |
| GPU monitoring | nvitop | Interactive, PyTorch Lightning integration |
| Config management | Hydra | Dynamic configs, command-line overrides |
| Inference server | ExLlamaV2 (speed) or Ollama (simplicity) | Depends on use case |

**MLflow local setup:**
```bash
# Start tracking server
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
```
```python
import mlflow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.autolog()  # Automatic parameter and metric logging
```

**Checkpoint strategy (critical for long training runs):**
- Tier 1: Fast NVMe (every 10-30 min) - quick recovery
- Tier 2: Local SSD (every 1-2 hours) - medium-term
- Tier 3: Cloud backup (every 4-6 hours) - durable

**Storage requirements:**
| Data Type | Size | Recommendation |
|-----------|------|----------------|
| 7B model weights | 14GB (FP16), 4GB (Q4) | 2TB minimum |
| Training checkpoints | 200-500GB per experiment | 4TB recommended |
| Datasets | 10-100GB typical | Separate drive |

---

## A 6-month practical roadmap from your starting point

### Month 1: Foundation
**Week 1-2:** Install Ollama, run `qwen2.5-coder:7b` and `phi3:mini`. Complete HuggingFace Course Chapters 1-4. Budget: $0

**Week 3-4:** Set up Google Colab, complete first fine-tuning experiment with Unsloth. Join r/LocalLLaMA. Budget: $0

**Deliverable:** Working LoRA adapter fine-tuned on a small custom dataset.

### Month 2: Fine-tuning proficiency
**Week 5-6:** Fine-tune Qwen2.5-Coder-7B on your coding style. Use 500-1000 examples from your own code/projects.

**Week 7-8:** Implement basic RAG with LlamaIndex + ChromaDB over your documentation. Set up MLflow for experiment tracking.

**Deliverable:** Personal coding assistant with RAG that knows your projects.

### Month 3: Hardware decision point
**Week 9-10:** Evaluate used RTX 3090 market. Build GPU-ready base system if budget allows (~$1,800 without GPU).

**Week 11-12:** Continue cloud experiments. Try Vast.ai for larger model training (budget ~$50).

**Deliverable:** Working system infrastructure, clear hardware purchase plan.

### Month 4: First local GPU (if budget allows)
Install used RTX 3090 or RTX 4070 Ti Super. Run local inference and fine-tuning without cloud.

**New capabilities:** 70B model inference, 13B QLoRA fine-tuning, no time limits.

### Month 5: Skill specialization
Create LoRA adapter library:
- Coding adapter (Python, your frameworks)
- Documentation adapter
- Problem-solving adapter

Implement retrieval-based adapter routing.

### Month 6: Integration
Build DSPy pipeline combining:
- RAG for knowledge retrieval
- Adapter routing for skill selection
- Multi-step reasoning chains

**Deliverable:** Functional personal research assistant with modular skills.

---

## Common pitfalls and how to avoid them

1. **Starting with models too large:** Begin with 3B-7B, not 13B+. Larger models don't teach you the pipeline faster.

2. **Ignoring chat templates:** Models require specific formatting. Use `tokenizer.apply_chat_template()`.

3. **Overfitting on small datasets:** Use 1 epoch maximum for datasets over 5K examples. Monitor validation loss.

4. **Buying hardware too early:** Validate your workflows on cloud first. Your needs will become clearer.

5. **Not setting thread count:** For CPU inference, set threads = physical cores (not logical).

6. **Colab disconnection losses:** Save checkpoints to Google Drive every 30 minutes.

7. **Wrong quantization format:** Use Q4_K_M for the best quality/size balance on laptops.

---

## Conclusion: Your path is well-supported by current tools

The December 2025 landscape makes your goal achievable with methodical execution. **Qwen2.5-Coder-32B** and **DeepSeek-R1** represent genuine state-of-the-art available under permissive licenses. QLoRA on free Colab enables real fine-tuning from day one. DSPy, mergekit, and LlamaIndex provide the building blocks for sophisticated skill compression systems.

Your phased approach—laptop learning → cloud experiments → used RTX 3090 → eventual workstation—optimizes for learning while minimizing upfront investment. The skill compression research you're planning builds on established techniques (MoE, adapter composition, retrieval routing) with clear implementation pathways today, while remaining connected to frontier research (hypernetwork adapter generation, dynamic skill acquisition) that will mature over your timeline.

Start with Ollama and Qwen2.5-Coder-7B this week. Run your first Unsloth fine-tuning on Colab next week. The pipeline from there becomes progressively clearer as you gain hands-on experience with each component.