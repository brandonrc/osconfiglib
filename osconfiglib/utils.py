# File: configlib/utils.py

import shutil

def check_dependencies():
    dependencies = ['virt-customize', 'git']
    if missing_dependencies := [
        dependency
        for dependency in dependencies
        if shutil.which(dependency) is None
    ]:
        print("Warning: The following dependencies are missing:")
        for dependency in missing_dependencies:
            print(f"- {dependency}")
        print("Please install the missing dependencies before running this application.")
        
def check_qcow2_file(value):
    if not os.path.isfile(value):
        raise ValueError(f"{value} does not exist")
    if not value.endswith('.qcow2'):
        raise ValueError(f"{value} is not a .qcow2 file")
    return value