#!/bin/bash
# Script to run all linters on the project

set -e  # Exit on any error

PYTHON_DIRS="dags plugins"
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Running linters on Python code...${NC}"

echo -e "\n${YELLOW}Running black (code formatter)...${NC}"
poetry run black $PYTHON_DIRS --check
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Black formatting check passed${NC}"
else
    echo -e "${RED}✗ Black formatting check failed. Run 'poetry run black $PYTHON_DIRS' to fix.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Running isort (import sorter)...${NC}"
poetry run isort $PYTHON_DIRS --check --profile black
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ isort check passed${NC}"
else
    echo -e "${RED}✗ isort check failed. Run 'poetry run isort $PYTHON_DIRS --profile black' to fix.${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Running flake8 (style guide enforcer)...${NC}"
poetry run flake8 $PYTHON_DIRS
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ flake8 check passed${NC}"
else
    echo -e "${RED}✗ flake8 check failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Running pylint (code analysis)...${NC}"
poetry run pylint $PYTHON_DIRS
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ pylint check passed${NC}"
else
    echo -e "${RED}✗ pylint check failed${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Running mypy (type checking)...${NC}"
poetry run mypy $PYTHON_DIRS
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ mypy check passed${NC}"
else
    echo -e "${RED}✗ mypy check failed${NC}"
    exit 1
fi

echo -e "\n${GREEN}All linting checks passed!${NC}"
