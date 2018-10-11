import click
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL
from sharedcloud_cli.mappers import _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _create_resource, _update_resource, _delete_resource, \
    _show_field_value, _list_resource
from sharedcloud_cli.validators import _validate_file, _validate_code


@click.group(help='List, create and modify your functions')
@pass_obj
def function(config):
    """List, create and modify your functions"""
    _exit_if_user_is_logged_out(config.token)


@function.command(help='Create a new function')
@click.option('--name', required=True)
@click.option('--image-uuid', required=True, type=click.UUID)
@click.option('--file', required=False, callback=_validate_file, type=click.File())
@click.option('--code', required=False, callback=_validate_code)
@pass_obj
def create(config, name, image_uuid, file, code):
    """
    It creates a new function by providing a set of data.

    It's possible to specify either the "code" or "file" parameter. But there should be at least one.

    >>> sharedcloud function create --name helloWorld --image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --code "def handler(event): print('Hello World!')"
    >>> sharedcloud function create --name helloWorld --image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --file helloworld.py

    :param config: context object
    :param name: name of the function
    :param image_uuid: uuid of the image that this function will use
    :param file: file containing the code of the function
    :param code: code of the function
    """
    if file:
        code = ''
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            code += chunk

    r = _create_resource('{}/api/v1/functions/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'name': name,
        'image': image_uuid,
        'code': code
    })


@function.command(help='Update a function')
@click.option('--uuid', required=True, type=click.UUID)
@click.option('--name', required=False)
@click.option('--image-uuid', required=False, type=click.UUID)
@click.option('--file', required=False, type=click.File())
@click.option('--code', required=False)
@pass_obj
def update(config, uuid, name, image_uuid, file, code):
    """
    It updates a function totally or partially by providing a set of data.

    >>> sharedcloud function create --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --name helloWorld --image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --code "def handler(event): print('Hello World!')"
    >>> sharedcloud function create --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --name helloWorld --image-uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138 --file helloworld.py

    :param config: context object
    :param uuid: uuid of the function
    :param name: name of the function
    :param image_uuid: uuid of the image that this function will use
    :param file: file containing the code of the function
    :param code: code of the function
    """
    if file:
        code = ''
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            code += chunk

    _update_resource('{}/api/v1/functions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid,
        'name': name,
        'image': image_uuid,
        'code': code
    })


@function.command(help='List all your functions')
@pass_obj
def list(config):
    """
    It lists all the user's functions.

    >>> sharedcloud function list

    :param config: context object
    """
    # sharedcloud function list"
    _list_resource('{}/api/v1/functions/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NAME', 'IMAGE', 'NUM_RUNS', 'WHEN'],
                   ['uuid', 'name', 'registry_path', 'num_runs', 'created_at'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@function.command(help='Delete a function')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    """
    It deletes a function by providing an identifier (UUID).

    >>> sharedcloud function delete --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the function
    """
    _delete_resource('{}/api/v1/functions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })


@function.command(help='Display the code of a function')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def code(config, uuid):
    """
    It prints the code of a function into stdout by providing an identifier (UUID).

    >>> sharedcloud function code --uuid 6ea7e5ce-afcc-4027-82a7-e01eeea6b138

    :param config: context object
    :param uuid: uuid of the function
    """
    _show_field_value(
        '{}/api/v1/functions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'code')
