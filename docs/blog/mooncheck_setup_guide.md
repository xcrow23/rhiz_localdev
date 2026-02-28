# Mooncheck Setup Guide - Complete Implementation

## Overview

**Mooncheck**: Separate memory branch for blog/creative transcripts, stored in Qdrant vector database, accessible via voice → iPhone → n8n → Qdrant → Claude Code.

**Flow:**
```
iPhone (dictate) → iOS Shortcut → n8n Webhook → Qdrant (moonchecks collection) → Claude Code retrieval
```

---

## Part 1: Deploy n8n Workflow

### Step 1: Import Workflow to Hostinger n8n

1. Log into your Hostinger n8n instance
2. Click **"+ Add workflow"** or **"Import from File"**
3. Upload `mooncheck_workflow_n8n.json` from `docs/blog/`
4. Workflow will be imported with all nodes configured

### Step 2: Configure Environment Variables

In your n8n instance, set these environment variables:

```bash
QDRANT_URL=https://[your-qdrant-cloud-url]:6333
```

Or if using Qdrant credentials node, configure the **Qdrant API** credential with:
- **Host**: Your Qdrant cloud URL
- **API Key**: Your Qdrant API key (if using cloud)

### Step 3: Test Qdrant Collection Creation

1. Open the workflow
2. Click on **"Ensure Moonchecks Collection"** node
3. Click **"Execute Node"**
4. Should return success (creates `moonchecks` collection if it doesn't exist)

### Step 4: Activate Webhook

1. Click **"Webhook Trigger"** node
2. Copy the **Production Webhook URL**
3. Should look like: `https://[your-n8n-domain]/webhook/mooncheck`
4. Save this URL for iOS Shortcut configuration

### Step 5: Activate Workflow

1. Toggle workflow to **"Active"**
2. Webhook is now live and ready to receive moonchecks

---

## Part 2: Configure iOS Shortcut

### Step 1: Create New Shortcut

1. Open **Shortcuts** app on iPhone
2. Tap **"+"** to create new shortcut
3. Name it: **"Mooncheck"**

### Step 2: Add Dictation Action

1. Search for **"Dictate Text"**
2. Add to shortcut
3. Configure:
   - **Show When Run**: ON (so you can speak)
   - **Language**: English (or your preference)
   - **Stop Listening**: After Pause

### Step 3: Add Topic Prompt (Optional)

1. Search for **"Ask for Input"**
2. Add to shortcut
3. Configure:
   - **Prompt**: "Topic hint? (optional)"
   - **Input Type**: Text
   - **Default Answer**: (leave blank)

### Step 4: Add Category Prompt (Optional)

1. Add another **"Ask for Input"**
2. Configure:
   - **Prompt**: "Category?"
   - **Input Type**: Text
   - **Default Answer**: "blog"

### Step 5: Build JSON Payload

1. Search for **"Dictionary"**
2. Add to shortcut
3. Add keys:
   - **transcript**: *(Dictated Text)* ← select variable from step 2
   - **topic_hint**: *(Provided Input)* ← select variable from step 3
   - **category**: *(Provided Input)* ← select variable from step 4

### Step 6: Send to n8n Webhook

1. Search for **"Get Contents of URL"**
2. Add to shortcut
3. Configure:
   - **URL**: `https://[your-n8n-domain]/webhook/mooncheck`
   - **Method**: POST
   - **Request Body**: JSON
   - **JSON**: *(Dictionary)* ← select variable from step 5
   - **Headers**:
     - Content-Type: `application/json`

### Step 7: Show Success Notification

1. Search for **"Get Dictionary from Input"**
2. Add to shortcut (parses n8n response)
3. Search for **"Show Notification"**
4. Add to shortcut
5. Configure:
   - **Title**: "Mooncheck Captured!"
   - **Body**: "ID: *(mooncheck_id)* | Words: *(word_count)*"

### Step 8: Add to Home Screen / Siri

**Option A: Siri Phrase**
1. Tap shortcut settings (three dots)
2. **"Add to Siri"**
3. Record phrase: **"Mooncheck"** or **"Blog note"**

**Option B: Widget**
1. Long press home screen → Add Widget
2. Find **Shortcuts** widget
3. Add shortcut to home screen

### Step 9: Test the Shortcut

1. Run the shortcut
2. Speak your transcript (e.g., "This is a test mooncheck about AI collaboration")
3. Enter topic hint: "testing"
4. Enter category: "blog"
5. Should see success notification with mooncheck ID

---

## Part 3: Verify in Qdrant

### Check Mooncheck was Stored

**Via Qdrant Web UI (if available):**
1. Open Qdrant dashboard
2. Select `moonchecks` collection
3. Should see your test point with transcript in payload

**Via n8n Test:**
1. Create simple n8n workflow with HTTP Request node
2. GET `https://[qdrant-url]/collections/moonchecks/points/scroll`
3. Should return stored moonchecks

---

## Part 4: Retrieve Moonchecks in Claude Code

### New MCP Tools Needed

We'll need to add to the `rhiz-mcp` server:

**Tool: `mooncheck_load`**
- Parameters: `id` (optional), `filter` (category, topic), `limit`
- Returns: Mooncheck(s) formatted for context loading

**Tool: `mooncheck_search`**
- Parameters: `query` (semantic search text)
- Returns: Relevant moonchecks via vector similarity

### Usage Patterns

**Load latest mooncheck:**
```
Captain: "Load latest mooncheck"
Daemon: [Calls mooncheck_load with filter="latest"]
```

**Load specific mooncheck:**
```
Captain: "Load mooncheck abc123"
Daemon: [Calls mooncheck_load with id="mooncheck_abc123"]
```

**Search moonchecks:**
```
Captain: "Find moonchecks about vectorized memory"
Daemon: [Calls mooncheck_search with query="vectorized memory"]
```

**Load for blog creation:**
```
Captain: "Load latest blog mooncheck and let's create a post"
Daemon: [Loads mooncheck, extracts verbatim sections, inserts italicized commentary]
```

### Blog Creation Workflow Pattern

**IMPORTANT**: This is NOT AI ghostwriting. Captain's actual words are extracted and organized, never rewritten into "cleaner" AI voice. Daemon adds technical/philosophical commentary in italics.

**Pipeline:**

1. **Raw Mooncheck Transcript** (~1,000-3,000 words)
   - Stream-of-consciousness audio dictation
   - Verbose, circles topics, explores tangents
   - Intentionally unstructured (Captain is thinking out loud)

2. **Daemon Structures the Arc** (based on topic, not transcript order)
   - Identify core theme/thesis
   - Map optimal article structure for that theme
   - Determine where images enhance flow

3. **Daemon Extracts Captain's Words** (verbatim, restructured)
   - Pull Captain's best phrases/sections that fit the arc
   - Use his ACTUAL words (no rewriting, no "cleaning up")
   - Minimal edits: only for grammatical flow between extracted sections
   - Ignore original transcript ordering—organize by article logic

4. **Daemon Inserts Commentary** (in italics)
   - Add technical depth where Captain was conceptual
   - Provide daemon perspective on workflow patterns
   - Expand on architectural implications
   - Create call-and-response dialogue between perspectives

5. **Image Prompts** (2 Captain, 2 Daemon)
   - Different aesthetic priors
   - Placed to break up text and enhance arc

6. **Iterate 1-2 Passes**
   - Captain reviews, edits, adds image prompts
   - Refine voice balance
   - Final ~800-1,200 words

**Example Pipeline:**

*Transcript (raw):* "So anyway moving on to semantically abstracted and vectorized search checkpoints. So currently what RISE is doing is we are deploying a cloud-based context memory system that's synced between a local PC and that..."

*Published (extracted & organized):* "What we've built in Rhiz is simple in concept: checkpoints written at session close, stored in a cloud-synced vector database (Qdrant), tagged with semantic keywords based on project domains."

Note: Same concepts, Captain's voice, but organized for article flow rather than transcript flow.

**Why This Matters:**
- Captain's raw verbosity is for neural net work patterns (thinking out loud)
- Published posts are for human readers (structured narrative)
- Extraction preserves authentic voice without transcription artifacts
- Daemon doesn't "ghostwrite"—uses Captain's actual words in better structure
- The arc comes from daemon analysis, the voice comes from Captain's transcript

---

## Architecture Notes

### Mooncheck vs Checkpoint

**Checkpoints** (existing):
- Session continuity
- Project memory
- Technical work state
- Alternatives rejected
- Working hypotheses

**Moonchecks** (new):
- Blog transcripts
- Philosophical musings
- Creative notes
- Voice memos
- Raw creative input

**Separate but complementary** - checkpoints track how we work, moonchecks track what we create.

### Qdrant Schema

**Collection**: `moonchecks`
**Vector Dimension**: 384 (all-MiniLM-L6-v2)
**Distance Metric**: Cosine

**Payload Structure**:
```yaml
id: mooncheck_1735930400_abc123def
timestamp: 2026-01-04T12:00:00.000Z
transcript: "Full transcript text here..."
topic_hint: "vectorized memory"
category: "blog"
word_count: 487
created_via: "ios_shortcut"
status: "captured"
```

### Future Enhancements

- **Moon phase tracking**: Add actual lunar phase to mooncheck metadata for long-view correlation analysis
- **Dyad state correlation**: Link moonchecks to dyad state at time of creation
- **Auto-categorization**: Use LLM to suggest category/tags from transcript
- **Voice characteristics**: Store audio file reference for tone/cadence analysis
- **Mooncheck threads**: Link related moonchecks into conversation threads

---

## Troubleshooting

### Shortcut fails to send

**Check:**
1. n8n webhook URL is correct
2. Workflow is activated
3. iPhone has internet connection
4. n8n instance is accessible from public internet

### Mooncheck not appearing in Qdrant

**Check:**
1. Qdrant collection exists (run "Ensure Collection" node)
2. Qdrant credentials configured correctly
3. Embedding generation succeeded
4. Check n8n execution history for errors

### Can't retrieve mooncheck in Claude Code

**Check:**
1. MCP server has mooncheck tools implemented
2. Qdrant accessible from Claude Code
3. Mooncheck ID is correct

---

## Security Considerations

1. **Webhook endpoint is public** - consider adding API key authentication
2. **Transcripts may contain sensitive content** - ensure Qdrant is secured
3. **iOS Shortcut stores webhook URL** - don't share shortcut publicly
4. **Qdrant credentials** - stored securely in n8n environment variables

---

## Success Metrics

After deployment, you should be able to:

✅ Dictate blog notes on iPhone via "Hey Siri, mooncheck"
✅ Receive confirmation with mooncheck ID
✅ Load mooncheck in Claude Code session
✅ Create blog posts collaboratively from moonchecks
✅ Search past moonchecks semantically
✅ Track creative output over time

---

**Last Updated**: 2026-01-04
**Status**: Ready for deployment
**Next**: Test with real blog transcript, iterate on retrieval UX
