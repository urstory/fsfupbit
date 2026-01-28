#!/bin/bash

# fsfupbit Package Verification Script
# This script verifies the package is ready for PyPI deployment

set -e

echo "=========================================="
echo "fsfupbit Package Verification"
echo "=========================================="

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check required files
echo ""
echo "Checking required files..."

required_files=("setup.py" "requirements.txt" "MANIFEST.in" "README.md" "LICENSE" "pyupbit/__init__.py" "docs/api.md" "docs/development.md" "docs/changelog.md" "docs/deployment.md")

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - MISSING!"
        exit 1
    fi
done

# Check package structure
echo ""
echo "Checking package structure..."

pyupbit_files=("pyupbit/__init__.py" "pyupbit/quotation_api.py" "pyupbit/exchange_api.py" "pyupbit/websocket_api.py" "pyupbit/request_api.py" "pyupbit/errors.py")

for file in "${pyupbit_files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
    else
        echo -e "${RED}✗${NC} $file - MISSING!"
        exit 1
    fi
done

# Check version in setup.py
echo ""
echo "Checking version..."

VERSION=$(grep "version='.*'" setup.py | grep -o "[0-9.]*")
if [ "$VERSION" == "1.0.0" ]; then
    echo -e "${GREEN}✓${NC} Version: $VERSION"
else
    echo -e "${YELLOW}⚠${NC} Version: $VERSION (expected 1.0.0)"
fi

# Check dependencies
echo ""
echo "Checking dependencies..."

if grep -q "pyjwt" requirements.txt; then
    echo -e "${GREEN}✓${NC} pyjwt dependency found"
else
    echo -e "${RED}✗${NC} pyjwt dependency missing"
    exit 1
fi

if grep -q "websockets" requirements.txt; then
    echo -e "${GREEN}✓${NC} websockets dependency found"
else
    echo -e "${RED}✗${NC} websockets dependency missing"
    exit 1
fi

# Check tests
echo ""
echo "Checking tests..."

if [ -d "tests" ]; then
    test_count=$(find tests -name "test_*.py" | wc -l)
    echo -e "${GREEN}✓${NC} Tests directory found ($test_count test files)"
else
    echo -e "${RED}✗${NC} Tests directory missing"
    exit 1
fi

# Run tests
echo ""
echo "Running tests..."

if pytest --q; then
    echo -e "${GREEN}✓${NC} All tests passed"
else
    echo -e "${RED}✗${NC} Some tests failed"
    exit 1
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Package verification complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Build package: python -m build"
echo "2. Check package: twine check dist/*"
echo "3. Upload to TestPyPI: twine upload --repository testpypi dist/*"
echo "4. Upload to PyPI: twine upload dist/*"
echo ""
