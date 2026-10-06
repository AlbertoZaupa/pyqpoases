# A Python interface for qpOASES

This repository includes a `pybind11`-based Python extension for [qpOASES](https://github.com/coin-or/qpOASES) in `qpoases.py/`.

## Installation

1. From this top-level repository directory (the one containing `Makefile`), build qpOASES:

```bash
make src
```

2. Create and activate a Python virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install Python dependencies:

```bash
python -m pip install -r qpoases.py/requirements.txt
```

4. From the top-level repository directory, build the Python extension:

```bash
python qpoases.py/setup.py build_ext
export PYTHONPATH="$PWD/bin:$PYTHONPATH"
```

The extension is placed in `bin/`, alongside `libqpOASES.so`. This makes it
available to Python through `PYTHONPATH`; it does not install it into the virtual
environment. Repeat the `export` command from the repository root in each new shell.

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
