"""JSON traversal utilities for extracting and updating string values."""

from typing import Any, List, Tuple, Union


def collect_string_paths(obj: Any, path: Tuple = ()) -> List[Tuple[Tuple, str]]:
    """
    Recursively collect all string values with their paths in a JSON structure.
    
    This function traverses a JSON structure (dicts, lists, and primitives) and
    extracts all string values along with their paths. Non-string values are
    ignored but the structure is preserved.
    
    Args:
        obj: The JSON object to traverse (dict, list, or primitive)
        path: Current path tuple (used for recursion)
        
    Returns:
        List of tuples where each tuple contains:
        - path: Tuple representing the path to the value (e.g., ('key1', 0, 'key2'))
        - value: The string value at that path
        
    Example:
        >>> data = {"name": "John", "age": 30, "items": ["apple", "banana"]}
        >>> collect_string_paths(data)
        [(('name',), 'John'), (('items', 0), 'apple'), (('items', 1), 'banana')]
    """
    result = []
    
    if isinstance(obj, dict):
        # Traverse dictionary
        for key, value in obj.items():
            new_path = path + (key,)
            if isinstance(value, str):
                # Found a string value
                result.append((new_path, value))
            elif isinstance(value, (dict, list)):
                # Recursively traverse nested structures
                result.extend(collect_string_paths(value, new_path))
            # Ignore non-string primitives (int, float, bool, None)
            
    elif isinstance(obj, list):
        # Traverse list
        for index, value in enumerate(obj):
            new_path = path + (index,)
            if isinstance(value, str):
                # Found a string value
                result.append((new_path, value))
            elif isinstance(value, (dict, list)):
                # Recursively traverse nested structures
                result.extend(collect_string_paths(value, new_path))
            # Ignore non-string primitives (int, float, bool, None)
    
    # If obj is a primitive (string, int, float, bool, None), handle at top level
    elif isinstance(obj, str) and path == ():
        # Top-level string
        result.append(((), obj))
    
    return result


def set_by_path(root: Any, path: Tuple, value: Any) -> None:
    """
    Set a value in a nested structure using a path tuple.
    
    This function modifies the root object in-place by navigating through
    the path and setting the final value.
    
    Args:
        root: The root JSON object (dict or list)
        path: Tuple representing the path to the value
        value: The new value to set
        
    Raises:
        KeyError: If a dictionary key in the path doesn't exist
        IndexError: If a list index in the path is out of range
        TypeError: If trying to index into a non-dict/list object
        
    Example:
        >>> data = {"user": {"name": "John", "items": ["apple", "banana"]}}
        >>> set_by_path(data, ('user', 'name'), 'Jane')
        >>> data
        {'user': {'name': 'Jane', 'items': ['apple', 'banana']}}
        >>> set_by_path(data, ('user', 'items', 0), 'orange')
        >>> data
        {'user': {'name': 'Jane', 'items': ['orange', 'banana']}}
    """
    if not path:
        # Empty path means we're trying to replace the root itself
        # This is not supported as we can't modify the root in-place
        raise ValueError("Cannot set value at empty path (root replacement not supported)")
    
    # Navigate to the parent of the target
    current = root
    for key in path[:-1]:
        if isinstance(current, dict):
            current = current[key]
        elif isinstance(current, list):
            current = current[key]
        else:
            raise TypeError(f"Cannot index into {type(current).__name__} with key {key}")
    
    # Set the final value
    final_key = path[-1]
    if isinstance(current, dict):
        current[final_key] = value
    elif isinstance(current, list):
        current[final_key] = value
    else:
        raise TypeError(f"Cannot set value in {type(current).__name__}")
