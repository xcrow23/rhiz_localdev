# N8N Blog Transcript Workflow - Design

## Purpose

Simple workflow to move audio transcripts from Captain's phone to collaborative session with daemon. No automation of public-facing actions—just smooth transition to joint work.

## Workflow Steps

### 1. Trigger: Webhook
- **Node**: Webhook trigger
- **Method**: POST
- **Endpoint**: `/webhook/blog-transcript`
- **Expected payload**:
  ```json
  {
    "transcript": "full transcript text here",
    "topic": "optional topic/title hint",
    "timestamp": "ISO timestamp"
  }
  ```

### 2. Process: Extract & Format
- **Node**: Function/Code node
- **Purpose**: Clean transcript, add metadata
- **Operations**:
  - Extract transcript text
  - Generate filename: `transcript_YYYYMMDD_HHMMSS.txt`
  - Add header with metadata (timestamp, topic hint if provided)

### 3. Store: Write to File System
- **Node**: HTTP Request or Execute Command
- **Purpose**: Save transcript to known location
- **Target path**: `C:\Users\dread\Documents\Rhiz_LocalDev\docs\blog\transcripts\`
- **Filename**: From previous step
- **Content**: Formatted transcript with metadata header

### 4. Notify: Signal Ready
- **Node**: Multiple options (Captain decides):
  - **Option A**: Simple HTTP response with success + file path
  - **Option B**: Send notification (Slack, Discord, etc.)
  - **Option C**: Update a status file that Captain can check
- **Purpose**: Let Captain know transcript is ready for collaborative session

## Data Flow

```
Phone → Transcription App → Webhook POST → n8n
                                            ↓
                                       Extract/Format
                                            ↓
                                       Write to File
                                            ↓
                                       Notify Captain
                                            ↓
                                    Manual Claude Code Session
```

## What Happens Next (Outside n8n)

1. Captain opens Claude Code session
2. Captain: "New blog transcript ready at transcripts/[filename]"
3. Daemon reads transcript
4. Daemon inserts italic commentary/expansion
5. Iterate 1-2 passes together
6. Generate images (in session)
7. Manual post to Substack

## Refinements for Later

- **Auto-trigger Claude Code session**: Possible but requires system integration
- **Context pre-load**: Could have n8n prepare a formatted prompt with transcript loaded
- **Image generation queue**: Could pre-generate some images based on topic keywords
- **Draft saving**: Auto-save drafts at each iteration stage
- **Substack API posting**: Once we trust the unofficial API, could add this

## Implementation Notes

**For cloud n8n (Hostinger):**
- Webhook will have public URL
- File writing requires either:
  - SSH/SFTP to local machine
  - Storage in cloud location accessible to both n8n and local Claude Code
  - Alternative: Store in Qdrant/database, retrieve in session

**For local n8n (if we set one up):**
- Direct file system access
- No SSH needed
- Webhook accessible via local network or ngrok

## Security Considerations

- Webhook endpoint should have authentication (API key or token)
- Transcripts may contain sensitive/personal content
- No auto-posting to public platforms without review

## Recommended Initial Setup

**Simplest path:**
1. Cloud n8n webhook receives transcript
2. Stores in Qdrant memory system (we already have this operational)
3. Returns success with memory ID
4. Captain starts Claude Code session: "Load transcript [memory_id]"
5. Daemon retrieves from Qdrant, begins collaboration

**Alternative (direct file):**
1. Cloud n8n webhook receives transcript
2. SSH/SFTP to Captain's machine, writes to transcripts folder
3. Returns success with filename
4. Captain starts Claude Code session with filename

Captain decides which approach fits the workflow better.
