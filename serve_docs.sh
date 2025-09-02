#!/bin/bash
# serve_docs.sh - Serve documentation locally

echo "Coffee Machine Documentation Server"
echo "=================================="

# Check if MkDocs is installed
if ! command -v mkdocs &> /dev/null; then
    echo "MkDocs not found. Installing documentation dependencies..."
    pip install mkdocs mkdocs-material mkdocstrings[python]
fi

# Start the development server
echo "Starting documentation server..."
echo "Visit http://localhost:8000 to view the documentation"
echo "Press Ctrl+C to stop the server"

mkdocs serve