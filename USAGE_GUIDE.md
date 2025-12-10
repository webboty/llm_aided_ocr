# LLM-Aided OCR - Usage Guide

## 🚀 Quick Start

### 1. Activate Environment
```bash
cd ~/AI-Tools/llm_aided_ocr
source venv/bin/activate
```

### 2. Choose Your LLM Provider

#### Option A: OpenAI (Cloud)
```bash
python config_helper.py openai
# Edit .env and add: OPENAI_API_KEY=sk-your-key-here
```

#### Option B: Anthropic Claude (Cloud)
```bash
python config_helper.py claude
# Edit .env and add: ANTHROPIC_API_KEY=sk-ant-your-key-here
```

#### Option C: LM Studio (Local Network) ⭐
```bash
python config_helper.py lm-studio
# Test connection first:
python test_lm_studio.py
```

#### Option D: Local GGUF Model
```bash
python config_helper.py local
# Edit .env and set: LOCAL_LLM_MODEL_PATH=path/to/model.gguf
```

### 3. Process a PDF
```bash
# Place your PDF in the project directory, then:
python llm_aided_ocr.py
```

## 📋 Configuration Management

### Show Current Config
```bash
python config_helper.py show
```

### Switch Providers
```bash
python config_helper.py openai      # Use OpenAI
python config_helper.py claude      # Use Claude  
python config_helper.py lm-studio   # Use LM Studio
python config_helper.py local       # Use local GGUF
```

### Set Specific LM Studio Model
```bash
python config_helper.py lm-model "llama-3.1-8b-instruct"
```

## 🔧 LM Studio Setup

### 1. Install & Start LM Studio
- Download from [lmstudio.ai](https://lmstudio.ai)
- Start LM Studio application

### 2. Load a Model
- Go to **AI Chat** tab
- Select a model (e.g., Llama 3.1, Mistral, etc.)
- Wait for model to fully load

### 3. Enable Server
- Go to **Settings** → **Server**
- Enable "Expose Server"
- Note the port (default: 11434, we use 11435)
- Set CORS to "*" if needed

### 4. Test Connection
```bash
python test_lm_studio.py
```

### 5. Run OCR
```bash
python config_helper.py lm-studio  # Switch to LM Studio
python llm_aided_ocr.py         # Process PDF
```

## 📁 File Structure

```
llm_aided_ocr/
├── llm_aided_ocr.py          # Main OCR script
├── config_helper.py           # Configuration manager
├── test_lm_studio.py         # LM Studio connection tester
├── .env                     # Configuration file
├── venv/                    # Python virtual environment
└── your-input.pdf           # Your PDF file
```

## 📄 Output Files

For each processed PDF `{filename}.pdf`:

- `{filename}__raw_ocr_output.txt` - Raw OCR text from Tesseract
- `{filename}_llm_corrected.md` - LLM-enhanced, formatted text

## ⚙️ Advanced Configuration

Edit `.env` file for fine-tuning:

```bash
# Processing Settings
ENABLE_MARKDOWN_FORMATTING=True          # Format as Markdown
SUPPRESS_HEADERS_AND_PAGE_NUMBERS=True   # Remove headers/footers
MAX_TOKENS_PER_CHUNK=3000              # Chunk size for processing
CHUNK_OVERLAP_SIZE=100                 # Overlap between chunks

# Quality Assessment
ENABLE_QUALITY_ASSESSMENT=True          # Compare output quality
```

## 🐛 Troubleshooting

### LM Studio Issues
```bash
# Test connection
python test_lm_studio.py

# Common fixes:
# 1. Make sure LM Studio is running
# 2. Load a model in AI Chat tab
# 3. Check server is enabled in Settings
# 4. Verify port matches (default: 11435)
```

### API Key Issues
```bash
# Check current config
python config_helper.py show

# Edit .env file to add keys:
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### Performance Tips
- **Cloud APIs**: Faster, no local resources needed
- **LM Studio**: Good balance of speed and privacy
- **Local GGUF**: Most private, requires powerful hardware

## 🎯 Best Practices

1. **Test with small PDFs first** to verify setup
2. **Check model compatibility** - some models work better for OCR correction
3. **Monitor token usage** with cloud APIs
4. **Use appropriate chunk sizes** for your model's context window
5. **Enable quality assessment** to compare improvements

## 📞 Support

- **GitHub Repository**: [Dicklesworthstone/llm_aided_ocr](https://github.com/Dicklesworthstone/llm_aided_ocr)
- **LM Studio**: [lmstudio.ai](https://lmstudio.ai)
- **Issues**: Check logs for detailed error messages

---

🎉 **Your LM Studio integration is ready!** 

Just load a model in LM Studio and run:
```bash
python config_helper.py lm-studio
python llm_aided_ocr.py
```