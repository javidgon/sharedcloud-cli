import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _create_resource, _update_resource, _delete_resource, \
    _list_resource


@click.group(help='List, create and delete your notebooks')
@pass_obj
def notebook(config):
    """List, create and modify your notebooks"""
    _exit_if_user_is_logged_out(config.token)


@notebook.command(help='Create a new notebook')
@click.option('--name', required=True)
@click.option('--image-uuid', required=True, type=click.UUID)
@pass_obj
def create(config, name, image_uuid):
    """
    It creates a new notebook by providing a set of data.

    >>> sharedcloud notebook create --name helloWorld --image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param name: name of the notebook
    :param image_uuid: uuid of the image that this notebook will use
    """

    _create_resource('{}/api/v1/notebooks/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'name': name,
        'image': image_uuid,
    })


@notebook.command(help='Update a notebook')
@click.option('--uuid', required=True, type=click.UUID)
@click.option('--name', required=False)
@click.option('--image-uuid', required=False, type=click.UUID)
@pass_obj
def update(config, uuid, name, image_uuid):
    """
    It updates a notebook by providing a set of data.

    >>> sharedcloud notebook update --uuid 31a2e9bc-e1bc-4cae-8822-0b1d0becad7c --name helloWorld--image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the notebook
    :param name: name of the notebook
    :param image_uuid: uuid of the image that this notebook will use
    """

    _update_resource('{}/api/v1/notebooks/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'name': name,
        'image': image_uuid,
    })


@notebook.command(help='List all your notebooks')
@pass_obj
def list(config):
    """
    It lists all the user's notebooks.

    >>> sharedcloud notebook list

    :param config: context object
    """
    _list_resource('{}/api/v1/notebooks/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NAME', 'IMAGE', 'WHEN'],
                   ['uuid', 'name', 'image_registry_path', 'created_at'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@notebook.command(help='Delete a notebook')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    """
    It deletes a notebook by providing an identifier (UUID).

    >>> sharedcloud notebook delete --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the notebook
    """
    _delete_resource('{}/api/v1/notebooks/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })
