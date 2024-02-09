# virt_customize.py

import os
import subprocess
import tempfile
import tarfile
import platform
import shutil
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
    # Use a temporary directory for storing temporary files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a tarball containing the configs
        tarball_path = os.path.join(temp_dir, "squashed_layer.tar.gz")
        with tarfile.open(tarball_path, "w:gz") as tar:
            for config in squashed_layer['configs']:
                tar.add(config, arcname=os.path.basename(config))

        # Write the squashed script into a temporary file
        script_path = os.path.join(temp_dir, "squashed_script.sh")
        with open(script_path, 'w') as script_file:
            script_file.write(squashed_layer['squash_script'])

        shutil.copyfile(base_image, output_image)

        # Construct the virt-customize command
        command = [
            'virt-customize', '-a', output_image,
            '--upload', f'{tarball_path}:/squashed_layer.tar.gz',
            '--run-command', f'tar xzf /squashed_layer.tar.gz -C /',
            '--upload', f'{script_path}:/opt/squashed_script.sh',
            '--run-command', 'chmod +x /opt/squashed_script.sh',
            '--run-command', '/opt/squashed_script.sh'
        ]

        if squashed_layer['rpm_requirements']:
            command.append('--run-command')
            command.append('bash -c "if [ -f /etc/redhat-release ]; then dnf install -y --nogpgcheck --allowerasing ' + ' '.join(squashed_layer["rpm_requirements"]) + '; fi"')
        elif squashed_layer['deb_requirements']:
            command.append('--run-command')
            command.append('bash -c "if [ -f /etc/debian_version ]; then apt-get install -y ' + ' '.join(squashed_layer["deb_requirements"]) + '; fi"')

        # Install pip requirements in the copied image
        if squashed_layer['pip_requirements']:
            command.append('--run-command')
            command.append(f'{python_version} -m venv /opt/os-python-venv && source /opt/os-python-venv/bin/activate && pip install {" ".join(squashed_layer["pip_requirements"])}')
            command.append('--run-command')
            command.append('chmod -R 777 /opt/os-python-venv')

        # Run the virt-customize command
        subprocess.run(command)

    print("Layers applied successfully.")


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