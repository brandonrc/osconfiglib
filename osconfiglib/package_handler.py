import subprocess
import tempfile
import os

def download_deb_packages(package_list, download_dir):
    """
    Downloads DEB packages and their dependencies.
    
    :param package_list: A list of package names to download.
    :param download_dir: The directory where packages will be downloaded.
    """
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)

    for package in package_list:
        try:
            # Simulate installing the package to capture dependency information
            simulate_cmd = ['apt-get', 'install', '--simulate', package]
            simulate_output = subprocess.check_output(simulate_cmd, universal_newlines=True)

            # Extract package names from the simulation output
            # This step needs refinement to accurately parse package names and versions
            # depending on your specific requirements and the output format
            
            # TODO: add support for apt-get packages. 
            extracted_packages = [] # need to actually implement this.. 
            print(f"We currently do not support apt-get package downloads")

            # For each package/dependency, download it using `apt-get download`
            for pkg in extracted_packages:
                download_cmd = ['apt-get', 'download', pkg, '-o=dir::cache=' + download_dir]
                subprocess.run(download_cmd, check=True, cwd=download_dir)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading package {package}: {e}")


def download_rpm_packages(package_list, download_dir):
    """
    Downloads the specified RPM packages and their dependencies to a given directory.
    
    :param package_list: A list of package names to download.
    :param download_dir: The directory where packages will be downloaded.


    example:
        package_list = ["tmux", "firefox"]
        download_dir = "/tmp/repo"

        package_handler.download_rpm_packages(package_list, download_dir)

    """
    # Ensure the download directory exists
    os.makedirs(download_dir, exist_ok=True)
    
    # Temporary DNF config to avoid system changes
    temp_dnf_config = "/tmp/temp_dnf.conf"
    with open(temp_dnf_config, "w") as config_file:
        config_file.write("[main]\ngpgcheck=0\n")

    # Prepare the DNF download command
    dnf_command = [
        "dnf", "download", "--alldeps", "--resolve",
        "--destdir", download_dir,
        "--config", temp_dnf_config
    ] + package_list
    
    try:
        # Execute the DNF command to download packages and dependencies
        subprocess.run(dnf_command, check=True)
        print(f"Downloaded packages and dependencies to {download_dir}")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading packages: {e}")
    finally:
        # Cleanup: remove temporary DNF config
        os.remove(temp_dnf_config)

def download_packages(package_list, download_dir, package_type='rpm'):
    """
    Downloads packages and their dependencies based on the system's package management type.
    
    :param package_list: A list of package names to download.
    :param download_dir: The directory where packages will be downloaded.
    :param package_type: The type of package management system ('rpm' or 'deb').
    """
    if package_type == 'rpm':
        # Call the function for downloading RPM packages (as previously defined)
        download_rpm_packages(package_list, download_dir)
    elif package_type == 'deb':
        # Call the function for downloading DEB packages
        download_deb_packages(package_list, download_dir)
    else:
        print("Unsupported package type.")


def extract_packages_qcow2(image_path):
    """
    Extracts a list of packages from a given qcow2 image, automatically determining
    if the system uses RPM or DEB packages.
    
    :param image_path: Path to the qcow2 image
    :return: A tuple of (package_list, package_type) where package_list is a list of packages installed
             in the image, and package_type is either 'rpm' or 'deb'
    """
    mount_point = tempfile.mkdtemp()
    package_list = []
    package_type = None
    
    try:
        subprocess.run(['guestmount', '-a', image_path, '-i', '--ro', mount_point], check=True)
        
        # Check for RPM or DEB system by attempting to list installed packages
        try:
            rpm_output = subprocess.check_output(['chroot', mount_point, 'rpm', '-qa'], universal_newlines=True)
            package_list = rpm_output.strip().split('\n')
            package_type = 'rpm'
        except subprocess.CalledProcessError:
            dpkg_output = subprocess.check_output(['chroot', mount_point, 'dpkg', '-l'], universal_newlines=True)
            for line in dpkg_output.split('\n'):
                if line.startswith("ii"):
                    parts = line.split()
                    package_list.append(parts[1] + "=" + parts[2])  # package_name=version
            package_type = 'deb'
    finally:
        subprocess.run(['guestunmount', mount_point], check=True)
    
    return package_list, package_type


def create_repo(package_dir, package_type):
    """
    Creates an offline repository from a directory of packages.
    
    :param package_dir: Directory containing the packages
    :param package_type: Type of packages ('rpm' or 'deb')
    """
    if not os.path.isdir(package_dir):
        print("The specified directory does not exist or is not a directory.")
        return
    
    if package_type == 'rpm':
        subprocess.run(['createrepo', package_dir], check=True)
        print(f"RPM repository created successfully in {package_dir}")
    elif package_type == 'deb':
        subprocess.run(['dpkg-scanpackages', '.', '/dev/null'], cwd=package_dir, stdout=open(os.path.join(package_dir, 'Packages'), 'w'), check=True)
        subprocess.run(['gzip', '-k', '-f', os.path.join(package_dir, 'Packages')], check=True)
        print(f"APT repository created successfully in {package_dir}")
    else:
        print("Unsupported package type.")
