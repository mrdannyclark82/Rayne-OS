#!/bin/bash

echo "🧪 Milla 3.0 - Integration Test Suite"
echo "======================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $1 exists"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 missing"
        ((FAILED++))
    fi
}

test_contains() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $1 contains '$2'"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $1 missing '$2'"
        ((FAILED++))
    fi
}

echo "📁 Testing File Structure..."
echo "----------------------------"
test_file "components/Sandbox.tsx"
test_file "components/CreativeStudio.tsx"
test_file "components/ThoughtLogger.tsx"
test_file "services/githubService.ts"
test_file "constants.ts"
test_file "NEW_CAPABILITIES.md"
echo ""

echo "🔧 Testing Service Integrations..."
echo "----------------------------------"
test_contains "services/geminiService.ts" "generateCode"
test_contains "services/geminiService.ts" "analyzeScreenShare"
test_contains "services/geminiService.ts" "generateBackgroundImage"
test_contains "services/geminiService.ts" "geminiService"
echo ""

echo "🎨 Testing Component Imports..."
echo "--------------------------------"
test_contains "App.tsx" "import Sandbox"
test_contains "App.tsx" "import CreativeStudio"
test_contains "App.tsx" "import ThoughtLogger"
test_contains "App.tsx" "geminiService"
echo ""

echo "🎭 Testing Feature States..."
echo "-----------------------------"
test_contains "App.tsx" "sandboxOpen"
test_contains "App.tsx" "creativeStudioOpen"
test_contains "App.tsx" "screenShareActive"
test_contains "App.tsx" "thoughtProcess"
test_contains "App.tsx" "backgroundImage"
test_contains "App.tsx" "PersonaMode.ADAPTIVE"
echo ""

echo "🚀 Testing Tool Modes..."
echo "------------------------"
test_contains "types.ts" "SANDBOX"
test_contains "types.ts" "CREATIVE"
test_contains "types.ts" "ADAPTIVE"
test_contains "types.ts" "thoughtProcess"
echo ""

echo "💅 Testing UI Elements..."
echo "-------------------------"
test_contains "App.tsx" "handleScreenShare"
test_contains "App.tsx" "open sandbox"
test_contains "App.tsx" "open studio"
test_contains "App.tsx" "ThoughtLogger"
echo ""

echo "📦 Testing Dependencies..."
echo "--------------------------"
if grep -q "prettier" package.json; then
    echo -e "${GREEN}✓${NC} prettier installed"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} prettier missing"
    ((FAILED++))
fi

if grep -q "react-simple-code-editor" package.json; then
    echo -e "${GREEN}✓${NC} react-simple-code-editor installed"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} react-simple-code-editor missing"
    ((FAILED++))
fi

if grep -q "prismjs" package.json; then
    echo -e "${GREEN}✓${NC} prismjs installed"
    ((PASSED++))
else
    echo -e "${RED}✗${NC} prismjs missing"
    ((FAILED++))
fi
echo ""

echo "🎨 Testing Styles..."
echo "--------------------"
test_contains "index.html" "prism-tomorrow.min.css"
test_contains "index.html" "code-line-numbers"
test_contains "index.html" "milla-400"
test_contains "index.html" "animate-in"
echo ""

echo "🧠 Testing System Instruction..."
echo "--------------------------------"
test_contains "services/geminiService.ts" "Sandbox"
test_contains "services/geminiService.ts" "Creative Studio"
test_contains "services/geminiService.ts" "Screen Share"
test_contains "services/geminiService.ts" "Adaptive Persona"
echo ""

echo "🏗️ Testing Build..."
echo "-------------------"
if [ -d "dist" ]; then
    echo -e "${GREEN}✓${NC} Build directory exists"
    ((PASSED++))
    if [ -f "dist/index.html" ]; then
        echo -e "${GREEN}✓${NC} Build output present"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} No build output"
        ((FAILED++))
    fi
else
    echo -e "${YELLOW}⚠${NC} Build directory not found (run 'npm run build')"
fi
echo ""

echo "======================================"
echo "📊 Test Results"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "${RED}Failed: $FAILED${NC}"
else
    echo -e "${GREEN}Failed: 0${NC}"
fi
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Milla 3.0 is ready!${NC}"
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Set your GEMINI_API_KEY in .env"
    echo "   2. Run: npm run dev"
    echo "   3. Open: http://localhost:3000"
    echo "   4. Tell Milla: 'open sandbox' or 'open studio'"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the errors above.${NC}"
    exit 1
fi
