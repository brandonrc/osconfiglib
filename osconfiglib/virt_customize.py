# virt_customize.py

import os
import subprocess
import tempfile
import tarfile
from osconfiglib import layers
import toml

def apply_squashed_layer(base_image, squashed_layer, output_image, python_version="python3"):
    """
    Apply squashed layers of configurations to a base image using virt-customize.

    Args:
        base_image (str): Path to the base image file
        squashed_layer (dict): Dictionary containing squashed layers
        output_image (str): Path to the output image file
        python_version (str): Python version used for virtual environment. If none then python3 is used
    """
    # Use a temporary file for the tarball
    with tempfile.NamedTemporaryFile(suffix=".tar.gz") as temp_file:
        with tarfile.open(temp_file.name, "w:gz") as tar:
            # Add configs to the tarball
            for config in squashed_layer['configs']:
                tar.add(config)

        # Upload the tarball and extract it in the base image
        subprocess.run(['virt-customize', '-a', base_image, '--upload', f'{temp_file.name}:/'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'tar xzf /{os.path.basename(temp_file.name)} -C /'])

    # Write the squashed script into the base image
    with tempfile.NamedTemporaryFile(suffix=".sh") as temp_script:
        with open(temp_script.name, 'w') as file:
            file.write(squashed_layer['squash_script'])
        subprocess.run(['virt-customize', '-a', base_image, '--upload', f'{temp_script.name}:/opt/squashed_script.sh'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', 'chmod +x /opt/squashed_script.sh'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', '/opt/squashed_script.sh'])

    # Install rpm and deb packages, and pip requirements in the base image
    if squashed_layer['rpm_requirements']:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'dnf install -y --nogpgcheck --allowerasing{" ".join(squashed_layer["rpm_requirements"])}'])
    if squashed_layer['deb_requirements']:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'apt-get install -y {" ".join(squashed_layer["deb_requirements"])}'])
    if squashed_layer['pip_requirements']:
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'{python_version} -m venv /opt/os-python-venv'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', f'source /opt/os-python-venv/bin/activate && pip install {" ".join(squashed_layer["pip_requirements"])}'])
        subprocess.run(['virt-customize', '-a', base_image, '--run-command', 'chmod -R 777 /opt/os-python-venv'])

    # Copy the base image to the output image
    subprocess.run(['cp', base_image, output_image])


def toml_apply(toml_file_path, base_image, output_image, python_version="python3"):
    """
    Applies layers specified in a TOML file to a base image.

    Args:
        toml_file_path (str): Path to the TOML file.
        base_image (str): Path to the base image file.
        output_image (str): Path to the output image file.
        python_version (str): Python version used for virtual environment. If none then python3 is used.
    """

    # Load and parse the TOML file
    with open(toml_file_path, 'r') as file:
        data = toml.load(file)

    # Iterate over the layers in the TOML file and squash them
    squashed_layers = layers.squash_layers(data['layers'])

    # Apply the squashed layer
    apply_squashed_layer(base_image, squashed_layers, output_image, python_version)
    print("Layers applied successfully.")