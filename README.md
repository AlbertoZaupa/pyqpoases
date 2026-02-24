# Python Usage (`pyqpoases`)

This repository includes a `pybind11`-based Python extension for qpOASES in `qpoases.py/`.

## Installation

1. From this top-level repository directory (the one containing `Makefile`), build qpOASES:

```bash
make src
```

2. Create and activate a Python virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
pip install -r qpoases.py/requirements.txt
```

4. Build and install the Python extension:

```bash
cd qpoases.py
python setup.py build_ext --install
```

## Running Examples

From `qpoases.py`, run any example script with:

```bash
python example_name.py
```

For example:

```bash
cd qpoases.py
python quadruped.py
```

## Notes

- During compilation you may see many compiler warnings. This is expected for this build and is usually not an error.
- If you rebuild frequently, ensure your virtual environment is active before reinstalling dependencies or rerunning `setup.py`.
