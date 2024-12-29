"""
Obsidian note handling utilities
"""
import os
from datetime import datetime
import frontmatter
from pathlib import Path
from typing import Dict, List, Optional

class ObsidianNote:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {vault_path}")

    def create_note(self, title: str, content: str, metadata: Optional[Dict] = None) -> Path:
        """
        Create a new note with the given title and content
        """
        # Sanitize title for filename
        filename = title.replace(" ", "_").lower() + ".md"
        file_path = self.vault_path / filename

        # Create frontmatter
        note = frontmatter.Post(content)
        if metadata:
            note.metadata.update(metadata)
        
        # Add default metadata
        note.metadata['created'] = datetime.now().isoformat()
        note.metadata['title'] = title

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(note))

        return file_path

    def update_note(self, file_path: Path, content: str, append: bool = True) -> None:
        """
        Update an existing note
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Note not found: {file_path}")

        # Read existing note
        with open(file_path, 'r', encoding='utf-8') as f:
            note = frontmatter.load(f)

        # Update content
        if append:
            note.content += f"\n\n{content}"
        else:
            note.content = content

        # Update modified timestamp
        note.metadata['modified'] = datetime.now().isoformat()

        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter.dumps(note))

    def find_related_notes(self, keywords: List[str]) -> List[Path]:
        """
        Find related notes based on keywords
        """
        related_notes = []
        for file_path in self.vault_path.glob("**/*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()
                if any(keyword.lower() in content for keyword in keywords):
                    related_notes.append(file_path)
        return related_notes

    def create_link(self, title: str) -> str:
        """
        Create an Obsidian link format
        """
        return f"[[{title}]]"
