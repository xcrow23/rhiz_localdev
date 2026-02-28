# OpenAI Image Generation MCP - Installation Guide

## Repository
GitHub: https://github.com/spartanz51/imagegen-mcp

## Prerequisites
- Node.js v18 or later
- npm or yarn
- OpenAI API key

## Quick Install (Recommended for Claude Code)

### Option 1: Direct npx (No Installation Required)

**Configure Claude Code to use the MCP server:**

1. Open Claude Code settings/configuration
2. Add MCP server entry (exact location depends on Claude Code setup)
3. Use this configuration:

```json
{
  "mcpServers": {
    "openai-image-gen": {
      "command": "npx",
      "args": ["imagegen-mcp", "--models", "dall-e-3"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

**Replace `your-openai-api-key-here` with actual OpenAI API key.**

### Option 2: Local Installation

If you prefer local installation for faster startup:

**1. Clone and install:**
```bash
git clone https://github.com/spartanz51/imagegen-mcp
cd imagegen-mcp
npm install
npm run build
```

**2. Create `.env` file:**
```bash
cp .env.example .env
```

**3. Edit `.env` and add:**
```
OPENAI_API_KEY=your-openai-api-key-here
```

**4. Configure Claude Code to use local installation:**
```json
{
  "mcpServers": {
    "openai-image-gen": {
      "command": "node",
      "args": ["C:\\path\\to\\imagegen-mcp\\dist\\index.js", "--models", "dall-e-3"],
      "env": {
        "OPENAI_API_KEY": "your-openai-api-key-here"
      }
    }
  }
}
```

## Model Options

Available models (specify with `--models` flag):
- `dall-e-3` - Latest DALL-E, best quality (recommended)
- `dall-e-2` - Previous version, faster/cheaper
- `gpt-image-1` - Alternative model

**For blog use, recommend `dall-e-3` for best results.**

## Usage in Blog Workflow

Once configured, in Claude Code session:

**Captain prompts 2 images:**
```
Captain: "Generate image: [description]"
```

**Daemon prompts 2 images:**
```
I'll generate: [description]
[uses MCP image generation tool]
```

Images save to specified location, ready for Substack upload.

## Testing the Installation

After configuration, test with:
```
Generate a simple test image: a blue sphere floating in space
```

Should return image URL or file path.

## Troubleshooting

**Error: "OPENAI_API_KEY not found"**
- Check API key is correctly set in env configuration
- Ensure no extra spaces or quotes in key

**Error: "npx: command not found"**
- Install Node.js v18+ from https://nodejs.org

**Slow first run with npx**
- Normal - npx downloads package on first use
- Subsequent runs are faster
- Use local installation option for consistent speed

## Next Steps

1. Captain: Install/configure MCP server using Option 1 or Option 2
2. Test with simple image generation
3. Ready for blog workflow integration

## Security Note

API key grants access to OpenAI services. Keep secure. Don't commit to git repos.
