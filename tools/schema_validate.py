#!/usr/bin/env python3
"""
Schema Validator

Lightweight CLI validation with optional strict jsonschema-based checks.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional


def validate_json_syntax(filepath: Path) -> bool:
    """
    Lightweight JSON syntax validation.
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        True if valid JSON, False otherwise
    """
    try:
        with open(filepath, 'r') as f:
            json.load(f)
        return True
    except json.JSONDecodeError as e:
        print(f"JSON syntax error in {filepath}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)
        return False


def validate_with_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Strict validation using jsonschema library.
    
    Args:
        data: JSON data to validate
        schema: JSON schema
        
    Returns:
        True if data matches schema, False otherwise
    """
    try:
        import jsonschema
        
        jsonschema.validate(instance=data, schema=schema)
        return True
        
    except ImportError:
        print("Warning: jsonschema not available, skipping schema validation", 
              file=sys.stderr)
        return True  # Don't fail if library not available
        
    except jsonschema.ValidationError as e:
        print(f"Schema validation error: {e.message}", file=sys.stderr)
        if e.path:
            print(f"At path: {'.'.join(str(p) for p in e.path)}", file=sys.stderr)
        return False
        
    except jsonschema.SchemaError as e:
        print(f"Invalid schema: {e.message}", file=sys.stderr)
        return False


def load_json(filepath: Path) -> Optional[Dict[str, Any]]:
    """Load JSON from file."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Validate JSON files with optional schema checking"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="JSON file to validate"
    )
    parser.add_argument(
        "-s", "--schema",
        type=Path,
        help="JSON schema file for strict validation (requires jsonschema)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if jsonschema library is not available"
    )
    
    args = parser.parse_args()
    
    # Validate file exists
    if not args.input.exists():
        print(f"Error: File {args.input} not found", file=sys.stderr)
        return 1
    
    # Lightweight syntax validation
    print(f"Validating JSON syntax: {args.input}")
    if not validate_json_syntax(args.input):
        return 1
    
    print("✓ JSON syntax valid")
    
    # Schema validation if requested
    if args.schema:
        if not args.schema.exists():
            print(f"Error: Schema file {args.schema} not found", file=sys.stderr)
            return 1
        
        print(f"Validating against schema: {args.schema}")
        
        data = load_json(args.input)
        schema = load_json(args.schema)
        
        if data is None or schema is None:
            return 1
        
        try:
            import jsonschema
            has_jsonschema = True
        except ImportError:
            has_jsonschema = False
            
        if not has_jsonschema:
            if args.strict:
                print("Error: jsonschema library required for --strict mode", 
                      file=sys.stderr)
                return 1
            else:
                print("Warning: jsonschema not available, skipping schema validation")
                return 0
        
        if not validate_with_schema(data, schema):
            return 1
        
        print("✓ Schema validation passed")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
