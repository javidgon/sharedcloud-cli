import subprocess

import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _get_instance_token_or_exit_if_there_is_none, \
    _list_resource, _perform_instance_action, _update_all_images


@click.group(help='Manage and download images for your functions')
@pass_obj
def image(config):
    """Manage and download images for your functions"""
    _exit_if_user_is_logged_out(config.token)


@image.command(help='List all the images available in Sharedcloud')
@click.option('--only-downloaded', is_flag=True)
@pass_obj
def list(config, only_downloaded):
    """
    It shows all the Images where you can run your functions.

    The flag "--only-downloaded" filters the images displayed and only shows the ones that have been already downloaded.

    >>> sharedcloud image list
    >>> sharedcloud image list --only-downloaded

    :param config: context object
    :param only_downloaded: flag to filter for downloaded instances
    """
    url = '{}/api/v1/images/'.format(SHAREDCLOUD_CLI_URL)
    if only_downloaded:
        instance_uuid = _get_instance_token_or_exit_if_there_is_none()

        url += '?instance={}'.format(instance_uuid)

    _list_resource(url,
                   config.token,
                   ['UUID', 'REGISTRY_PATH', 'DESCRIPTION', 'REQUIRES_GPU', 'WHEN'],
                   ['uuid', 'registry_path', 'description', 'requires_gpu', 'created_at'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@image.command(help='Clean an image from the system')
@click.option('--registry-path', required=True, type=click.STRING)
@pass_obj
def clean(config, registry_path):
    """
    It cleans an image from the system.

    >>> sharedcloud image clean --registry-path sharedcloud/web-crawling-python36:latest

    :param config: context object
    :param registry_path: the path to the DockerHub registry
    """
    instance_uuid = _get_instance_token_or_exit_if_there_is_none()

    p = subprocess.Popen(
        ['docker', 'rmi', '-f', registry_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    if error:
        for line in error.splitlines():
            click.echo(line + b'\n')
            exit(2)
    else:
        _perform_instance_action('delete-image', instance_uuid, config.token, data={
            'image_registry_path': registry_path
        })
        for line in output.splitlines():
            click.echo(line + b'\n')


@image.command(help='Download an image to your system')
@click.option('--registry-path', required=True)
@pass_obj
def download(config, registry_path):
    """
    It downloads an image to the system.

    >>> sharedcloud image download --registry-path sharedcloud/web-crawling-python36:latest

    :param config: context object
    :param registry_path: the path to the DockerHub registry
    """
    instance_uuid = _get_instance_token_or_exit_if_there_is_none()

    p = subprocess.Popen(
        ['docker', 'pull', registry_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    if error:
        for line in error.splitlines():
            click.echo(line + b'\n')
    else:
        _perform_instance_action('add-image', instance_uuid, config.token, data={
            'image_registry_path': registry_path
        })
        for line in output.splitlines():
            click.echo(line + b'\n')


@image.command(help='Update all the images in your system')
@pass_obj
def update_all(config):
    """
    It updates all the images downloaded by pulling from the registry.

    >>> sharedcloud image update_all

    :param config: context object
    """
    _update_all_images(config)