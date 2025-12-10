# 🚀 LM Studio Setup for Qwen3-VL-30B

## Step 1: Load Model in LM Studio

1. **Open LM Studio**
2. **Search for Qwen3-VL-30B:**
   - Click the search icon (🔍)
   - Type: `qwen3-vl-30b`
   - Look for: `qwen/qwen3-vl-30b`
3. **Download & Load:**
   - Click the model
   - Click "Download" (this may take a while - it's a large model)
   - Once downloaded, click "Load Model"
4. **Verify Loading:**
   - Wait for the model to fully load (progress bar completes)
   - You should see the model name in the AI Chat tab

## Step 2: Enable Server

1. **Go to Settings** (⚙️ icon)
2. **Server Tab:**
   - ✅ Enable "Expose Server"
   - Port: `11435` (or whatever port you prefer)
   - CORS: `*` (allows all origins)
3. **Start Server** if not already running

## Step 3: Configure OCR Tool

```bash
cd ~/AI-Tools/llm_aided_ocr
source venv/bin/activate

# Set up for Qwen3-VL-30B
python config_helper.py lm-model "qwen/qwen3-vl-30b"

# Verify connection
python discover_models.py
```

## Step 4: Test & Run

```bash
# Test the connection
python test_lm_studio.py

# If successful, process a PDF
python llm_aided_ocr.py
```

## 🔍 Troubleshooting

### Model Not Found
```bash
python discover_models.py
# This will show exact model names available
# Use the exact name in config_helper.py
```

### Connection Issues
- Check LM Studio is running
- Verify server port matches (11435)
- Ensure model is fully loaded
- Check firewall isn't blocking the connection

### Performance Tips
- Qwen3-VL-30B is a large model - ensure you have enough RAM
- First response may be slower as model warms up
- Consider using a smaller model for faster processing

## 📋 Quick Commands

```bash
# Switch to LM Studio with Qwen3-VL-30B
python config_helper.py lm-model "qwen/qwen3-vl-30b"

# Check current config
python config_helper.py show

# Test connection
python test_lm_studio.py

# Discover available models
python discover_models.py

# Process PDF
python llm_aided_ocr.py
```

---

🎯 **Target Configuration:**
- **Model**: qwen/qwen3-vl-30b
- **URL**: http://192.168.1.107:11435
- **Provider**: LM_STUDIO

Once the model is loaded in LM Studio, the OCR tool will use it for intelligent text correction and formatting!