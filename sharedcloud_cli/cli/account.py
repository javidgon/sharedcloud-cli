import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_non_formatted_money_to_version_with_currency, \
    _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _create_resource, _exit_if_user_is_logged_out, _update_resource, _delete_resource, \
    _list_resource, _logout


@click.group(help='List and modify your account details')
@pass_obj
def account(config):
    """List and modify account details."""
    pass


@account.command(help='Create a new account in Sharedcloud')
@click.option('--email', required=True)
@click.option('--username', required=True)
@pass_obj
def create(config, email, username):
    """
    It creates a new user by providing a set of credentials.

    >>> sharedcloud account create --email blabla@example.com --username blabla

    :param config: context object
    :param email: user's email
    :param username: user's username
    """
    password = click.prompt('Please enter a password', type=str)

    _create_resource('{}/api/v1/users/'.format(SHAREDCLOUD_CLI_URL), None, {
        'email': email,
        'username': username,
        'password': password
    })

    click.echo('Account Created')


@account.command(help='Update an account in Sharedcloud')
@click.option('--email', required=True)
@click.option('--username', required=False)
@pass_obj
def update(config, email, username):
    """
    It updates a user totally or partially.

    >>> sharedcloud account update --email blabla@example.com --username blabla

    :param config: context object
    :param email: user's email
    :param username: user's username
    """
    _exit_if_user_is_logged_out(config.token)

    _update_resource('{}/api/v1/users/account/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'email': email,
        'username': username
    })
    click.echo('Account Updated')

    _logout()


@account.command(help='Change password in Sharedcloud')
@pass_obj
def change_password(config):
    """
    It changes the password of the user.

    >>> sharedcloud account change_password

    :param config: context object
    """
    _exit_if_user_is_logged_out(config.token)

    password = click.prompt('Please enter a new password', type=str)

    _update_resource('{}/api/v1/users/account/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'password': password,
    })

    click.echo('Password Changed')

    _logout()


@account.command(help='Delete an account in Sharedcloud')
@pass_obj
def delete(config):
    """
    It deletes a user account.

    >>> sharedcloud account delete

    :param config: context object
    """
    _exit_if_user_is_logged_out(config.token)

    click.confirm('Are you sure?', abort=True)

    _delete_resource('{}/api/v1/users/account/'.format(SHAREDCLOUD_CLI_URL), config.token, {})

    click.echo('Account Deleted')

    _logout()


@account.command(help='List the account information, such as email, username, balance...')
@pass_obj
def list(config):
    """
    It shows the user account details (e.g., email, username, balance).

    >>> sharedcloud account list

    :param config: context object
    """
    _exit_if_user_is_logged_out(config.token)

    _list_resource('{}/api/v1/users/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'EMAIL', 'USERNAME', 'BALANCE', 'DATE_JOINED', 'LAST_LOGIN'],
                   ['uuid', 'email', 'username', 'balance', 'date_joined', 'last_login'],
                   mappers={
                       'balance': _map_non_formatted_money_to_version_with_currency,
                       'date_joined': _map_datetime_obj_to_human_representation,
                       'last_login': _map_datetime_obj_to_human_representation
                   })
