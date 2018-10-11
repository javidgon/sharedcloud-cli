import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_non_formatted_money_to_version_with_currency, \
    _map_instance_type_to_human_readable, _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _list_resource


@click.group(help='List the offers that are currently available in Sharedcloud')
@pass_obj
def offer(config):
    """List the offers that are currently available in Sharedcloud"""
    _exit_if_user_is_logged_out(config.token)


@offer.command(help='List offers in Sharedcloud')
@pass_obj
def list(config):
    """
    It lists all the offers available


    >>> sharedcloud offer list

    :param config: context object
    """
    _list_resource('{}/api/v1/offers/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['INSTANCE_NAME', 'TYPE', 'GPU', 'CUDA_CORES', 'ASK_PRICE', 'WHEN'],
                   ['name', 'type', 'gpu_name', 'cuda_cores', 'ask_price', 'last_connection'],
                   mappers={
                       'ask_price': _map_non_formatted_money_to_version_with_currency,
                       'type': _map_instance_type_to_human_readable,
                       'last_connection': _map_datetime_obj_to_human_representation
                   })

