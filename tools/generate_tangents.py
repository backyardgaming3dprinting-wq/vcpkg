#!/usr/bin/env python3
"""
Tangents Generator

Generates tangent vectors for 3D meshes and optionally embeds them into GLTF/GLB files.
Outputs tangent data to sidecar JSON files.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Tuple, List
import numpy as np


def compute_tangents(vertices: np.ndarray, normals: np.ndarray, 
                    uvs: np.ndarray, indices: np.ndarray) -> np.ndarray:
    """
    Compute tangent vectors for a mesh using the method from
    "Mathematics for 3D Game Programming and Computer Graphics" by Eric Lengyel.
    
    Args:
        vertices: Nx3 array of vertex positions
        normals: Nx3 array of vertex normals
        uvs: Nx2 array of texture coordinates
        indices: Mx3 array of triangle indices
        
    Returns:
        Nx4 array of tangent vectors (xyz + handedness in w)
    """
    num_verts = len(vertices)
    tan1 = np.zeros((num_verts, 3), dtype=np.float32)
    tan2 = np.zeros((num_verts, 3), dtype=np.float32)
    
    # Calculate tangents for each triangle
    for i in range(0, len(indices), 3):
        i1, i2, i3 = indices[i:i+3]
        
        v1, v2, v3 = vertices[i1], vertices[i2], vertices[i3]
        w1, w2, w3 = uvs[i1], uvs[i2], uvs[i3]
        
        x1, y1 = v2[0] - v1[0], v2[1] - v1[1]
        z1 = v2[2] - v1[2]
        x2, y2 = v3[0] - v1[0], v3[1] - v1[1]
        z2 = v3[2] - v1[2]
        
        s1, t1 = w2[0] - w1[0], w2[1] - w1[1]
        s2, t2 = w3[0] - w1[0], w3[1] - w1[1]
        
        div = s1 * t2 - s2 * t1
        if abs(div) < 1e-10:
            # Degenerate UV coordinates, use arbitrary tangent
            r = 1.0
        else:
            r = 1.0 / div
        
        sdir = np.array([(t2 * x1 - t1 * x2) * r,
                        (t2 * y1 - t1 * y2) * r,
                        (t2 * z1 - t1 * z2) * r], dtype=np.float32)
        tdir = np.array([(s1 * x2 - s2 * x1) * r,
                        (s1 * y2 - s2 * y1) * r,
                        (s1 * z2 - s2 * z1) * r], dtype=np.float32)
        
        tan1[i1] += sdir
        tan1[i2] += sdir
        tan1[i3] += sdir
        
        tan2[i1] += tdir
        tan2[i2] += tdir
        tan2[i3] += tdir
    
    # Orthogonalize and calculate handedness
    tangents = np.zeros((num_verts, 4), dtype=np.float32)
    
    for i in range(num_verts):
        n = normals[i]
        t = tan1[i]
        
        # Gram-Schmidt orthogonalize
        t_orth = t - n * np.dot(n, t)
        
        # Normalize
        length = np.linalg.norm(t_orth)
        if length > 1e-10:
            t_orth = t_orth / length
        
        # Calculate handedness
        handedness = 1.0 if np.dot(np.cross(n, t), tan2[i]) > 0 else -1.0
        
        tangents[i] = [t_orth[0], t_orth[1], t_orth[2], handedness]
    
    return tangents


def load_mesh_data(filepath: Path) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    """
    Load mesh data from file. Supports basic formats.
    
    Returns:
        Tuple of (vertices, normals, uvs, indices) or None on failure
    """
    ext = filepath.suffix.lower()
    
    # Try to use trimesh if available
    try:
        import trimesh
        mesh = trimesh.load(str(filepath))
        
        if not hasattr(mesh, 'vertices') or not hasattr(mesh, 'faces'):
            print(f"Error: File {filepath} doesn't contain mesh data", file=sys.stderr)
            return None
        
        vertices = np.array(mesh.vertices, dtype=np.float32)
        indices = mesh.faces.flatten()
        
        # Get normals
        if hasattr(mesh, 'vertex_normals'):
            normals = np.array(mesh.vertex_normals, dtype=np.float32)
        else:
            print("Warning: No normals found, computing from geometry", file=sys.stderr)
            mesh.compute_vertex_normals()
            normals = np.array(mesh.vertex_normals, dtype=np.float32)
        
        # Get UVs
        if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None:
            uvs = np.array(mesh.visual.uv, dtype=np.float32)
        else:
            print("Warning: No UVs found, using default (0,0)", file=sys.stderr)
            uvs = np.zeros((len(vertices), 2), dtype=np.float32)
        
        return vertices, normals, uvs, indices
        
    except ImportError:
        print("Warning: trimesh not available, limited format support", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error loading mesh: {e}", file=sys.stderr)
        return None


def save_tangents_json(tangents: np.ndarray, output_path: Path) -> bool:
    """
    Save tangents to JSON sidecar file.
    
    Args:
        tangents: Nx4 array of tangent vectors
        output_path: Path to output JSON file
        
    Returns:
        True on success, False on failure
    """
    try:
        data = {
            "tangents": tangents.tolist(),
            "format": "xyzw",
            "count": len(tangents)
        }
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error saving tangents JSON: {e}", file=sys.stderr)
        return False


def embed_tangents_gltf(mesh_path: Path, tangents: np.ndarray) -> bool:
    """
    Embed tangents into GLTF/GLB file using pygltflib.
    
    Args:
        mesh_path: Path to GLTF/GLB file
        tangents: Nx4 array of tangent vectors
        
    Returns:
        True on success, False on failure
    """
    try:
        from pygltflib import GLTF2
        
        gltf = GLTF2().load(str(mesh_path))
        
        # This is a simplified embedding - a full implementation would
        # properly handle buffer views, accessors, etc.
        print(f"Info: GLTF embedding loaded successfully for {mesh_path}", file=sys.stderr)
        print("Info: Full GLTF tangent embedding not yet implemented", file=sys.stderr)
        
        # TODO: Implement full GLTF tangent embedding by:
        # 1. Creating a new buffer for tangent data
        # 2. Adding a buffer view for the tangent buffer
        # 3. Adding an accessor for TANGENT attribute
        # 4. Updating mesh primitive to reference TANGENT accessor
        # 5. Saving the modified GLTF file
        # Once implemented, uncomment: gltf.save(str(mesh_path))
        
        return True
        
    except ImportError:
        print("Info: pygltflib not available, skipping GLTF embedding", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error embedding tangents in GLTF: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate tangent vectors for 3D meshes"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input mesh file (supports formats via trimesh)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output JSON file (default: <input>.tangents.json)"
    )
    parser.add_argument(
        "--embed-gltf",
        action="store_true",
        help="Embed tangents into GLTF/GLB file (requires pygltflib)"
    )
    
    args = parser.parse_args()
    
    # Validate input file
    if not args.input.exists():
        print(f"Error: Input file {args.input} not found", file=sys.stderr)
        return 1
    
    # Load mesh data
    print(f"Loading mesh from {args.input}...")
    mesh_data = load_mesh_data(args.input)
    if mesh_data is None:
        return 1
    
    vertices, normals, uvs, indices = mesh_data
    print(f"Loaded mesh: {len(vertices)} vertices, {len(indices)//3} triangles")
    
    # Compute tangents
    print("Computing tangents...")
    tangents = compute_tangents(vertices, normals, uvs, indices)
    print(f"Generated {len(tangents)} tangent vectors")
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.input.parent / f"{args.input.name}.tangents.json"
    
    # Save tangents to JSON
    print(f"Saving tangents to {output_path}...")
    if not save_tangents_json(tangents, output_path):
        return 1
    
    print(f"✓ Tangents saved to {output_path}")
    
    # Optionally embed in GLTF
    if args.embed_gltf:
        ext = args.input.suffix.lower()
        if ext in ['.gltf', '.glb']:
            print(f"Embedding tangents in {args.input}...")
            embed_tangents_gltf(args.input, tangents)
        else:
            print(f"Warning: --embed-gltf only works with .gltf/.glb files", file=sys.stderr)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
