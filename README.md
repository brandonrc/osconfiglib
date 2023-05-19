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
from osconfiglib.layers import squash_layers, export_squashed_layer
from osconfiglib.virt_customize import apply_squashed_layer

# Use osconfiglib to squash layers
squashed_layer = squash_layers(base_image_path, os_recipe_toml_path)

# Export the squashed layer
export_squashed_layer(squashed_layer, output_image_path)

# Apply the squashed layer to a base image
apply_squashed_layer(base_image_path, squashed_layer, output_image_path, python_version="python3")
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



## TOML File Usage

You can define your layers in a TOML file for easy import, squash, and application. Here's an example of a TOML file:

```toml
name = "Ubuntu-Python-Dev"
version = "1.0.0"

[layers]
[[layers]]
type = "git"
url = "https://github.com/user/os-ubuntu.git"
branch_or_tag = "main"

[[layers]]
type = "git"
url = "https://github.com/user/os-python.git"
branch_or_tag = "main"

[[layers]]
type = "local"
path = "/path/to/your/local/os-custom-configs"
```

This TOML file defines three layers. The `os-ubuntu` and `os-python` layers are git layers. The `os-custom-configs` layer is a local layer, stored in your filesystem.

To use these layers:

1. Import the layers using the `import_layers` function:

   ```python
   import_layers('path/to/your/layers.toml')
   ```

   This function will import all the layers defined in your TOML file into your local cache. For git layers, the repositories will be cloned. For local layers, they are already in your filesystem, so they won't be imported.

2. Squash the layers using the `squash_layers` function:

   ```python
   squashed_layer = squash_layers(layers)
   ```

   This function will combine all the layers into a single squashed layer.

3. You can either export the squashed layer into a tarball using the `export_squashed_layer` function:

   ```python
   export_squashed_layer(squashed_layer, 'path/to/your/output.tar.gz')
   ```

   Or apply the squashed layer to a base image using the `apply_squashed_layer` function:

   ```python
   apply_squashed_layer('path/to/your/base.qcow2', squashed_layer, 'path/to/your/output.qcow2')
   ```

4. If you want to export or apply layers based on a TOML file directly, you can use the `toml_export` or `toml_apply` functions:

   ```python
   toml_export('path/to/your/layers.toml', 'path/to/your/output.tar.gz')
   ```

   ```python
   toml_apply('path/to/your/layers.toml', 'path/to/your/base.qcow2', 'path/to/your/output.qcow2')
   ```

   The `toml_export` function will export a squashed layer based on the layers defined in the TOML file. The `toml_apply` function will apply a squashed layer based on the layers defined in the TOML file to a base image.



## Developing

To run the test suite, install the dev dependencies and run pytest:

```bash
$ pip install -r dev-requirements.txt
$ pytest
```

## Contact

If you have any issues or questions, feel free to

 contact me at brandon.geraci@gmail.com.
