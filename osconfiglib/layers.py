# File: osconfiglib/layers.py

import os
import subprocess
import tarfile
import tempfile
import urllib.parse
import toml
from pathlib import Path

from shutil import copy2
import shutil
from pathlib import Path
from urllib.parse import urlparse
import re


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

    layer_dir = Path.home() / ".cache" / "osconfiglib" / layer_name / "configs"

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
    layer_dir = Path.home() / ".cache" / "osconfiglib" / layer_name

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
    layer_dir = Path.home() / ".cache" / "osconfiglib" / layer_name

    # Check if the layer already exists
    if layer_dir.exists():
        print(f"A layer named {layer_name} already exists.")
        return False

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
    return True

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
    cache_dir = home_dir / ".cache" / "osconfiglib"  # Cache directory

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

def validate_git_url(url):
    # regex for matching SSH URLs
    ssh_pattern = re.compile(r"^(git@|ssh:\/\/git@)([\w\.@:\/~-]|(%[0-9a-fA-F]{2}))*$")

    # first, check if the URL is an HTTP(S) URL
    try:
        result = urlparse(url)
        if all([result.scheme in ['http', 'https'], result.netloc, result.path]):
            return True
    except ValueError:
        pass

    # if it's not an HTTP(S) URL, check if it's an SSH URL
    if ssh_pattern.match(url):
        return True

    # if neither check passed, the URL is invalid
    return False

def validate_layer_structure(layer_path):
    """
    Validate the structure of a layer directory.

    Args:
        layer_path (str): Path to the layer directory

    Returns:
        bool: True if the layer structure is valid, False otherwise
    """
    expected_dirs = ['configs', 'package-lists', 'scripts']
    expected_files = {
        'package-lists': ['dpm-requirments.txt', 'pip-requirments.txt', 'rpm-requirments.txt'],
    }

    # Check if the required directories exist
    for dir_name in expected_dirs:
        if not os.path.isdir(os.path.join(layer_path, dir_name)):
            print(f"Directory '{dir_name}' is missing in the layer")
            return False

    # Check if the required files exist
    for dir_name, file_names in expected_files.items():
        for file_name in file_names:
            if not os.path.isfile(os.path.join(layer_path, dir_name, file_name)):
                print(f"File '{file_name}' is missing in the '{dir_name}' directory of the layer")
                return False

    return True

def delete_layer_if_invalid(layer_path):
    """
    Delete the layer directory if its structure is invalid.

    Args:
        layer_path (str): Path to the layer directory
    """
    if not validate_layer_structure(layer_path):
        print(f"Deleting invalid layer: {layer_path}")
        shutil.rmtree(layer_path)
        return True
    # Returns false if we did not delete the layer. 
    return False

def import_layer(repo_url, branch='main'):
    """
    Import a layer from a git repository. The layer will be stored in a local
    cache directory (~/.cache/osconfiglib/). Each repository and branch combination
    will be stored in a separate directory.

    Args:
        name: The name of the layer.
        repo_url: The URL of the git repository.
        branch: The branch of the repository to import. Default is 'main'.

    Returns:
        None
    """
    # Checking to see if the URL is valid
    if not validate_git_url(repo_url):
        print(f"Url '{repo_url}' is not valid")
        return False
    
    parsed_url = urllib.parse.urlparse(repo_url)
    
    # Extract the host
    host = parsed_url.netloc

    # Extract the owner and repository name
    path_parts = parsed_url.path.strip('/').split('/')
    owner = '-'.join(path_parts[:-1])  # Combine all groups into one string
    repo_name = path_parts[-1].replace('.git', '')  # The repository name is the last part
    cache_dir = os.path.expanduser(f"~/.cache/osconfiglib/{host}-{owner}-{repo_name}-{branch}")
    print(cache_dir)
    if os.path.exists(cache_dir):
        print(f"Layer '{repo_name}' from '{owner}' on branch '{branch}' is already imported.")
        return False

    print(f"Cloning repository '{repo_url}' branch '{branch}' into '{cache_dir}'...")
    result = subprocess.run(['git', 'clone', '--branch', branch, repo_url, cache_dir], check=False)
    if result.returncode != 0:
        print(f"Branch '{branch}' not found, trying with 'master' branch...")
        branch = 'master'
        cache_dir = os.path.expanduser(f"~/.cache/osconfiglib/{host}-{owner}-{repo_name}-{branch}")
        if os.path.exists(cache_dir):
            print(f"Layer '{repo_name}' from '{owner}' on branch '{branch}' is already imported.")
            return True
        subprocess.run(['git', 'clone', '--branch', branch, repo_url, cache_dir], check=True)
    if delete_layer_if_invalid(cache_dir):
        print(f"Deleting the folder '{cache_dir}' because it was not valid Need to follow the layer file structure")
        print("I need to find that URL and put it here...")
        return False
    print(f"Layer '{repo_name}' from '{owner}' on branch '{branch}' imported successfully.")
    return True


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
    cache_dir = home_dir / ".cache" / "osconfiglib"  # Cache directory

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
                    parsed_url = urlparse(layer['url'])
                    host = parsed_url.netloc
                    user_repo = parsed_url.path.lstrip('/')
                    branch = layer['branch_or_tag']
                    local_layer_path = os.path.join(cache_dir, f"{host}-{user_repo}-{branch}")
                    if not os.path.exists(local_layer_path):
                        subprocess.run(['git', 'clone', '--branch', branch, layer['url'], local_layer_path])
                    else:
                        print(f"Layer '{user_repo}' from branch '{branch}' is already imported.")
                    layer_path = local_layer_path

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
