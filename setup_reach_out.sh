#!/bin/bash
# Setup script for Reach Out feature

set -e

echo "=========================================="
echo "Reach Out Feature Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"
echo ""

# Check if running from correct directory
if [ ! -d "services" ] || [ ! -d "app" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
echo ""

echo "1. Installing keyword extractor dependencies..."
pip install -q google-genai python-dotenv
echo "   ✅ Done"

echo "2. Installing reach-out generator dependencies..."
# Already installed in step 1
echo "   ✅ Done"

echo "3. Installing LinkedIn search dependencies..."
pip install -q requests beautifulsoup4
pip install -q serpapi 2>/dev/null || echo "   ⚠️  SerpAPI not installed (optional)"
echo "   ✅ Done"

echo ""
echo "=========================================="
echo "Environment Setup"
echo "=========================================="
echo ""

# Check for .env file
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    touch .env
fi

# Check for API keys
if ! grep -q "GOOGLE_API_KEY" .env; then
    echo ""
    echo "⚠️  GOOGLE_API_KEY not found in .env"
    echo ""
    read -p "Do you have a Google Gemini API key? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your Google API key: " google_key
        echo "GOOGLE_API_KEY=$google_key" >> .env
        echo "✅ Google API key added to .env"
    else
        echo "❌ Google API key is required for this feature"
        echo "   Get one at: https://aistudio.google.com/apikey"
    fi
else
    echo "✅ GOOGLE_API_KEY found in .env"
fi

echo ""

# Check for SerpAPI key (optional)
if ! grep -q "SERPAPI_API_KEY" .env; then
    echo "⚠️  SERPAPI_API_KEY not found in .env (optional)"
    echo ""
    read -p "Do you want to add SerpAPI key for better LinkedIn search? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Enter your SerpAPI key: " serp_key
        echo "SERPAPI_API_KEY=$serp_key" >> .env
        echo "✅ SerpAPI key added to .env"
    else
        echo "⚠️  Will use DuckDuckGo fallback for LinkedIn search"
    fi
else
    echo "✅ SERPAPI_API_KEY found in .env"
fi

echo ""
echo "=========================================="
echo "Testing Installation"
echo "=========================================="
echo ""

# Test the installation
echo "Running tests..."
python3 tests/test_reach_out_workflow.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Run the app: streamlit run app/app.py"
echo "2. Go to the Profile tab and upload your resume"
echo "3. Search for jobs in the Job Search tab"
echo "4. Use the Reach Out tab to find contacts and generate messages"
echo ""
echo "For more information, see:"
echo "- REACH_OUT_INTEGRATION.md (comprehensive guide)"
echo "- app/tabs/REACH_OUT_README.md (feature documentation)"
echo ""
