# osconfiglib/cli/main.py
import click
from osconfiglib import layers, utils, virt_customize

@click.group()
def cli():
    pass

@click.command()
@click.option('--version', is_flag=True, help='Show the version and exit.')
def version():
    click.echo('osconfiglib-cli, version 1.0.0')
cli.add_command(version)

@click.command()
def list_layers():
    # Here you would call the functionality from layers.py that lists the layers
    layers.list_layers()
cli.add_command(list_layers, name='list')

@click.command()
@click.argument('layer')
@click.argument('package')
def add_rpm(layer, package):
    # Here you would call the functionality that adds an rpm to a layer
    click.echo(f'Adding rpm {package} to layer {layer}.')
cli.add_command(add_rpm, name='add-rpm')

@click.command()
@click.argument('layer')
@click.argument('local_filepath')
@click.argument('config_directory')
def add_file(layer, local_filepath, config_directory):
    # Here you would call the functionality that adds a file to a layer
    click.echo(f'Adding file {local_filepath} to layer {layer} at directory {config_directory}.')
cli.add_command(add_file, name='add-file')

@click.command()
@click.argument('layer_name')
def create_layer(layer_name):
    # Here you would call the functionality that creates a new layer
    
    if layers.create_layer(layer_name=layer_name):
        click.echo(f'Creating new layer {layer_name}.')
    else:
        exit(1)
cli.add_command(create_layer, name='create-layer')

@click.command()
@click.argument('url')
@click.argument('branch', required=False, default="main")
def import_layer(url, branch):
    # Here you would call the functionality that creates a new layer
    click.echo(f'Importing layer from url: {url}.')
    if branch == 'main':
        if not layers.import_layer(repo_url=url):
            exit(1)
    else:
        if not layers.import_layer(repo_url=url,branch=branch):
            exit(1)
cli.add_command(import_layer, name='import-layer')

@click.command()
@click.argument('layer_name')
def delete_layer(layer_name):
    # Here you would call the functionality that deletes a layer
    click.echo(f'Deleting layer {layer_name}.')
cli.add_command(delete_layer, name='delete')


@click.command()
@click.argument('recipe')
@click.argument('output_dir')
def export_squashed_configs(recipe,output_dir):
    # Here you would call the functionality that deletes a layer
    click.echo(f'Squashing configs for {recipe} and saving them to {output_dir}.')
    layers.toml_export(recipe,output_dir)
cli.add_command(export_squashed_configs, name='export-squashed-configs')

if __name__ == '__main__':
    cli()