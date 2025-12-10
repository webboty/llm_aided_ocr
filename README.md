# 📖 LLM-Aided OCR Manual (LM Studio Enhanced Version)

## 🚀 Quick Start

### 1. Navigate to Project Directory
```bash
# Replace with your actual installation path
cd /path/to/your/llm_aided_ocr
source venv/bin/activate
```

### 2. Verify LM Studio Connection
```bash
python test_lm_studio.py
```

### 3. Process Your First PDF
```bash
# Place your PDF in the project directory, then:
python llm_aided_ocr.py
```

---

## 📁 File Structure & Where to Put Files

```
llm_aided_ocr/                          # Project root directory
├── 📄 YOUR-PDF-FILE.pdf          # ← PUT YOUR PDFs HERE
├── 🤖 llm_aided_ocr.py          # Main OCR script
├── ⚙️ config_helper.py             # Configuration manager
├── 🔍 test_lm_studio.py           # LM Studio connection tester
├── 📋 discover_models.py          # List available models
├── 🔧 .env                       # Configuration file
├── 📁 venv/                      # Python virtual environment
└── 📄 OUTPUT FILES:              # ← RESULTS APPEAR HERE
    ├── YOUR-PDF__raw_ocr_output.txt
    └── YOUR-PDF_llm_corrected.md
```

### 📥 Where to Put PDFs
**Location**: Project root directory (where `llm_aided_ocr.py` is located)
- Simply copy any PDF file into the same directory as the script
- No subfolders - PDFs must be in the root directory
- The script automatically detects its installation directory

### 📤 Where to Find Results
**Location**: Same directory as your PDF and script
- **Raw OCR**: `{filename}__raw_ocr_output.txt`
- **Enhanced**: `{filename}_llm_corrected.md`

---

## ⚙️ Configuration

### Method 1: Configuration Helper (Recommended)
```bash
# Show current settings
python config_helper.py show

# Switch to LM Studio
python config_helper.py lm-studio

# Use specific model
python config_helper.py lm-model "qwen/qwen3-vl-30b"

# Switch to other providers
python config_helper.py openai      # OpenAI
python config_helper.py claude      # Claude
python config_helper.py local       # Local GGUF
```

### Method 2: Manual .env Editing
Edit `.env` file directly:

```bash
# LLM Provider
API_PROVIDER=LM_STUDIO          # Options: OPENAI, CLAUDE, LM_STUDIO
USE_LOCAL_LLM=False            # Set to True for local GGUF files

# LM Studio Settings
LM_STUDIO_BASE_URL=http://192.168.1.107:11435
LM_STUDIO_MODEL=qwen/qwen3-vl-30b

# Cloud API Keys (if needed)
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Processing Settings
ENABLE_MARKDOWN_FORMATTING=True
SUPPRESS_HEADERS_AND_PAGE_NUMBERS=True
MAX_TOKENS_PER_CHUNK=3000
CHUNK_OVERLAP_SIZE=100
```

---

## 🔍 LM Studio Model Management

### List Available Models
```bash
python discover_models.py
```

### Test Connection
```bash
python test_lm_studio.py
```

### Switch Models
```bash
# Use a specific model
python config_helper.py lm-model "model-name-from-list"

# Examples:
python config_helper.py lm-model "qwen/qwen3-vl-30b"
python config_helper.py lm-model "mistralai/ministral-3-14b-reasoning"
python config_helper.py lm-model "qwen/qwen3-vl-8b"
```

---

## 📋 Step-by-Step Workflow

### 1. Prepare LM Studio
1. **Open LM Studio application**
2. **Load your model** (e.g., `qwen/qwen3-vl-30b`)
3. **Enable Server**:
   - Settings → Server → ✅ "Expose Server"
   - Port: `11435`
   - CORS: `*`
4. **Verify**: `python test_lm_studio.py`

### 2. Configure OCR Tool
```bash
# Navigate to project directory
cd /path/to/your/llm_aided_ocr
source venv/bin/activate

# Set to LM Studio
python config_helper.py lm-studio

# Verify configuration
python config_helper.py show
```

### 3. Process PDF
```bash
# Step 1: Copy PDF to project directory
cp ~/Desktop/your-document.pdf /path/to/your/llm_aided_ocr/

# Step 2: Run OCR
python llm_aided_ocr.py

# Step 3: Check results
ls -la *_llm_corrected.md
```

---

## 📄 Output Files Explained

### Raw OCR Output
**File**: `{filename}__raw_ocr_output.txt`
- Direct text from Tesseract OCR
- Contains errors, formatting issues
- Good for comparison purposes

### LLM Enhanced Output  
**File**: `{filename}_llm_corrected.md`
- **OCR Error Correction**: Fixes recognition mistakes
- **Professional Formatting**: Clean Markdown structure
- **Content Enhancement**: Improves readability
- **Header/Footer Removal**: Optional suppression of page numbers

---

## 🛠️ Advanced Usage

### Processing Specific Pages
Edit `llm_aided_ocr.py` main function:
```python
# Process only first 5 pages, skip first 2 pages
max_test_pages = 5
skip_first_n_pages = 2
```

### Custom Processing Settings
```bash
# Edit .env for fine-tuning
ENABLE_MARKDOWN_FORMATTING=True      # Format as Markdown
SUPPRESS_HEADERS_AND_PAGE_NUMBERS=True   # Remove headers/footers  
MAX_TOKENS_PER_CHUNK=2000             # Smaller chunks (slower but more stable)
CHUNK_OVERLAP_SIZE=50                 # Less overlap (faster)
ENABLE_QUALITY_ASSESSMENT=True         # Compare output quality
```

### Batch Processing Multiple PDFs
```bash
# Process all PDFs in directory
for pdf in *.pdf; do
    echo "Processing $pdf..."
    python llm_aided_ocr.py
    # Move results to output folder
    mv *_llm_corrected.md results/
    mv *__raw_ocr_output.txt results/
done
```

---

## 🔧 Troubleshooting

### LM Studio Connection Issues
```bash
# Test basic connection
python test_lm_studio.py

# Common fixes:
□ LM Studio is running
□ Model is loaded in AI Chat tab  
□ Server enabled in Settings
□ Port 11435 is correct
□ Model name matches exactly
```

### Model Name Problems
```bash
# Discover exact model names
python discover_models.py

# Use exact name from list
python config_helper.py lm-model "exact-model-name-from-list"
```

### Processing Errors
```bash
# Check logs for details
tail -f *.log  # If logging enabled

# Common issues:
□ PDF is corrupted/protected
□ Not enough RAM for large models
□ Network timeout (increase chunk size)
□ Model context window too small
```

### Performance Optimization
```bash
# For faster processing:
MAX_TOKENS_PER_CHUNK=4000    # Larger chunks
CHUNK_OVERLAP_SIZE=50         # Less overlap

# For better quality:
MAX_TOKENS_PER_CHUNK=2000    # Smaller chunks  
CHUNK_OVERLAP_SIZE=200        # More overlap
```

---

## 📋 Quick Reference Commands

```bash
# Environment Setup
cd /path/to/your/llm_aided_ocr && source venv/bin/activate

# Configuration
python config_helper.py show                    # Current settings
python config_helper.py lm-studio               # Use LM Studio
python config_helper.py lm-model "model-name"    # Set model

# Testing
python test_lm_studio.py                       # Test connection
python discover_models.py                      # List models

# Processing
python llm_aided_ocr.py                      # Process PDF

# Results
ls *_llm_corrected.md                         # Find outputs
open *_llm_corrected.md                       # View results
```

---

## 🎯 Best Practices

1. **Test First**: Always run `python test_lm_studio.py` before processing
2. **Start Small**: Test with short PDFs first
3. **Monitor Resources**: Large models need sufficient RAM
4. **Check Model Names**: Use exact names from `discover_models.py`
5. **Backup Originals**: Keep original PDFs safe
6. **Review Output**: Compare raw vs enhanced for quality

---

## 📞 Help & Support

### Configuration Issues
```bash
python config_helper.py show    # Check current config
```

### Connection Problems  
```bash
python test_lm_studio.py      # Diagnose connection
python discover_models.py     # Verify models available
```

### File Locations
- **PDFs Go**: Same directory as `llm_aided_ocr.py`
- **Results Appear**: Same directory as PDF
- **Configuration**: `.env` file
- **Logs**: Console output (can be redirected to file)

---

## 🌟 Installation-Specific Instructions

### Finding Your Installation Directory
If you're not sure where `llm_aided_ocr` is installed:

```bash
# Find the installation
find / -name "llm_aided_ocr.py" 2>/dev/null

# Common locations:
~/AI-Tools/llm_aided_ocr/
~/llm_aided_ocr/
/usr/local/bin/llm_aided_ocr/
/opt/llm_aided_ocr/
```

### Directory Detection
The script automatically detects its installation directory, so you can:
- Install it anywhere on your system
- Navigate to that directory
- All relative paths work automatically

---

🎉 **You're ready to use LM Studio with LLM-Aided OCR!**

The enhanced version supports your local LM Studio instance with 74+ available models and provides professional OCR correction and formatting.