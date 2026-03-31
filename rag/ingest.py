"""Load and clean raw documents before chunking."""
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Document:
    content: str
    source: str
    metadata: dict


class DocumentLoader:
    def load_file(self, path: Path) -> Document:
        """Load a single file. Handles .txt, .md, .pdf."""
        raise NotImplementedError

    def load_directory(self, path: Path, glob: str = "**/*") -> list[Document]:
        """Recursively load all matching files from a directory."""
        raise NotImplementedError
