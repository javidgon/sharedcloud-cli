import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL, SESSION_STATUSES
from sharedcloud_cli.mappers import _map_datetime_obj_to_human_representation, \
    _map_non_formatted_money_to_version_with_currency, _map_duration_to_human_readable, \
    _map_session_status_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _create_resource, _update_resource, _list_resource


@click.group(help='List, start and stop your sessions')
@pass_obj
def session(config):
    """List, start and stop your sessions"""
    _exit_if_user_is_logged_out(config.token)


@session.command(help='Start a new session')
@click.option('--notebook-uuid', required=True, type=click.UUID)
@click.option('--bid-price', required=True)
@click.option('--password', required=True)
@click.option('--base-gpu-uuid', required=True, type=click.UUID)
@pass_obj
def start(config, notebook_uuid, bid_price, password, base_gpu_uuid):
    """
    It starts a new notebook session by providing a set of data.

    >>> sharedcloud session start --notebook-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --bid-price 0.01 --base-gpu-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param notebook_uuid: uuid of the notebook
    :param bid_price: max price that the user is willing to pay
    :param password: password to access the jupyter notebook
    :param base_gpu_uuid: uuid of the gpu that it's the "minimum requirement" to run session
    """

    _create_resource('{}/api/v1/sessions/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'notebook': notebook_uuid,
        'bid_price': bid_price,
        'password': password,
        'base_gpu': base_gpu_uuid,
    })


@session.command(help='List all your sessions')
@pass_obj
def list(config):
    """
    It lists all the user's sessions.

    >>> sharedcloud session list

    :param config: context object
    """
    _list_resource('{}/api/v1/sessions/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NOTEBOOK', 'STATUS', 'COST', 'URL', 'DURATION', 'BASE_GPU', 'WHEN'],
                   ['uuid', 'notebook_name', 'status', 'cost', 'url', 'duration', 'base_gpu_name', 'created_at'],
                   mappers={
                       'cost': _map_non_formatted_money_to_version_with_currency,
                       'duration': _map_duration_to_human_readable,
                       'status': _map_session_status_to_human_representation,
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@session.command(help='Stop a session')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def stop(config, uuid):
    """
    It stops a session by providing an identifier (UUID).

    >>> sharedcloud session stop --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the session
    """
    _update_resource('{}/api/v1/sessions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'status': SESSION_STATUSES['FINISHED']
    })
