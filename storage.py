"""
Storage system for managing documents and search indexes
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import orjson
from loguru import logger
from anthropic import AsyncAnthropic

from config import PROCESSED_DIR, INDEX_DIR, RAW_DIR, ANTHROPIC_API_KEY


class DocumentStorage:
    """Manages document storage and metadata"""
    
    # Initialize Anthropic client as class variable
    anthropic_client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
    
    def __init__(self):
        self.metadata_file = INDEX_DIR / "document_metadata.json"
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load document metadata from storage"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'rb') as f:
                    return orjson.loads(f.read())
            except Exception as e:
                logger.warning(f"Failed to load metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """Save document metadata to storage"""
        try:
            with open(self.metadata_file, 'wb') as f:
                f.write(orjson.dumps(self.metadata, option=orjson.OPT_INDENT_2))
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash file {file_path}: {e}")
            return ""
    
    def get_raw_files(self) -> List[Path]:
        """Get all raw text files"""
        files = []
        for ext in [".txt", ".md", ".text"]:
            files.extend(RAW_DIR.glob(f"*{ext}"))
        return sorted(files)
    
    def get_processed_files(self) -> List[Path]:
        """Get all processed files"""
        files = []
        for ext in [".txt", ".md", ".text"]:
            files.extend(PROCESSED_DIR.glob(f"*{ext}"))
        return sorted(files)
    
    def file_needs_processing(self, raw_file: Path) -> bool:
        """Check if a raw file needs processing"""
        if not raw_file.exists():
            return False
        
        file_key = str(raw_file.name)
        current_hash = self._get_file_hash(raw_file)
        
        # Check if file is new or changed
        if file_key not in self.metadata:
            return True
        
        stored_hash = self.metadata[file_key].get("hash", "")
        return current_hash != stored_hash
    
    def mark_file_processed(self, raw_file: Path, processed_file: Path):
        """Mark a file as processed and update metadata"""
        file_key = str(raw_file.name)
        
        self.metadata[file_key] = {
            "hash": self._get_file_hash(raw_file),
            "processed_at": datetime.now().isoformat(),
            "raw_path": str(raw_file),
            "processed_path": str(processed_file),
            "size": raw_file.stat().st_size if raw_file.exists() else 0
        }
        
        self._save_metadata()
        logger.info(f"Marked {raw_file.name} as processed")
    
    def get_document_info(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific document"""
        return self.metadata.get(filename)
    
    def list_all_documents(self) -> Dict[str, Any]:
        """List all documents with their metadata"""
        return self.metadata
    
    def read_raw_file(self, filename: str) -> Optional[str]:
        """Read content from a raw file"""
        raw_file = RAW_DIR / filename
        if not raw_file.exists():
            return None
        
        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {filename}: {e}")
            return None
    
    def read_processed_file(self, filename: str) -> Optional[str]:
        """Read content from a processed file"""
        processed_file = PROCESSED_DIR / filename
        if not processed_file.exists():
            return None
        
        try:
            with open(processed_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read processed {filename}: {e}")
            return None
    
    def write_processed_file(self, filename: str, content: str) -> bool:
        """Write content to a processed file"""
        processed_file = PROCESSED_DIR / filename
        
        try:
            with open(processed_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"Saved processed file: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to write processed {filename}: {e}")
            return False
    
    def get_files_needing_processing(self) -> List[Path]:
        """Get list of files that need processing"""
        raw_files = self.get_raw_files()
        return [f for f in raw_files if self.file_needs_processing(f)]
    
    async def process_raw_file(self, filename: str) -> str:
        """Process a raw file through LLM to improve formatting and fix OCR errors"""
        
        # Check if API key is available
        if not self.anthropic_client:
            return "Error: ANTHROPIC_API_KEY not configured. Please set the API key in your environment."
        
        # Check if file exists and needs processing
        raw_file = RAW_DIR / filename
        if not raw_file.exists():
            return f"Error: File '{filename}' not found in raw directory"
        
        # Read raw file content
        raw_content = self.read_raw_file(filename)
        if raw_content is None:
            return f"Error: Could not read file '{filename}'"
        
        try:
            # Process the content through LLM
            logger.info(f"Processing file {filename} through LLM...")
            
            system_prompt = """You are a document processor that improves handwritten text that has been converted through OCR. Your task is to:

1. Fix OCR errors and typos
2. Improve formatting and structure
3. Maintain the original meaning and content
4. Organize the text into proper paragraphs
5. Fix punctuation and capitalization
6. Preserve important information like dates, names, numbers

Return only the cleaned and formatted text without any additional commentary or explanation."""

            response = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Please process and improve this handwritten text:\n\n{raw_content}"
                    }
                ]
            )
            
            processed_content = response.content[0].text
            
            # Write processed content to file
            if self.write_processed_file(filename, processed_content):
                # Update metadata
                self.mark_file_processed(raw_file, PROCESSED_DIR / filename)
                
                return f"✅ Successfully processed '{filename}'\n\nProcessed content saved to: {PROCESSED_DIR / filename}\n\nPreview of processed content:\n{processed_content[:300]}{'...' if len(processed_content) > 300 else ''}"
            else:
                return f"Error: Failed to save processed content for '{filename}'"
        
        except Exception as e:
            logger.error(f"Error processing file {filename}: {e}")
            return f"Error processing file '{filename}': {str(e)}"