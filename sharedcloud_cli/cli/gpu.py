import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_boolean_to_human_readable
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _list_resource


@click.group(help='List the GPUs models available for your runs')
@pass_obj
def gpu(config):
    """
    Gpu command.

    :param config: context object
    """
    _exit_if_user_is_logged_out(config.token)


@gpu.command(help='List the GPUs models from Sharedcloud')
@pass_obj
def list(config):
    """
    It shows all the GPUs models and their availability at that precise moment.

    >>> sharedcloud gpu list

    :param config: context object
    """
    url = '{}/api/v1/gpus/'.format(SHAREDCLOUD_CLI_URL)

    _list_resource(url,
                   config.token,
                   ['UUID', 'NAME', 'CODENAME', 'CUDA_CORES', 'IS_AVAILABLE'],
                   ['uuid', 'name', 'codename', 'cuda_cores', 'is_available'],
                   mappers={
                       'is_available': _map_boolean_to_human_readable
                   })