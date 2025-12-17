#!/usr/bin/env python3
"""
Basic tests for tools functionality.
"""

import unittest
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))


class TestToolsImports(unittest.TestCase):
    """Test that all tool modules can be imported."""
    
    def test_import_schema_validate(self):
        """Test schema_validate module import."""
        try:
            import schema_validate
            self.assertTrue(hasattr(schema_validate, 'validate_json_syntax'))
            self.assertTrue(hasattr(schema_validate, 'validate_with_schema'))
        except ImportError as e:
            self.fail(f"Failed to import schema_validate: {e}")
    
    def test_import_generate_tangents(self):
        """Test generate_tangents module import."""
        try:
            import generate_tangents
            self.assertTrue(hasattr(generate_tangents, 'compute_tangents'))
            self.assertTrue(hasattr(generate_tangents, 'load_mesh_data'))
            self.assertTrue(hasattr(generate_tangents, 'save_tangents_json'))
        except ImportError as e:
            self.fail(f"Failed to import generate_tangents: {e}")


class TestSchemaValidate(unittest.TestCase):
    """Tests for schema validation."""
    
    def test_validate_json_syntax_simple(self):
        """Test JSON syntax validation with simple valid JSON."""
        import tempfile
        import schema_validate
        
        # Create temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value", "number": 42}')
            temp_path = Path(f.name)
        
        try:
            result = schema_validate.validate_json_syntax(temp_path)
            self.assertTrue(result)
        finally:
            temp_path.unlink()
    
    def test_validate_json_syntax_invalid(self):
        """Test JSON syntax validation with invalid JSON."""
        import tempfile
        import schema_validate
        
        # Create temporary invalid JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value",}')  # Trailing comma
            temp_path = Path(f.name)
        
        try:
            result = schema_validate.validate_json_syntax(temp_path)
            self.assertFalse(result)
        finally:
            temp_path.unlink()


class TestRendererPlugin(unittest.TestCase):
    """Tests for renderer plugin."""
    
    def test_import_renderer(self):
        """Test that renderer plugin can be imported."""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'plugins'))
        try:
            import renderer
            self.assertTrue(hasattr(renderer, 'RendererPlugin'))
        except ImportError as e:
            self.fail(f"Failed to import renderer: {e}")
        finally:
            sys.path.pop(0)
    
    def test_renderer_plugin_init(self):
        """Test renderer plugin initialization."""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'tools' / 'plugins'))
        try:
            from renderer import RendererPlugin
            
            plugin = RendererPlugin("test_renderer")
            self.assertEqual(plugin.renderer_cmd, "test_renderer")
            self.assertIsNotNone(plugin.working_dir)
        except ImportError as e:
            self.fail(f"Failed to import renderer: {e}")
        finally:
            sys.path.pop(0)


if __name__ == '__main__':
    unittest.main()
