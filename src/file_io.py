"""File I/O operations for JSON translation."""

import json
import os
from pathlib import Path
from typing import Any, Dict

from src.config import FILE_ENCODING, JSON_INDENT, JSON_ENSURE_ASCII


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load and parse JSON file, raise error if invalid.
    
    Args:
        filepath: Path to the JSON file to load
        
    Returns:
        Parsed JSON data as a dictionary or other JSON-compatible type
        
    Raises:
        FileNotFoundError: If the file does not exist
        json.JSONDecodeError: If the file contains invalid JSON
        
    Example:
        >>> data = load_json_file("es.json")
        >>> print(data["greeting"])
    """
    file_path = Path(filepath)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Load and parse JSON
    try:
        with open(file_path, 'r', encoding=FILE_ENCODING) as f:
            data = json.load(f)
        return data
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in file {filepath}: {e.msg}",
            e.doc,
            e.pos
        )


def validate_json_structure(data: Any) -> bool:
    """
    Validate that JSON structure is supported.
    
    Args:
        data: The JSON data to validate
        
    Returns:
        True if the structure is valid and supported
        
    Note:
        Currently accepts all valid JSON structures (objects, arrays, primitives)
    """
    # All valid JSON structures are supported
    # This includes: dict, list, str, int, float, bool, None
    return True


def ensure_output_directory(directory: str) -> None:
    """
    Create output directory if it doesn't exist and handle permission errors gracefully.
    
    Args:
        directory: Path to the output directory
        
    Raises:
        PermissionError: If the directory cannot be created due to insufficient permissions
        OSError: If the directory cannot be created for other reasons
        
    Example:
        >>> ensure_output_directory("./translations")
        >>> ensure_output_directory("/path/to/output")
    """
    dir_path = Path(directory)
    
    # If directory already exists, verify it's writable
    if dir_path.exists():
        if not dir_path.is_dir():
            raise NotADirectoryError(f"Path exists but is not a directory: {directory}")
        
        # Check if directory is writable
        if not os.access(dir_path, os.W_OK):
            raise PermissionError(f"Directory is not writable: {directory}")
        
        return
    
    # Try to create the directory
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except PermissionError as e:
        raise PermissionError(f"Cannot create directory due to insufficient permissions: {directory}") from e
    except OSError as e:
        raise OSError(f"Cannot create directory: {directory}") from e


def serialize_json(data: Any, filepath: str) -> None:
    """
    Serialize JSON with consistent formatting.
    
    Args:
        data: The JSON data to serialize
        filepath: Path where the JSON file should be written
        
    Format:
        - Indentation: From config (default: 2 spaces)
        - Encoding: From config (default: UTF-8)
        - Unicode: Not escaped (from config)
        
    Example:
        >>> data = {"greeting": "Hola", "count": 5}
        >>> serialize_json(data, "output.json")
    """
    file_path = Path(filepath)
    
    # Create parent directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON with consistent formatting from config
    with open(file_path, 'w', encoding=FILE_ENCODING) as f:
        json.dump(data, f, ensure_ascii=JSON_ENSURE_ASCII, indent=JSON_INDENT)
