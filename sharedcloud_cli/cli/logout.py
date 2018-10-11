import click

from sharedcloud_cli.utils import _logout


@click.command(help='Logout from Sharedcloud')
def logout():
    """
    It logs out the user from Sharedcloud.

    >>> sharedcloud logout
    """
    _logout()
