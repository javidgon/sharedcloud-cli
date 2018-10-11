import click

from sharedcloud_cli.utils import _login


@click.command(help='Login into Sharedcloud')
@click.option('--username', required=True)
def login(username):
    """
    It logs in the user into Sharedcloud by providing a username and password.

    >>> sharedcloud login --username john

    :param username: user's username
    :param password: user's password
    """
    password = click.prompt('Please enter your password', type=str)

    _login(username, password)
