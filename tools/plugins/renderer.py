#!/usr/bin/env python3
"""
Renderer Plugin

Executes external renderer commands with proper working directory handling
for deterministic retry behavior.
"""

import subprocess
import sys
from pathlib import Path
from typing import List, Optional


class RendererPlugin:
    """Plugin for running external rendering commands."""
    
    def __init__(self, renderer_cmd: str, working_dir: Optional[Path] = None):
        """
        Initialize the renderer plugin.
        
        Args:
            renderer_cmd: Command to execute the renderer
            working_dir: Working directory for the renderer (default: current dir)
        """
        self.renderer_cmd = renderer_cmd
        self.working_dir = working_dir or Path.cwd()
    
    def render(self, input_file: Path, output_file: Path, 
               extra_args: Optional[List[str]] = None) -> bool:
        """
        Run the renderer on an input file.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            extra_args: Additional command-line arguments
            
        Returns:
            True if rendering succeeded, False otherwise
        """
        cmd = [self.renderer_cmd, str(input_file), str(output_file)]
        if extra_args:
            cmd.extend(extra_args)
        
        try:
            # Run with cwd set for deterministic retry behavior
            result = subprocess.run(
                cmd,
                cwd=self.working_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"Renderer failed with exit code {result.returncode}", 
                      file=sys.stderr)
                if result.stderr:
                    print(f"Error output: {result.stderr}", file=sys.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print("Renderer timed out after 5 minutes", file=sys.stderr)
            return False
        except FileNotFoundError:
            print(f"Renderer command not found: {self.renderer_cmd}", 
                  file=sys.stderr)
            return False
        except Exception as e:
            print(f"Error running renderer: {e}", file=sys.stderr)
            return False
    
    def render_with_retry(self, input_file: Path, output_file: Path,
                         max_retries: int = 3,
                         extra_args: Optional[List[str]] = None) -> bool:
        """
        Run the renderer with retry logic.
        
        Args:
            input_file: Path to input file
            output_file: Path to output file
            max_retries: Maximum number of retry attempts
            extra_args: Additional command-line arguments
            
        Returns:
            True if rendering succeeded, False otherwise
        """
        for attempt in range(max_retries):
            if attempt > 0:
                print(f"Retry attempt {attempt + 1}/{max_retries}...", 
                      file=sys.stderr)
            
            if self.render(input_file, output_file, extra_args):
                return True
        
        print(f"Rendering failed after {max_retries} attempts", file=sys.stderr)
        return False


def main():
    """CLI interface for the renderer plugin."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Run external renderer with deterministic working directory"
    )
    parser.add_argument("renderer", help="Renderer command")
    parser.add_argument("input", type=Path, help="Input file")
    parser.add_argument("output", type=Path, help="Output file")
    parser.add_argument(
        "--cwd", type=Path, 
        help="Working directory (default: current directory)"
    )
    parser.add_argument(
        "--retry", type=int, default=1,
        help="Number of retry attempts (default: 1)"
    )
    parser.add_argument(
        "extra_args", nargs="*",
        help="Additional arguments to pass to renderer"
    )
    
    args = parser.parse_args()
    
    plugin = RendererPlugin(args.renderer, args.cwd)
    
    if args.retry > 1:
        success = plugin.render_with_retry(
            args.input, args.output, args.retry, args.extra_args
        )
    else:
        success = plugin.render(args.input, args.output, args.extra_args)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
