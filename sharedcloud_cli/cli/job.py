import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_non_formatted_money_to_version_with_currency, _map_duration_to_human_readable, \
    _map_job_status_to_human_representation, _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _list_resource, _show_field_value


@click.group(help='List all your jobs')
@pass_obj
def job(config):
    """List all your jobs"""
    _exit_if_user_is_logged_out(config.token)


@job.command(help='List all your jobs')
@pass_obj
def list(config):
    """
    It lists all your jobs.

    >>> sharedcloud job list

    :param config: context object
    """
    _list_resource('{}/api/v1/jobs/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'ID', 'STATUS', 'COST', 'DURATION', 'WHEN', 'RUN_UUID', 'FUNCTION'],
                   ['uuid', 'incremental_id', 'status', 'cost', 'duration', 'created_at', 'run', 'function_name'],
                   mappers={
                       'cost': _map_non_formatted_money_to_version_with_currency,
                       'duration': _map_duration_to_human_readable,
                       'status': _map_job_status_to_human_representation,
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@job.command(help='Display the build logs of a job')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def logs(config, uuid):
    """
    It prints the logs of a job into stdout by providing an identifier (UUID).

    >>> sharedcloud job logs --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    """
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'build_logs')


@job.command(help='Display the result of a job')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def result(config, uuid):
    """
    It prints the result of a job into stdout by providing an identifier (UUID).

    >>> sharedcloud job result --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    """
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'result')


@job.command(help='Display the stdout of a job')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def stdout(config, uuid):
    """
    It prints the output of a job into stdout by providing an identifier (UUID).

    >>> sharedcloud job stdout --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    """
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'stdout')


@job.command(help='Display the stderr of a job')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def stderr(config, uuid):
    """
    It prints the stderr of a job into stdout by providing an identifier (UUID).

    >>> sharedcloud job stderr --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    """
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'stderr')
