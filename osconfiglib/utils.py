# File: osconfiglib/utils.py

import os
import shutil
import platform

def check_package_availability(package_name):
    """
    Check if a package is available in the system.

    Args:
        package_name (str): Name of the package to check.

    Returns:
        bool: True if the package is available, False otherwise.
    """
    # Check the platform to determine the package manager
    if platform.system() in ['Linux']:
        # Check for RHEL/CentOS/Fedora
        if os.path.exists('/etc/redhat-release'):
            cmd = ['rpm', '-q', package_name]
        # Check for Ubuntu/Debian
        elif os.path.exists('/etc/debian_version'):
            cmd = ['dpkg', '-l', package_name]
        else:
            # Unsupported Linux distribution
            raise NotImplementedError("Unsupported Linux distribution.")
        
        # Run the command to check package availability
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            return False
    else:
        raise NotImplementedError("Unsupported operating system.")

def check_and_install_package(package_name):
    """
    Check if a package is available and install it if necessary.

    Args:
        package_name (str): Name of the package to check and install.
    """
    if not check_package_availability(package_name):
        raise RuntimeError(f"The package '{package_name}' is not available on this system.")

    # If the package is available, no further action is needed


def check_dependencies():
    """
    Check for necessary dependencies in the system's PATH. If a required dependency is missing, a warning message is printed.
    The necessary dependencies are 'virt-customize' and 'git'.
    """
    # List of dependencies that the application requires
    dependencies = ['virt-customize', 'git']
    
    # Check if each dependency can be found in the system's PATH
    missing_dependencies = [
        dependency
        for dependency in dependencies
        if shutil.which(dependency) is None  # `shutil.which` returns None if the dependency isn't found
    ]
    
    # If there are any missing dependencies, print a warning message
    if missing_dependencies:
        print("Warning: The following dependencies are missing:")
        for dependency in missing_dependencies:
            print(f"- {dependency}")
        print("Please install the missing dependencies before running this application.")
        

def check_qcow2_file(value):
    """
    Check if the given value is a valid path to a .qcow2 file.

    Args:
        value (str): Path to the file to be checked

    Returns:
        str: The given value if it's valid

    Raises:
        ValueError: If the file does not exist or if it's not a .qcow2 file
    """
    # Check if the file exists
    if not os.path.isfile(value):
        raise ValueError(f"{value} does not exist")
    
    # Check if the file is a .qcow2 file
    if not value.endswith('.qcow2'):
        raise ValueError(f"{value} is not a .qcow2 file")
    
    # If no errors are raised, the value is valid
    return value
