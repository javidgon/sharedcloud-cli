import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_non_formatted_money_to_version_with_currency, \
    _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _create_resource, _delete_resource, _list_resource


@click.group(help='List and create new runs')
@pass_obj
def run(config):
    """List and create new runs"""
    _exit_if_user_is_logged_out(config.token)


@run.command(help='Create a new run')
@click.option('--function-uuid', required=True, type=click.UUID)
@click.option('--parameters', required=True)
@click.option('--bid-price', required=True, type=click.FLOAT)
@click.option('--base-gpu-uuid', required=False)
@pass_obj
def create(config, function_uuid, parameters, bid_price, base_gpu_uuid):
    """
    It creates a new run by providing a set of data.

    It's important to notice that the "parameters" argument needs to be a tuple of tuples. Any other thing will raise a
    validation error.

    >>> sharedcloud run create --function-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --parameters "((1, 2, 3), (4, 5, 6))" --bid-price 2.0 --base_gpu_uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    :param function_uuid: uuid of the function that the run will use
    :param parameters: parameters to be used when creating the jobs. Each tuple will be sent to each Job.
    :param bid_price: max price that the user is willing to pay
    :param base_gpu_uuid: uuid of the gpu that it's the "minimum requirement" to run the batch of jobs created by this run
    """
    _create_resource('{}/api/v1/runs/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'function': function_uuid,
        'parameters': parameters,
        'bid_price': bid_price,
        'base_gpu': base_gpu_uuid
    })


@run.command(help='Delete a run')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    """
    Run delete sub-command. It deletes a run by providing an identifier (UUID).

    >>> sharedcloud run delete --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the function
    """
    _delete_resource('{}/api/v1/runs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })


@run.command(help='List all your runs')
@pass_obj
def list(config):
    """
    Run list sub-command. It lists all the user's runs.

    >>> sharedcloud run list

    :param config: context object
    """
    _list_resource('{}/api/v1/runs/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'PARAMETERS', 'BID_PRICE', 'BASE_GPU', 'FUNCTION', 'WHEN'],
                   ['uuid', 'parameters', 'bid_price', 'base_gpu_name', 'function_name', 'created_at'],
                   mappers={
                       'bid_price': _map_non_formatted_money_to_version_with_currency,
                       'created_at': _map_datetime_obj_to_human_representation
                   })

