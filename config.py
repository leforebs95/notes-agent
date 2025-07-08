"""
Configuration settings for the Handwritten Notes MCP Server
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory for the project
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
INDEX_DIR = DATA_DIR / "index"

# Ensure directories exist
for dir_path in [DATA_DIR, RAW_DIR, PROCESSED_DIR, INDEX_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Document processing settings
SUPPORTED_FILE_EXTENSIONS = {".txt", ".md", ".text"}
MAX_CHUNK_SIZE = 1000  # Maximum characters per chunk
CHUNK_OVERLAP = 100    # Overlap between chunks

# Search settings
MAX_SEARCH_RESULTS = 10
KEYWORD_SEARCH_THRESHOLD = 0.6  # Fuzzy matching threshold
SEMANTIC_SEARCH_THRESHOLD = 0.7  # Semantic similarity threshold

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "notes_mcp_server.log"

# MCP Server settings
SERVER_NAME = "notes-mcp-server"
SERVER_VERSION = "1.0.0"