# Rhiz Training Loop Design

## Overview

This document describes the iterative training loop for improving Qwen's filesystem capabilities within the Rhiz project.

## Philosophy: Alignment Signals, Not Pavlovian Rewards

The "reward function" terminology is borrowed from reinforcement learning, but it's a misnomer that obscures what's actually happening:

| Pavlovian Framing | Reality |
|-------------------|---------|
| Model "experiences" reward | Model has no experience - it's matrix operations |
| Model "wants" to get treats | Model has no wants - outputs are probability distributions |
| We're conditioning behavior | We're reshaping probability landscapes via gradients |
| Reward is arbitrary human preference | Score is verifiable correctness signal |

For Rhiz, we use **alignment signals** - verifiable indicators that an output moved toward our mutually agreed goals.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Training Loop                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   Dataset   │───▶│   Qwen 7B   │───▶│   Score     │         │
│  │  Generator  │    │  (Ollama)   │    │  Function   │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│        │                   │                  │                 │
│        │                   │                  │                 │
│        ▼                   ▼                  ▼                 │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Atropos Trajectory API                 │       │
│  │  - Collects rollouts                               │       │
│  │  - Batches for training                            │       │
│  │  - Tracks metrics (wandb)                          │       │
│  └─────────────────────────────────────────────────────┘       │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              Gradient Update (QLoRA)                │       │
│  │  - Low-rank adaptation for 16GB RAM               │       │
│  │  - Preserves base model capabilities              │       │
│  └─────────────────────────────────────────────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Components Created

### 1. Filesystem Tools (`core/tools/filesystem_tools.py`)
- `read_file`: Read file contents
- `write_file`: Write/append to files
- `list_directory`: List directory contents
- `file_exists`: Check path existence
- Sandboxed to Rhiz_LocalDev for safety

### 2. Qwen Agent (`core/tools/qwen_agent.py`)
- Interactive agent loop for Qwen via Ollama
- Automatic tool call handling
- Conversation history management

### 3. Training Environment (`core/training/rhiz_filesystem_env.py`)
- Training dataset generator
- Scoring function for tool calls
- Execution verification
- Template for atropos integration

## The Score Function

```python
def score_tool_call(model_output, expected_tool, expected_args):
    """
    Returns 0.0 to 1.0 based on correctness:
    - 1.0: Correct tool with correct arguments
    - 0.5: Correct tool, partial argument match
    - 0.0: Wrong tool or malformed output
    """
```

This is NOT arbitrary preference. It's **verifiable correctness**:
- Did the model call `read_file` when asked to read a file? (checkable)
- Did it provide the correct path? (checkable)
- Did the file operation succeed? (checkable)

## Training Process

### Phase 1: Inference Testing (Current)
1. Start Ollama: `ollama serve`
2. Run agent: `python core/tools/qwen_agent.py`
3. Test filesystem operations manually
4. Verify tool calling works

### Phase 2: Dataset Generation
1. Generate training samples: `python core/training/rhiz_filesystem_env.py`
2. Review and curate samples
3. Add domain-specific tasks (permaculture queries, design files)

### Phase 3: RL Training with Atropos
1. Install atropos: `pip install atroposlib`
2. Set up training server
3. Run training loop:
```bash
# Start trajectory API
run-api

# Start filesystem environment
python environments/rhiz_filesystem_server.py serve \
    --openai.model_name qwen2.5-coder:7b \
    --slurm false
```

### Phase 4: Fine-tuning with QLoRA
For weight updates (not just RL):
```bash
# Using transformers + peft
python train_qlora.py \
    --model qwen2.5-coder:7b \
    --dataset rhiz_filesystem_dataset.json \
    --output rhiz-qwen-filesystem-v1
```

## Hardware Considerations

| Constraint | Mitigation |
|------------|------------|
| 16GB RAM | Use 4-bit quantization, QLoRA |
| No GPU | CPU inference (slower but works) |
| Limited storage | Keep checkpoints minimal |

## browser-use Integration

The browser-use repo can enhance training by:
1. Gathering real-world permaculture data
2. Downloading documentation/research
3. Creating training samples from web content

Location: `Gifts_From_Alex/browser-use-main/`

## Next Steps

1. [ ] Test Qwen agent with Ollama running
2. [ ] Generate initial training dataset (100-500 samples)
3. [ ] Set up wandb for training metrics
4. [ ] Create first training run (50-100 steps)
5. [ ] Evaluate and iterate

## Resources

- **Atropos**: `Gifts_From_Alex/atropos-main/`
- **DataTrove**: `Gifts_From_Alex/datatrove-main/` (for data processing)
- **Hermes Function Calling**: `Gifts_From_Alex/Hermes-Function-Calling-main/`
- **Qwen Docs**: https://qwen.readthedocs.io/en/latest/framework/function_call.html
- **Ollama Tool Calling**: https://docs.ollama.com/capabilities/tool-calling
