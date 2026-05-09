#!/bin/bash

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   GitHub Actions Code Analysis Workflow - Quick Start     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  This script is optimized for macOS. Some commands may differ.${NC}\n"
fi

# Step 1: Check Python
echo -e "${BLUE}Step 1: Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    echo "  Install Python 3.11 or higher"
    exit 1
fi
python_version=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓ Python ${python_version} found${NC}\n"

# Step 2: Install Python dependencies
echo -e "${BLUE}Step 2: Installing Python dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
else
    echo -e "${RED}✗ requirements.txt not found${NC}"
    exit 1
fi

# Step 3: Check Ollama
echo -e "${BLUE}Step 3: Checking Ollama installation...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}⚠️  Ollama not found${NC}"
    echo -e "  Installing Ollama for macOS..."
    echo ""
    echo -e "${BLUE}Run this command:${NC}"
    echo "  brew install ollama"
    echo ""
    echo -e "  Then start the Ollama service:"
    echo "  ollama serve"
    echo ""
    read -p "Press Enter after installing Ollama..."
fi

if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓ Ollama found${NC}\n"
fi

# Step 4: Check Ollama service
echo -e "${BLUE}Step 4: Checking Ollama service...${NC}"
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Ollama service is running${NC}"
    
    # Check for deepseek-coder model
    if curl -s http://localhost:11434/api/tags | grep -q "deepseek-coder"; then
        echo -e "${GREEN}✓ deepseek-coder model found${NC}\n"
    else
        echo -e "${YELLOW}⚠️  deepseek-coder model not found${NC}"
        echo -e "  ${BLUE}Pulling deepseek-coder:6.7b (this may take a few minutes)...${NC}"
        ollama pull deepseek-coder:6.7b
        echo ""
    fi
else
    echo -e "${RED}✗ Ollama service is not running${NC}"
    echo -e "  ${BLUE}Start Ollama service:${NC}"
    echo "  ollama serve"
    echo ""
    read -p "Start Ollama service now and press Enter..."
fi

# Step 5: Test local analysis
echo -e "${BLUE}Step 5: Testing code analysis...${NC}"
read -p "Test the analysis script now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${BLUE}Running analysis...${NC}\n"
    python3 analyze.py --help > /dev/null 2>&1
    if python3 analyze.py; then
        echo ""
        echo -e "${GREEN}✓ Analysis test completed successfully${NC}"
    else
        echo -e "${RED}✗ Analysis test failed${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Setup Complete! 🎉                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"

echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. ${BLUE}Initialize git repository${NC} (if not already done):"
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo ""
echo "2. ${BLUE}Push to GitHub:${NC}"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "3. ${BLUE}Run the workflow:${NC}"
echo "   - Go to GitHub repository → Actions tab"
echo "   - Select 'Code Analysis with Ollama' workflow"
echo "   - Click 'Run workflow'"
echo ""
echo "4. ${BLUE}Check results:${NC}"
echo "   - Download 'analysis-results' artifact"
echo "   - View analysis-report.md and analysis-results.json"
echo ""
echo -e "${YELLOW}Note:${NC} The workflow requires Ollama to be accessible from the GitHub runner."
echo "For Self-hosted runners, this will work automatically."
echo "For GitHub-hosted runners, you'll need to run Ollama on a publicly accessible server."
echo ""
