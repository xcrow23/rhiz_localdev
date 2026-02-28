# Blog Image Generation - Options & Research

**Current Approach:** Manual generation (Jan 2026)
- Captain generates 2 images, Daemon generates 2 images
- Joint prompt crafting process
- High quality, fast results
- Works well for 1-2 posts/week cadence

## Future Automation Options

### Option 1: HuggingFace Inference Providers
**Status:** Researched, not cost-effective for regular use

**Free Tier:**
- $0.10/month credits for free users
- ~83 images/month max (~20 blog posts)
- No pay-as-you-go without PRO subscription

**PRO Tier ($9/month):**
- $2.00/month credits + pay-as-you-go
- Cost: ~$0.0012 per FLUX.1-dev image
- Viable if blog generates revenue

**Implementation:**
```python
from huggingface_hub import InferenceClient

client = InferenceClient(api_key="hf_...")
image = client.text_to_image(
    prompt="...",
    model="black-forest-labs/FLUX.1-schnell"
)
image.save("output.png")
```

**Providers:** fal-ai, replicate, together, hf-inference

### Option 2: OllamaDiffuser (Local)
**Status:** Researched, CPU constraint

**Setup:**
- Install: `pip install ollamadiffuser`
- Models: FLUX.1-schnell (free), SD 1.5, SD 3.5, FLUX.1-dev

**Hardware Reality:**
- Dell Inspiron: AMD Ryzen 5 7530U (CPU only)
- Generation time: 2-5+ minutes per image on CPU
- Viable for overnight batch generation

**Use case:** When we have time but not budget

### Option 3: ComfyUI (Local)
**Status:** Not explored in detail

**Pros:**
- Full control over SD pipeline
- LoRA support, custom workflows
- Active community

**Cons:**
- Same CPU slowness issue
- Steeper learning curve
- Overkill for blog needs

### Option 4: Free Web UIs (Current Manual Approach)
**Status:** Active

**Services:**
- HuggingFace Spaces (various models)
- Replicate free tier
- Fal.ai playground
- Direct model web UIs

**Pros:**
- High quality, fast
- No local compute
- No API costs

**Cons:**
- Manual process
- Not automated

## Decision Criteria for Future

**Stick with manual if:**
- Blog posts remain 1-2/week
- Image quality is priority
- Time investment is acceptable

**Move to HF PRO if:**
- Blog generates $9+/month
- Need API automation
- Want programmatic control

**Move to local if:**
- Need full control over prompts/models
- Can tolerate generation time
- Want zero ongoing costs

## MCP Wrapper Design (Shelved)

If we implement automated image gen, here's the MCP wrapper structure:

**Tool:** `generate_blog_image`
**Parameters:**
- `prompt` (required)
- `model` (default: "black-forest-labs/FLUX.1-schnell")
- `provider` (default: "auto")
- `output_path` (required)

**Implementation:** Python wrapper around `huggingface_hub.InferenceClient`

**Status:** Designed but not built (waiting for cost justification)

---

**Last Updated:** 2026-01-04
**Decision:** Manual generation for now, revisit when blog economics justify automation
