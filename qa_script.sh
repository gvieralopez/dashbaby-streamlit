#!/bin/bash

# This script is intended for CI/CD. You can use locally too if you don't want to
# install pre-commits or run pytest manually.

# Function to check exit status and exit script if non-zero
check_exit_status() {
    if [ $? -ne 0 ]; then
        printf "\e[91m[QA] One or more checks failed. Exiting...\e[0m"
        exit 1
    fi
}

# Run ruff for linting
printf "\n\e[1;34mRunning Ruff Linter\e[0m\n"
ruff check --fix
check_exit_status

# Run ruff format for code formatting
printf "\n\e[1;34mRunning Ruff Format\e[0m\n"
ruff format
check_exit_status

# Run mypy for type checking
printf "\n\e[1;34mRunning Mypy\e[0m\n"
mypy .
check_exit_status

# Run pytest for unit testing
printf "\n\e[1;34mRunning Pytest\e[0m\n"
pytest
check_exit_status

# Exit 0 if all check passed
printf "\e[92m[QA] All checks passed successfully.\e[0m"
