import click
from click import pass_obj


@click.command(help='Display CLI version')
@pass_obj
def version(config):
    """
    It displays the version of cli.

    >>> sharedcloud version
    """
    click.echo(config.version)