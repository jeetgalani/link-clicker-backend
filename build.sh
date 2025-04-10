#!/bin/bash
set -e

echo "🧪 Installing Python dependencies..."
pip install -r requirements.txt

echo "📦 Installing Playwright browser binaries..."
npx playwright install chromium