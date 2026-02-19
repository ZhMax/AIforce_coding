#!/usr/bin/env python3
"""
Bot Configuration Validator
============================

Standalone module for validating bot configurations against JSON Schema.

Usage:
    from bot_config_validator import BotConfigValidator

    validator = BotConfigValidator("bot_import_schema_v2.json")
    is_valid, errors = validator.validate(bot_config)

    if is_valid:
        print("Configuration is valid!")
    else:
        print(f"Validation failed: {errors}")
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from jsonschema import Draft7Validator, ValidationError
    from jsonschema.exceptions import SchemaError
except ImportError:
    raise ImportError(
        "jsonschema package is required. Install it with: pip install jsonschema"
    )


class ConfigValidator:
    """Validator for bot configuration against JSON Schema"""

    def __init__(self, schema_path: str):
        """
        Initialize validator with schema file

        Args:
            schema_path: Path to JSON Schema file

        Raises:
            FileNotFoundError: If schema file doesn't exist
            ValueError: If schema is invalid
        """
        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)

    def _load_schema(self) -> dict:
        """Load and validate JSON Schema file"""
        if not self.schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {self.schema_path}")

        try:
            with open(self.schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in schema file: {e}")

        # Validate schema itself
        try:
            Draft7Validator.check_schema(schema)
        except SchemaError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")

        return schema

    def validate(
        self, config: dict, verbose: bool = False
    ) -> Tuple[bool, Optional[List[str]]]:
        """
        Validate bot configuration

        Args:
            config: Bot configuration to validate
            verbose: If True, return detailed error messages

        Returns:
            Tuple of (is_valid, error_messages)
            - is_valid: True if valid, False otherwise
            - error_messages: List of error messages if invalid, None if valid
        """
        try:
            self.validator.validate(config)
            return True, None
        except ValidationError:
            errors = self._collect_errors(config, verbose)
            return False, errors

    def _collect_errors(self, config: dict, verbose: bool = False) -> List[str]:
        """Collect all validation errors"""
        errors = []
        validation_errors = sorted(self.validator.iter_errors(config), key=str)

        for error in validation_errors:
            error_msg = self._format_error(error, verbose)
            errors.append(error_msg)

        return errors

    def _format_error(self, error: ValidationError, verbose: bool = False) -> str:
        """Format validation error message"""
        # Build path to error location
        if error.path:
            path = " -> ".join(str(p) for p in error.path)
            location = f"at '{path}'"
        else:
            location = "at root"

        # Basic error message
        message = f"{location}: {error.message}"

        # Add verbose details
        if verbose:
            details = []

            if error.validator_value:
                details.append(f"Expected: {error.validator_value}")

            if error.instance is not None:
                instance_str = str(error.instance)
                if len(instance_str) > 100:
                    instance_str = instance_str[:97] + "..."
                details.append(f"Got: {instance_str}")

            if details:
                message += "\n  " + "\n  ".join(details)

        return message

    def validate_file(
        self, config_path: str, verbose: bool = False
    ) -> Tuple[bool, Optional[List[str]]]:
        """
        Validate bot configuration from file

        Args:
            config_path: Path to bot configuration JSON file
            verbose: If True, return detailed error messages

        Returns:
            Tuple of (is_valid, error_messages)
        """
        config_file = Path(config_path)

        if not config_file.exists():
            return False, [f"Configuration file not found: {config_path}"]

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON in configuration file: {e}"]

        return self.validate(config, verbose)

    def get_required_fields(self, path: str = "") -> List[str]:
        """
        Get list of required fields at given path

        Args:
            path: Dot-separated path (e.g., "data.attributes")

        Returns:
            List of required field names
        """
        schema_part = self.schema

        if path:
            for part in path.split("."):
                if "properties" in schema_part:
                    schema_part = schema_part["properties"].get(part, {})
                else:
                    return []

        return schema_part.get("required", [])

    def print_validation_report(self, config: dict, show_valid: bool = True) -> bool:
        """
        Print detailed validation report

        Args:
            config: Bot configuration to validate
            show_valid: If True, print success message for valid config

        Returns:
            True if valid, False otherwise
        """
        print("=" * 70)
        print("Bot Configuration Validation Report")
        print("=" * 70)

        is_valid, errors = self.validate(config, verbose=True)

        if is_valid:
            if show_valid:
                print("Configuration is VALID")
                print("Summary:")
                print(f"   Schema: {self.schema_path.name}")
                print(
                    f"   Bot Name: {config.get('data', {}).get('attributes', {}).get('bot_name', 'N/A')}"
                )
                print(
                    f"   Scenarios: {len(config.get('data', {}).get('attributes', {}).get('scenarios', []))}"
                )
        else:
            print("Configuration is INVALID")
            print(f"Found {len(errors)} validation error(s):")
            print()
            for idx, error in enumerate(errors, 1):
                print(f"{idx}. {error}")
                print()

        print("=" * 70)
        return is_valid


def validate_bot_config_quick(
    config: dict, schema_path: str = "bot_import_schema_v2.json"
) -> bool:
    """
    Quick validation function - returns True if valid, False otherwise

    Args:
        config: Bot configuration to validate
        schema_path: Path to JSON Schema file

    Returns:
        True if valid, False otherwise
    """
    try:
        validator = ConfigValidator(schema_path)
        is_valid, _ = validator.validate(config)
        return is_valid
    except Exception as e:
        print(f"Validation error: {e}")
        return False


def main():
    """CLI for validating bot configuration files"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate bot configuration against JSON Schema"
    )
    parser.add_argument(
        "config_file", help="Path to bot configuration JSON file to validate"
    )
    parser.add_argument(
        "-s",
        "--schema",
        default="bot_import_schema_v2.json",
        help="Path to JSON Schema file (default: bot_import_schema_v2.json)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed error messages"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only return exit code (0=valid, 1=invalid)",
    )

    args = parser.parse_args()

    try:
        validator = ConfigValidator(args.schema)

        if args.quiet:
            is_valid, _ = validator.validate_file(args.config_file)
            exit(0 if is_valid else 1)

        # Load and validate
        with open(args.config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        is_valid = validator.print_validation_report(config)

        if is_valid and not args.quiet:
            print("\n✅ Validation passed!")
            exit(0)
        else:
            print("\n❌ Validation failed!")
            exit(1)

    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"❌ Error: {e}")
        exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        exit(1)


if __name__ == "__main__":
    main()
