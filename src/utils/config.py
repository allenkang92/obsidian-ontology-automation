"""
Configuration management utilities
"""
import os
from pathlib import Path
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        # Load API key
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Load vault path
        self.vault_path = os.getenv('OBSIDIAN_VAULT_PATH')
        if not self.vault_path:
            raise ValueError("OBSIDIAN_VAULT_PATH not found in environment variables")
        
        # Validate vault path
        vault_path = Path(self.vault_path)
        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
        
        # Default settings
        self.settings = {
            'default_summary_length': 'medium',  # short, medium, long
            'auto_link_keywords': True,
            'append_mode': True,  # True: append to existing notes, False: create new notes
        }
    
    def update_settings(self, **kwargs):
        """
        Update settings with new values
        """
        self.settings.update(kwargs)
