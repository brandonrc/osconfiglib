# tests/utils_test.py
import pytest
from osconfiglib import utils

def test_check_dependencies():
    # Assuming your system has 'virt-customize' and 'git' installed
    utils.check_dependencies()  # This should pass without any errors

def test_check_qcow2_file():
    # Assuming '/path/to/valid.qcow2' exists and is a .qcow2 file
    utils.check_qcow2_file('/path/to/valid.qcow2')

    with pytest.raises(ValueError):
        # Assuming '/path/to/invalid.qcow2' does not exist
        utils.check_qcow2_file('/path/to/invalid.qcow2')

    with pytest.raises(ValueError):
        # Assuming '/path/to/file' exists but is not a .qcow2 file
        utils.check_qcow2_file('/path/to/file')
