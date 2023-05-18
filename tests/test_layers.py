# tests/layers_test.py
import pytest
from osconfiglib import layers

# You'll need to mock many of the filesystem and external calls in layers.py
# This is just an example of how you might set up your tests
def test_get_requirements_files(mocker):
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.open', mocker.mock_open(read_data='requirement1\n# This is a comment\nrequirement2'))

    requirements = layers.get_requirements_files('/path/to/layer', 'file.txt')
    assert requirements == ['requirement1', 'requirement2']
