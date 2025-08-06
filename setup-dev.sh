#!/bin/bash

echo "Setting up dev environment..."

pip install -r requirements-dev.txt

pre-commit install --hook-type commit-msg
git config core.hooksPath .githooks
git config --global alias.commit '!cz commit'

echo "✅ Dev environment ready. Use 'git commit' → will block. Use 'cz commit' instead."
