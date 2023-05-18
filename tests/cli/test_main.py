# tests/cli_test.py
from click.testing import CliRunner
from osconfiglib.cli import main

def test_version():
    runner = CliRunner()
    result = runner.invoke(main.cli, ['--version'])
    assert result.exit_code == 0
    assert result.output == 'osconfiglib-cli, version 1.0.0\n'

def test_list_layers(mocker):
    mocker.patch('osconfiglib.layers.list_layers')
    runner = CliRunner()
    result = runner.invoke(main.cli, ['list'])
    assert result.exit_code == 0

# You can write similar tests for the other CLI commands
