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


def squash_layers(layers):
    """
    Combine multiple layers into a single layer (squashed layer).

    Args:
        layers (list): List of layers
    """
    squashed_layer = {
        'rpm_requirements': [],
        'deb_requirements': [],
        'pip_requirements': [],
        'configs': [],
        'squash_script': "#!/bin/bash\n\n"
                          "trap 'echo \"Error occurred in ${FUNCNAME[1]}\"; exit 1' ERR\n"
    }

    # Iterate over layers and squash configurations
    for layer in layers:
        # Append requirements to the lists
        squashed_layer['rpm_requirements'] += get_requirements_files(layer_path, 'rpm-requirements.txt')
        squashed_layer['deb_requirements'] += get_requirements_files(layer_path, 'dpm-requirements.txt')
        squashed_layer['pip_requirements'] += get_requirements_files(layer_path, 'pip-requirements.txt')

        # Combine configs into the squashed layer
        config_dir = os.path.join(layer_path, 'configs')
        if os.path.exists(config_dir):
            squashed_layer['configs'].append(config_dir)

        # Combine scripts into the squashed layer
        script_dir = os.path.join(layer_path, 'scripts')
        if os.path.exists(script_dir):
            for script in os.listdir(script_dir):
                with open(os.path.join(script_dir, script), 'r') as file:
                    # Strip comments and add layer/script info
                    stripped_script = "\n".join(line for line in file if not line.startswith("#"))
                    squashed_layer['squash_script'] += f"\n# {layer['name']} {script}\n"
                    squashed_layer['squash_script'] += f"function {layer['name']}_{script.replace('.', '_')}() {{\n"
                    squashed_layer['squash_script'] += stripped_script + "\n}\n"
                    squashed_layer['squash_script'] += f"{layer['name']}_{script.replace('.', '_')}\n"

    return squashed_layer

def export_squashed_layer(squashed_layer, output_file):
    """
    Export the squashed layer into a tarball.

    Args:
        squashed_layer (dict): Squashed layer of configurations
        output_file (str): Path to the output tarball file
    """
    with tarfile.open(output_file, "w:gz") as tar:
        # Add configs to the tarball
        for config in squashed_layer['configs']:
            tar.add(config, arcname=os.path.basename(config))

        # Add requirements to the tarball
        for requirements in ['rpm_requirements', 'deb_requirements', 'pip_requirements']:
            with tempfile.NamedTemporaryFile(suffix=".txt") as temp_requirements:
                with open(temp_requirements.name, 'w') as file:
                    file.write("\n".join(squashed_layer[requirements]))
                tar.add(temp_requirements.name, arcname=f"{requirements}.txt")

        # Add the squashed script to the tarball
        with tempfile.NamedTemporaryFile(suffix=".sh") as temp_script:
            with open(temp_script.name, 'w') as file:
                file.write(squashed_layer['squash_script'])
            tar.add(temp_script.name, arcname="squash_script.sh")

