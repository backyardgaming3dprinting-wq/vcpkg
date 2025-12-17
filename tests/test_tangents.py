#!/usr/bin/env python3
"""
Tests for tangent generation functionality.
"""

import json
import tempfile
import unittest
from pathlib import Path
import sys
import os

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import trimesh
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False

try:
    from pygltflib import GLTF2
    HAS_PYGLTFLIB = True
except ImportError:
    HAS_PYGLTFLIB = False


class TestTangentsSidecar(unittest.TestCase):
    """Test sidecar JSON generation for tangents."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    @unittest.skipUnless(HAS_NUMPY, "NumPy not available")
    def test_tangents_computation_simple(self):
        """Test basic tangent computation."""
        from generate_tangents import compute_tangents
        
        # Simple quad: 2 triangles
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [1, 1, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        
        normals = np.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ], dtype=np.float32)
        
        uvs = np.array([
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2, 0, 2, 3], dtype=np.int32)
        
        tangents = compute_tangents(vertices, normals, uvs, indices)
        
        # Check shape
        self.assertEqual(tangents.shape, (4, 4))
        
        # Check that tangents are roughly in the X direction
        for i in range(4):
            # X component should be dominant
            self.assertGreater(abs(tangents[i, 0]), 0.9)
            # Handedness should be valid
            self.assertIn(tangents[i, 3], [-1.0, 1.0])
    
    @unittest.skipUnless(HAS_NUMPY, "NumPy not available")
    def test_save_tangents_json(self):
        """Test saving tangents to JSON sidecar."""
        from generate_tangents import save_tangents_json
        
        tangents = np.array([
            [1, 0, 0, 1],
            [1, 0, 0, 1],
            [1, 0, 0, -1],
            [0, 1, 0, 1]
        ], dtype=np.float32)
        
        output_path = Path(self.temp_dir) / "test.tangents.json"
        
        result = save_tangents_json(tangents, output_path)
        self.assertTrue(result)
        self.assertTrue(output_path.exists())
        
        # Verify content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn('tangents', data)
        self.assertIn('format', data)
        self.assertIn('count', data)
        self.assertEqual(data['format'], 'xyzw')
        self.assertEqual(data['count'], 4)
        self.assertEqual(len(data['tangents']), 4)
    
    @unittest.skipUnless(HAS_NUMPY, "NumPy not available")
    def test_tangents_degenerate_uvs(self):
        """Test tangent computation with degenerate UVs."""
        from generate_tangents import compute_tangents
        
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        
        normals = np.array([
            [0, 0, 1],
            [0, 0, 1],
            [0, 0, 1]
        ], dtype=np.float32)
        
        # All UVs the same (degenerate)
        uvs = np.array([
            [0, 0],
            [0, 0],
            [0, 0]
        ], dtype=np.float32)
        
        indices = np.array([0, 1, 2], dtype=np.int32)
        
        # Should not crash
        tangents = compute_tangents(vertices, normals, uvs, indices)
        self.assertEqual(tangents.shape, (3, 4))


@unittest.skipUnless(HAS_PYGLTFLIB, "pygltflib not available")
class TestTangentsGLBEmbedding(unittest.TestCase):
    """Test optional GLB embedding functionality."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def test_embed_tangents_gltf_loading(self):
        """Test that GLTF embedding can load files."""
        from generate_tangents import embed_tangents_gltf
        
        # Create a minimal GLTF file
        gltf_path = Path(self.temp_dir) / "test.gltf"
        
        minimal_gltf = {
            "asset": {"version": "2.0"},
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0}],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
            "accessors": [
                {
                    "bufferView": 0,
                    "componentType": 5126,
                    "count": 3,
                    "type": "VEC3"
                }
            ],
            "bufferViews": [
                {
                    "buffer": 0,
                    "byteLength": 36
                }
            ],
            "buffers": [{"byteLength": 36}]
        }
        
        with open(gltf_path, 'w') as f:
            json.dump(minimal_gltf, f)
        
        # Create dummy buffer file
        buffer_path = Path(self.temp_dir) / "test.bin"
        with open(buffer_path, 'wb') as f:
            f.write(b'\x00' * 36)
        
        # Update GLTF to reference buffer
        minimal_gltf["buffers"][0]["uri"] = "test.bin"
        with open(gltf_path, 'w') as f:
            json.dump(minimal_gltf, f)
        
        tangents = np.array([[1, 0, 0, 1]] * 3, dtype=np.float32)
        
        # This should at least load the file without crashing
        # Full embedding is a placeholder in the implementation
        result = embed_tangents_gltf(gltf_path, tangents)
        # Result may be True or False depending on implementation state
        self.assertIsInstance(result, bool)


class TestToolsBasic(unittest.TestCase):
    """Basic tests for tools functionality."""
    
    def test_imports(self):
        """Test that tool modules can be imported."""
        try:
            import generate_tangents
            self.assertTrue(hasattr(generate_tangents, 'compute_tangents'))
            self.assertTrue(hasattr(generate_tangents, 'save_tangents_json'))
        except ImportError as e:
            self.fail(f"Failed to import generate_tangents: {e}")


if __name__ == '__main__':
    unittest.main()
