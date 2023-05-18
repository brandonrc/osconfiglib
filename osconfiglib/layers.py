# File: osconfiglib/layers.py

import os
import subprocess
import tarfile
import tempfile
import urllib.parse
import toml
from pathlib import Path

from shutil import copy2
from pathlib import Path

def add_file_to_layer(layer_name, source_file_path, destination_path):
    """
    Add a file to the specified layer.

    Args:
        layer_name (str): Name of the layer to which the file should be added.
        source_file_path (str): The path to the file on the local file system that should be added to the layer.
        destination_path (str): The destination path in the layer's config directory where the file should be placed.
    """

    # Convert the paths to Path objects to handle file paths more easily
    source_file_path = Path(source_file_path)
    destination_path = Path(destination_path)

    # Verify that the source file exists
    if not source_file_path.exists():
        print(f"The file {source_file_path} does not exist.")
        return

    # Verify that the source file is a file
    if not source_file_path.is_file():
        print(f"{source_file_path} is not a file.")
        return

    layer_dir = Path.home() / ".cache" / "myapp" / layer_name / "configs"

    # Check if the layer exists
    if not layer_dir.exists():
        print(f"A layer named {layer_name} does not exist.")
        return

    # Create the destination directory in the layer's config directory, if it doesn't exist
    (layer_dir / destination_path).mkdir(parents=True, exist_ok=True)

    # Copy the source file to the destination directory in the layer's config directory
    copy2(source_file_path, layer_dir / destination_path / source_file_path.name)

    print(f"File {source_file_path.name} added to layer {layer_name} successfully.")


def add_package_to_layer(layer_name, package_type, package_name):
    """
    Add a new package to the specified layer.

    Args:
        layer_name (str): Name of the layer to edit
        package_type (str): Type of the package ("rpm", "dpm", or "pip")
        package_name (str): Name of the package to add
    """
    layer_dir = Path.home() / ".cache" / "myapp" / layer_name

    # Check if the layer exists
    if not layer_dir.exists():
        print(f"A layer named {layer_name} does not exist.")
        return

    # Open the package list file and add the new package
    package_list_file = layer_dir / "package-lists" / f"{package_type}-requirements.txt"
    with open(package_list_file, 'a') as file:
        file.write(package_name + '\n')

    print(f"Package {package_name} added to layer {layer_name} successfully.")

def create_layer(layer_name):
    """
    Create a new layer in the local cache with the specified name.

    Args:
        layer_name (str): Name of the layer to create
    """
    layer_dir = Path.home() / ".cache" / "myapp" / layer_name

    # Check if the layer already exists
    if layer_dir.exists():
        print(f"A layer named {layer_name} already exists.")
        return

    # Create the layer directory and the necessary subdirectories
    layer_dir.mkdir(parents=True)
    (layer_dir / "configs").mkdir()
    (layer_dir / "package-lists").mkdir()
    (layer_dir / "scripts").mkdir()

    # Create the package list files
    for package_type in ["rpm", "dpm", "pip"]:
        with open(layer_dir / "package-lists" / f"{package_type}-requirements.txt", 'w') as file:
            pass

    print(f"Layer {layer_name} created successfully.")

def get_requirements_files(layer, file_name):
    """
    Get the content of the requirement file in the given layer.
    
    Args:
        layer (str): Path to the layer directory
        file_name (str): Name of the requirement file

    Returns:
        list: List of requirements
    """
    file_path = os.path.join(layer, 'package-lists', file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return [line.strip() for line in file if line.strip() and not line.startswith('#')]
    return []


def list_layers():
    """
    List all layers stored locally in the 'layers' directory and in the cache directory.
    """
    # Define the path of directories
    home_dir = Path.home()  # User's home directory
    cache_dir = home_dir / ".cache" / "myapp"  # Cache directory

    # Header for the output
    print(f"{'Layer Name':<20} {'Source':<20}")

    # List layers in the 'layers' directory
    layers_dir = Path('layers')
    if layers_dir.exists():
        for item in layers_dir.iterdir():
            if item.is_dir():
                print(f'{item.name:<20} {"Configurator":<20}')

    # List layers in the cache directory
    if cache_dir.exists():
        for item in cache_dir.iterdir():
            if item.is_dir():
                # Get the origin URL of the git repository
                git_url = subprocess.getoutput(f'git -C {item} config --get remote.origin.url')
                print(f'{item.name:<20} {git_url:<20}')


def import_layer(git_url):
    """
    Clone a git repository and store it in the cache directory.

    Args:
        git_url (str): URL of the git repository to clone
    """
    # Parse the name of the repository from the URL
    layer_name = urllib.parse.urlparse(git_url).path.strip('/').split('/')[-1]

    # Define the path of directories
    home_dir = Path.home()  # User's home directory
    cache_dir = home_dir / ".cache" / "myapp"  # Cache directory

    # Create the cache directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Define the local path where the repository should be cloned
    local_layer_path = cache_dir / layer_name

    # Clone the repository or pull the latest changes if it's already cloned
    if not local_layer_path.exists():
        subprocess.run(['git', 'clone', git_url, local_layer_path])
    else:
        subprocess.run(['git', '-C', local_layer_path, 'pull'])


def apply_layers(base_image, os_recipe_toml, output_image, python_version):
    """
    Apply layers of configurations to a base image.

    Args:
        base_image (str): Path to the base image file
        os_recipe_toml (str): Path to the TOML recipe file
        output_image (str): Path to the output image file
        python_version (str): Python version used for virtual environment
    """
    # Load the recipe from the TOML file
    with open(os_recipe_toml, 'r') as file:
        recipe = toml.load(file)

    # Initialize lists of requirements
    rpm_requirements = []
    deb_requirements = []
    pip_requirements = []

    # Define the path of directories
    home_dir = Path.home()  # User's home directory
    cache_dir = home_dir / ".cache" / "myapp"  # Cache directory

    # Create the cache directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Extract the layers from the recipe
    config_layers = recipe['layers']

    # Use a temporary file for the tarball
    with tempfile.NamedTemporaryFile(suffix=".tar.gz") as temp_file:
        with tarfile.open(temp_file.name, "w:gz") as tar:
            # Iterate over layers and apply configurations
            for layer in config_layers:
                # Handle git layer type
                if layer['type'] == 'git':
                    layer_name = urllib.parse.urlparse(layer['url']).path.strip('/').split('/')[-1]
                    local_layer_path = os.path.join(cache_dir, layer_name)
                    if not os.path.exists(local_layer_path):
                        subprocess.run(['git', 'clone', '-b', layer['branch_or_tag'], layer['url'], local_layer_path])
                    else:
                        subprocess.run(['git', '-C', local_layer_path, 'pull'])
                    layer_path = local_layer_path
                else:  # For local layer type
                    layer_path = os.path.join('layers', layer['name'])

                # Append requirements to the lists
                rpm_requirements += get_requirements_files(layer_path, 'rpm-requirements.txt')
                deb_requirements += get_requirements_files(layer_path, 'dpm-requirements.txt')
                pip_requirements += get_requirements_files(layer_path, 'pip-requirements.txt')

                # Add configs to the tarball
                config_dir = os.path.join(layer_path, 'configs')
                if not os.path.exists(config_dir):
                    print(f"Config directory not found in layer: {layer['name']}")
                    continue
                tar.add(config_dir, arcname=f'{layer["name"]}')

        # Upload the tarball and extract it in the base image
        subprocess.run(['virt-customize', '-a', base_image, '--upload', f'{temp_file.name}:/'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'tar xzf /{os.path.basename(temp_file.name)} -C /'])

    # Install rpm and deb packages, and pip requirements in the base image
    if rpm_requirements:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'dnf install -y {" ".join(rpm_requirements)}'])
    if deb_requirements:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'apt-get install -y {" ".join(deb_requirements)}'])
    if pip_requirements:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'{python_version} -m venv /opt/os-python-venv'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'source /opt/os-python-venv/bin/activate && pip install {" ".join(pip_requirements)}'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', 'chmod -R 777 /opt/os-python-venv'])

    # Copy the base image to the output image
    subprocess.run(['cp', base_image, output_image])
