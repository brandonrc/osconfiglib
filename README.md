[![Lint](https://github.com/brandonrc/osconfiglib/actions/workflows/lint.yml/badge.svg)](https://github.com/brandonrc/osconfiglib/actions/workflows/lint.yml)

# osconfiglib

osconfiglib is a Python library designed to ease the process of layer-based configuration for virtual machines (QCOW2). The library provides utilities to manage layers, apply configurations, and includes a CLI tool for easy management.

## Installation

To install osconfiglib, add the following to the dependencies section of your project's `pyproject.toml`:

```toml
osconfiglib = "^1.0.0"
```

Then run:

```bash
$ pip install -r requirements.txt
```

## Usage

Here's a basic example of how you can use osconfiglib:

```python
from osconfiglib.layers import apply_layers

# Use osconfiglib to apply layers to a base image
apply_layers(base_image_path, os_recipe_toml_path, output_image_path, python_version)
```

### CLI Usage

osconfiglib also includes a CLI tool to manage your layers. Here are some examples of how to use it:

```bash
# List all layers
$ osconfiglib-cli list layers

# Check version
$ osconfiglib-cli --version

# Add RPM to a layer
$ osconfiglib-cli add rpm mylayer tmux

# Add a file to a layer
$ osconfiglib-cli add file mylayer ~/.tmux.conf /home/user

# Create a new layer
$ osconfiglib-cli create layer newLayer

# Delete a layer
$ osconfiglib-cli delete layer <layer>
```

## Repository Structure

When using osconfiglib to manage layers, your repository should follow this structure:

```
my-build/
├── configs/
│   ├── bin/
│   │   └── custom-executable
│   ├── etc/
│   │   └── custom-executable.conf
│   └── usr/local/bin
│       └── symlink-to-something
├── package-lists/
│   ├── rpm-requirements.txt
│   ├── dpm-requirements.txt
│   └── pip-requirements.txt
└── scripts/
    ├── 01-first-script-to-run.sh
    └── 02-second-script-to-run.sh
```

- `configs/`: This directory is where you put custom config files that go in the root filesystem. Examples can include custom dns, dhcpd, tftp, and other services required for this "layer".
- `package-lists/`: This directory contains lists for RedHat and Debian packages based on the flavor of Linux. A separate file is included for pip requirements for the system Python.
- `scripts/`: Scripts are run in alphabetical order. If you number them you can control the order of the scripts.

You can refer to this [os-layer-template](https://github.com/brandonrc/os-layer-template) for a complete template of the repository structure.


## Developing

To run the test suite, install the dev dependencies and run pytest:

```bash
$ pip install -r dev-requirements.txt
$ pytest
```

## Contact

If you have any issues or questions, feel free to contact me at brandon.geraci@gmail.com.
