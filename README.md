# ConfigLib

## Overview

ConfigLib is a Python library designed by Brandon Geraci to handle configuration and layering tasks for image files, specifically .qcow2 files. It provides a streamlined and simplified interface for operations such as applying layers, importing layers from Git repositories, listing available layers, and checking for necessary dependencies.

## Installation

The recommended way to install ConfigLib is via pip:

```shell
pip install configlib
```

Or, if you're using Poetry for dependency management:

```shell
poetry add configlib
```

## Usage

Here's a quick overview of how you can use ConfigLib in your own projects:

```python
from configlib import apply_layers, import_layer, list_layers, check_dependencies

# Check for required dependencies
check_dependencies()

# Import a layer from a Git repository
import_layer('https://github.com/username/repo.git')

# List available layers
list_layers()

# Apply layers from a .toml recipe to a base image
apply_layers('path/to/base_image.qcow2', 'path/to/recipe.toml', 'path/to/output_image.qcow2', 'python3')
```

Please note that you may need to adjust file paths and URLs to fit your own use case.

## Contributing

Contributions to ConfigLib are very welcome! Please submit issues and pull requests on our GitHub page.

## License

ConfigLib is released under the MIT License. Please see the `LICENSE` file for more details.

## Contact

For any questions or feedback, please contact Brandon Geraci at [brandon.geraci@gmail.com](mailto:brandon.geraci@gmail.com).