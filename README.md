# Configlib

Configlib is a Python library designed to ease the process of layer-based configuration for virtual machines. The library provides utilities to list, import, and apply configurations based on a recipe file. It is designed to work with a specific repository structure that includes configurations, package lists, and scripts.

## Installation

To install Configlib, add the following to the dependencies section of your project's `pyproject.toml`:

```toml
configlib = "^1.0.0"
```

Then run:

```bash
$ pip install -r requirements.txt
```

## Usage

Here's a basic example of how you can use Configlib:

```python
from configlib.utils import apply_layers

# Use Configlib to apply layers to a base image
apply_layers(base_image_path, os_recipe_toml_path, output_image_path, python_version)
```

## Repository Structure

When using Configlib to manage layers, your repository should follow this structure:

```
my-packer-build/
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

## Contact

If you have any issues or questions, feel free to contact me at brandon.geraci@gmail.com.