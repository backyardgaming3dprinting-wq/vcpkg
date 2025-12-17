# Development Environment Setup

This document describes how to set up a development environment for working on this project.

## Prerequisites

- Python 3.8 or later
- CMake 3.15 or later (for C++ components)
- A C++17 compatible compiler (GCC 7+, Clang 5+, MSVC 2017+)

## Python Development Setup

### Linux/macOS

1. Clone the repository:
```bash
git clone https://github.com/backyardgaming3dprinting-wq/vcpkg.git
cd vcpkg
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

### Windows

1. Clone the repository:
```powershell
git clone https://github.com/backyardgaming3dprinting-wq/vcpkg.git
cd vcpkg
```

2. Run the bootstrap script:
```powershell
.\scripts\bootstrap-dev.ps1
```

This will create a virtual environment and install all development dependencies.

## Running Tests

### Python Tests

Run all Python tests:
```bash
pytest tests/
```

Run tests with coverage:
```bash
pytest --cov=tools --cov-report=html tests/
```

Run specific test file:
```bash
pytest tests/test_tangents.py
```

### C++ Tests

Build and run C++ tests:

```bash
cd app
mkdir build
cd build
cmake ..
cmake --build .
ctest
```

Or on Windows:
```powershell
cd app
mkdir build
cd build
cmake ..
cmake --build . --config Release
ctest -C Release
```

## Development Tools

### Code Formatting

Python code formatting with Black:
```bash
black tools/ tests/
```

### Linting

Python linting with flake8:
```bash
flake8 tools/ tests/
```

### Type Checking

Python type checking with mypy:
```bash
mypy tools/ tests/
```

## Project Structure

```
.
├── app/                    # C++ application code
│   └── src/
│       └── mesh_core/      # Mesh processing core
├── tools/                  # Python tools and utilities
│   ├── plugins/            # Plugin modules
│   ├── generate_tangents.py
│   └── schema_validate.py
├── tests/                  # Python tests
├── scripts/                # Build and setup scripts
├── docs/                   # Documentation
└── requirements-dev.txt    # Python development dependencies
```

## Continuous Integration

GitHub Actions workflows are configured to run tests automatically:

- `.github/workflows/dev-python-tests.yml` - Python tests on all PRs
- `.github/workflows/cpp-ci.yml` - C++ build and tests

## Optional Dependencies

Some features require optional dependencies:

- **trimesh**: For loading various 3D mesh formats
- **pygltflib**: For embedding tangents into GLTF/GLB files
- **jsonschema**: For strict schema validation

These are included in `requirements-dev.txt` but the code will gracefully degrade if they're not available.

## Troubleshooting

### Python Import Errors

If you see import errors, make sure your virtual environment is activated and dependencies are installed:

```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements-dev.txt
```

### C++ Build Errors

Make sure you have CMake and a compatible C++ compiler installed:

```bash
cmake --version
gcc --version  # or clang --version, or cl.exe on Windows
```

### Test Failures

Some tests may be skipped if optional dependencies are not available. This is expected behavior. To run all tests, install all optional dependencies from `requirements-dev.txt`.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on contributing to this project.
