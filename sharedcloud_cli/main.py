import multiprocessing
import os
import subprocess

import click
import datetime
import requests
import time
import timeago
from click import pass_obj
from tabulate import tabulate


__VERSION__ = '0.0.3'


DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'
DATA_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))

SHAREDCLOUD_CLI_URL = os.environ.get('SHAREDCLOUD_CLI_URL', 'https://sharedcloud.io')
SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME = '{}/{}'.format(DATA_FOLDER, os.environ.get(
    'SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME', 'client_config'))
SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME = '{}/{}'.format(DATA_FOLDER, os.environ.get(
    'SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME', 'instance_config'))

JOB_STATUSES = {
    'CREATED': 1,
    'IN_PROGRESS': 2,
    'SUCCEEDED': 3,
    'FAILED': 4,
    'TIMEOUT': 5
}

INSTANCE_STATUSES = {
    'NOT_AVAILABLE': 1,
    'AVAILABLE': 2
}

INSTANCE_TYPES = {
    'CPU': 1,
    'GPU': 2
}


# Utils
def _read_user_token():
    """
    Read user token from the DATA_FOLDER.
    """
    if not os.path.exists(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME):
        return None
    with open(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME, 'r') as f:
        token = f.read()
    return token


def _read_instance_token():
    """
    Read instance token from the DATA_FOLDER.
    """
    if not os.path.exists(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME):
        return None
    with open(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, 'r') as f:
        uuid = f.read()
    return uuid


def _get_cli_version():
    """
    Returns the CLI version.
    """
    return __VERSION__


def _exit_if_user_is_logged_out(token):
    """
    Exit if user is not logged in.

    :param token: user token
    """
    if not token:
        click.echo('You seem to be logged out. Please log in first')
        exit(1)


def _get_instance_token_or_exit_if_there_is_none():
    """
    Get instance UUID or exit otherwise.
    """
    instance_uuid = _read_instance_token()
    if not instance_uuid:
        click.echo('Instance not found in this computer')
        exit(1)
    return instance_uuid


# Generic methods
def _create_resource(url, token, data):
    """
    Create a resource using a POST request.

    This function is generic and was designed to unify all the POST requests to the Backend.

    :param url: url to create the resource
    :param token: user token
    :param data: dict with data containing all the resource's attributes
    """
    if token:
        r = requests.post(url, data=data,
                          headers={'Authorization': 'Token {}'.format(token)})
    else:
        r = requests.post(url, data=data)

    if r.status_code == 201:
        click.echo(r.json().get('uuid'))
    else:
        click.echo(r.content)
        exit(1)
    return r


def _list_resource(url, token, headers, keys, mappers=None):
    """
    List resources using a GET request.

    This function is generic and was designed to unify all the GET requests to the Backend.
    Additionally, this function displays the returned values using the "tabulate" library.
    We use "mappers" to change the values that we display to the users.

    :param url: url to fetch the data
    :param token: user token
    :param headers: titles that will be displayed once the data is shown to the user
    :param keys: attributes names from the response sent by the Backend
    :param mappers: list of functions that will transform the data that the user sees (Default value = None)
    """

    def _get_data(resource, key, token):
        """
        Iterate over the data a transform the values using the mappers.

        :param resource: resource sent by the Backend
        :param key: attribute that we want to map
        :param token: user token
        """
        value = resource.get(key)
        if key in mappers.keys():
            return mappers[key](value, resource, token)
        return value

    r = requests.get(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        resources = r.json()
        click.echo(tabulate(
            [[_get_data(resource, key, token) for key in keys] for resource in resources],
            headers=headers))
    elif r.status_code == 404:
        click.echo('Not found resource with this UUID')
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


def _show_field_value(url, token, field_name):
    """
    Fetch a resource and extract an attribute from it.

    This function also prints the field right away.
    We use it to show attributes that are to too long to be displayed in a table.

    :param url: url to fetch the data
    :param token: user token
    :param field_name: field to be printed
    """
    r = requests.get(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        click.echo(r.json().get(field_name))
    else:
        click.echo(r.content)
        exit(1)

    return r


def _update_resource(url, token, data):
    """
    Update a resource using a PATCH request.

    This function is generic and was designed to unify all the PATCH requests to the Backend.

    :param url: url to update the resource
    :param token: user token
    :param data: dict with the updated data to be applied
    """
    cleaned_data = {}
    for key, value in data.items():
        if value:
            cleaned_data[key] = value

    r = requests.patch(url, data=cleaned_data, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        click.echo(r.json().get('uuid'))
    elif r.status_code == 404:
        click.echo('Not found resource with this UUID')
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


def _delete_resource(url, token, data):
    """
    Delete a resource using a DELETE request.

    This function is generic and was designed to unify all the DELETE requests to the Backend.

    :param url: url to delete the resource
    :param token: user token
    :param data: dict containing the uuid required to identify the resource
    """
    r = requests.delete(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 204:
        pass
    elif r.status_code == 404:
        click.echo('Not found resource with this UUID')
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


def _perform_instance_action(action, instance_uuid, token, data=None):
    """
    Generic method to update instances and to fetch jobs.
    We use it to change the statuses (e.g., START, STOP)
    and for fetching jobs from the Backend

    :param action: action to perform
    :param instance_uuid: instance uuid
    :param token: user token
    :param data: dict containing the data to apply (Default value = None)
    """
    if not data:
        data = {}

    r = requests.patch('{}/api/v1/instances/{}/{}/'.format(SHAREDCLOUD_CLI_URL, instance_uuid, action),
                       data=data, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        pass
    elif r.status_code == 404:
        click.echo('Not found resource with this UUID')
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


# Mappers
def _map_datetime_obj_to_human_representation(datetime_obj, resource, token):
    """
    Map a datetime obj into a human readable representation.

    :param datetime_obj: the datetime object that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    now = datetime.datetime.strptime(resource.get('current_server_time'), DATETIME_FORMAT)

    if datetime_obj:  # It can be None for certain dates
        return timeago.format(datetime.datetime.strptime(datetime_obj, DATETIME_FORMAT), now)


def _map_job_status_to_human_representation(status, resource, token):
    """
    Map an Job Status type code (e.g., 1, 2) to a human readable name.

    :param status: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for status_name, id in JOB_STATUSES.items():
        if id == status:
            return status_name


def _map_instance_status_to_human_representation(status, resource, token):
    """
    Map an Instance status code (e.g., 1, 2) to a human readable name.

    :param status: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for status_name, id in INSTANCE_STATUSES.items():
        if id == status:
            return status_name


def _map_instance_type_to_human_readable(type, resource, token):
    """
    Map an Instance type code (e.g., 1, 2) to a human readable name.

    :param type: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    for type_name, id in INSTANCE_TYPES.items():
        if id == type:
            return type_name


def _map_non_formatted_money_to_version_with_currency(cost, resource, token):
    """
    Map a non formatted money str (e.g., 0.001) to a version with currency (e.g., $0.001).

    :param cost: float with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    return f'${cost:.3f}'


def _map_duration_to_human_readable(duration, resource, token):
    """
    Map duration in seconds (e.g., 5) into a human readable representation (e.g., 1 second/s).

    :param duration: integer with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    if duration:
        return '{} second/s'.format(duration)


def _map_boolean_to_human_readable(boolean, resource, token):
    """
    Map a boolean into a human readable representation (Yes/No).

    :param boolean: boolean with the value that we want to transform
    :param resource: resource containing all the values and keys
    :param token: user token
    """
    if boolean:
        return 'Yes'
    else:
        return 'No'


# Validators
def _validate_at_least_one_but_only_one(ctx, main_field_value, main_field_key, other_field_key):
    """
    Validate that either "main_field" or "other_field" are passed into the CMD.

    It also validates that only one is provided.

    :param ctx: cmd context
    :param main_field_value: argument containing the main field value to compare with
    :param main_field_key: argument containing the main field name
    :param other_field_key: argument containing the other field name
    """
    if not main_field_value and other_field_key not in ctx.params:
        raise click.BadParameter('Either "{}" or "{}" parameters need to be provided'.format(
            main_field_key, other_field_key))
    if main_field_value and other_field_key in ctx.params:
        raise click.BadParameter('Only one of "{}" and "{}" parameters need to be provided'.format(
            main_field_key, other_field_key))

    return main_field_value


def _validate_code(ctx, param, code):
    return _validate_at_least_one_but_only_one(ctx, code, 'code', 'file')


def _validate_file(ctx, param, file):
    return _validate_at_least_one_but_only_one(ctx, file, 'file', 'code')


class Config(object):
    """
    Context object that will contain the user token.
    """

    def __init__(self):
        self.token = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def cli(config):
    """
    Sharedcloud CLI tool to:

    Check the help available for each command listed below.
    """
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    config.token = _read_user_token()
    config.version = _get_cli_version()


@cli.command(help='Display CLI version')
@pass_obj
def version(config):
    """
    It displays the version of cli.

    >>> sharedcloud version
    """
    click.echo(config.version)


@cli.group(help='List and modify your account details')
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


def _login(username, password):
    r = requests.post('{}/api/v1/api-token-auth/'.format(SHAREDCLOUD_CLI_URL), data={
        'username': username,
        'password': password
    })

    if r.status_code == 200:
        click.echo('Login Succeeded')
        result = r.json()
        with open(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME, 'w+') as f:
            f.write(result.get('token'))
    else:
        click.echo(r.content)
        exit(1)


@cli.command(help='Login into Sharedcloud')
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


def _logout():
    if os.path.exists(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME):
        click.echo('Logout Succeeded')
        os.remove(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME)
    else:
        click.echo('You are already logged out')
        exit(1)


@cli.command(help='Logout from Sharedcloud')
def logout():
    """
    It logs out the user from Sharedcloud.

    >>> sharedcloud logout
    """
    _logout()


@cli.group(help='List the GPUs models available for your runs')
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


@cli.group(help='Manage and download images for your functions')
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
        _perform_instance_action('delete_image', instance_uuid, config.token, data={
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
        _perform_instance_action('add_image', instance_uuid, config.token, data={
            'image_registry_path': registry_path
        })
        for line in output.splitlines():
            click.echo(line + b'\n')


def _update_image(registry_path):
    """
    Update a single image by pulling it from the DockerHub registry.

    :param registry_path: path to the DockerHub registry
    """
    logs = b''
    p = subprocess.Popen(
        ['docker', 'pull', registry_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = p.communicate()

    for line in (output + b'\n' + error).splitlines():
        logs += line + b'\n'

    return logs


def _update_all_images(config):
    """
    Update all the downloaded images.

    :param config: context object
    """
    instance_uuid = _get_instance_token_or_exit_if_there_is_none()

    r = requests.get(
        '{}/api/v1/images/?instance={}'.format(SHAREDCLOUD_CLI_URL, instance_uuid),
        headers={'Authorization': 'Token {}'.format(config.token)})

    if r.status_code == 200:
        images = r.json()

        for image in images:
            logs = _update_image(image.get('registry_path'))
            click.echo(logs)
    else:
        click.echo(r.content)
        exit(1)


@image.command(help='Update all the images in your system')
@pass_obj
def update_all(config):
    """
    It updates all the images downloaded by pulling from the registry.

    >>> sharedcloud image update_all

    :param config: context object
    """
    _update_all_images(config)


@cli.group(help='List, create and modify your functions')
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


@cli.group(help='List and create new runs')
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


@cli.group(help='List all your jobs')
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


@cli.group(help='List the offers that are currently available in Sharedcloud')
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


@cli.group(help='List, create and modify your instances')
@pass_obj
def instance(config):
    """List, create and modify your instances"""
    _exit_if_user_is_logged_out(config.token)


@instance.command(help='Create a new instance')
@click.option('--name', required=True)
@click.option('--type', required=True, default='cpu', type=click.Choice(['cpu', 'gpu']))
@click.option('--ask-price', required=True, type=click.FLOAT)
@click.option('--max-num-parallel-jobs', default=1, type=click.INT)
@click.option('--gpu-uuid', required=False, type=click.UUID)
@pass_obj
def create(config, name, type, ask_price, max_num_parallel_jobs, gpu_uuid):
    """
    It creates a new instance by providing a set of data.

    It's important to notice that the "max-num-parallel-jobs" argument defaults to 1 in case it's not provided

    >>> sharedcloud instance create --name instance1 --type cpu --ask-price 2.0 --max-num-parallel-jobs 3

    :param config: context object
    :param name: name of the instance
    :param type: type of the instance. It can be either "gpu" or "cpu"
    :param ask_price: min price for which the instance would be willing to process jobs
    :param max_num_parallel_jobs: max number of jobs that the instance is allowed to process in parallel
    """
    r = _create_resource('{}/api/v1/instances/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'name': name,
        'type': INSTANCE_TYPES[type.upper()],
        'ask_price': ask_price,
        'max_num_parallel_jobs': max_num_parallel_jobs,
        'gpu': gpu_uuid
    })

    if r.status_code == 201:
        instance = r.json()
        with open(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, 'w') as f:
            f.write(instance.get('uuid'))


@instance.command(help='List your instances')
@pass_obj
def list(config):
    """
    It lists all your instances

    >>> sharedcloud instance list

    :param config: context object
    """
    _list_resource('{}/api/v1/instances/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NAME', 'STATUS', 'ASK_PRICE', 'TYPE', 'GPU', 'RUNNING_JOBS', 'MAX_NUM_PARALLEL_JOBS',
                    'LAST_CONNECTION'],
                   ['uuid', 'name', 'status', 'ask_price', 'type', 'gpu_name', 'num_running_jobs',
                    'max_num_parallel_jobs',
                    'last_connection'],
                   mappers={
                       'status': _map_instance_status_to_human_representation,
                       'type': _map_instance_type_to_human_readable,
                       'last_connection': _map_datetime_obj_to_human_representation
                   })


@instance.command(help='Update an instance')
@click.option('--uuid', required=True, type=click.UUID)
@click.option('--type', required=False, type=click.Choice(['cpu', 'gpu']))
@click.option('--name', required=False)
@click.option('--ask-price', required=False, type=click.FLOAT)
@click.option('--max-num-parallel-jobs', required=False, type=click.INT)
@click.option('--gpu-uuid', required=False, type=click.UUID)
@pass_obj
def update(config, uuid, type, name, ask_price, max_num_parallel_jobs, gpu_uuid):
    """
    It updates totally or partially a new instance by providing a set of data.

    >>> sharedcloud instance update --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647 --name instance1 --type cpu --ask-price 2.0 --max-num-parallel-jobs 3

    :param config: context object
    :param uuid: uuid of the instance
    :param name: name of the instance
    :param type: type of the instance. It can be either "gpu" or "cpu"
    :param ask_price: min price for which the instance would be willing to process jobs
    :param max_num_parallel_jobs: max number of jobs that the instance is allowed to process in parallel
    """

    _update_resource('{}/api/v1/instances/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid,
        'name': name,
        'type': INSTANCE_TYPES[type.upper()] if type else None,
        'ask_price': ask_price,
        'max_num_parallel_jobs': max_num_parallel_jobs,
        'gpu': gpu_uuid,
    })


@instance.command(help='Delete an instance')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    """
    It deletes a run by providing an identifier (UUID).

    >>> sharedcloud instance delete --uuid 8b8b6cc2-ebde-418a-88ba-84e0d6f76647

    :param config: context object
    :param uuid: uuid of the instance
    """

    r = _delete_resource('{}/api/v1/instances/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })

    if r.status_code == 204:
        if os.path.exists(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME):
            os.remove(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME)


@instance.command(help='Start the active instance in your system')
@click.option('--job-timeout', required=False, default=1800.0, type=click.FLOAT)
@pass_obj
def start(config, job_timeout):
    """
    Starts the active instance in your system.

    It's important to notice that, by default, jobs are automatically timeout to 30 minutes. This can be changed by
    the argument "job_timeout", but it's strongly discouraged to do this.

    >>> sharedcloud instance start

    :param config: context object
    :param uuid: uuid of the instance
    """

    def _update_job(job_uuid, data, token):
        """
        Updates a job in Sharedcloud. It's mostly used to send the results.

        :param job_uuid: job uuid
        :param data: dict containing the data to change
        :param token: user token
        """
        r = requests.patch('{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, job_uuid),
                           data=data, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code != 200:
            raise Exception(r.content)
        return r

    def _run_container(job_uuid, job_wrapped_code, job_requires_gpu, job_image_registry_path):
        """
        Runs a container based on the arguments provided.

        :param job_uuid: uuid of the job
        :param job_wrapped_code: job wrapped code
        :param job_requires_gpu: does the job requires gpu?
        :param job_image_registry_path: image path in the DockerHub registry
        """
        container_name = job_uuid
        has_failed = False

        args = ['docker', 'run', '--rm', '--name',
                container_name, '-e', 'CODE={}'.format(job_wrapped_code), job_image_registry_path]

        if job_requires_gpu:
            args.insert(2, '--runtime=nvidia')
        else:
            args.insert(2, '--memory=1024m')
            args.insert(2, '--cpus=1')

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        if p.returncode != 0:
            click.echo('[ERROR] Job {} has failed :('.format(job_uuid))
            if job_requires_gpu:
                click.echo(
                    '[WARNING] As your instance is type "GPU", make sure that the "--max-num-parallel-jobs" in your instance is less than 3')

            has_failed = True

        return output, error, has_failed

    def _exit_if_docker_daemon_is_not_running():
        """
        Exit if the docker daemon is not running in this precise moment.
        """
        p = subprocess.Popen(
            ['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        if error:
            exit('Is the Docker daemon running in your machine?')

    def _job_loop(
            config, job_uuid, job_requires_gpu, job_image_registry_path, job_wrapped_code):
        """
        Performs the job of executing a job and extract his results. It's executed inside a different process.
        :param config: context object
        :param job_uuid: uuid of the job
        :param job_requires_gpu: does the job requires gpu?
        :param job_image_registry_path: image path to the DockerHub registry
        :param job_wrapped_code: job wrapped code

        """
        # We update the job in the remote, so it doesn't get assigned to other instances
        _update_job(
            job_uuid, {
                "status": JOB_STATUSES['IN_PROGRESS']
            }, config.token)

        build_logs = _update_image(job_image_registry_path)

        # After the image has been generated, we run our container and calculate our result
        output, error, has_failed = _run_container(
            job_uuid, job_wrapped_code, job_requires_gpu, job_image_registry_path)

        _update_job(
            job_uuid, {
                "build_logs": build_logs,
                "output": output,
                "error": error,
                "status": JOB_STATUSES['FAILED'] if has_failed else JOB_STATUSES['SUCCEEDED']
            }, config.token)

    instance_uuid = _get_instance_token_or_exit_if_there_is_none()

    _exit_if_docker_daemon_is_not_running()

    try:
        # First, we let our remote know that we are starting the instance
        _perform_instance_action('start', instance_uuid, config.token)
        click.echo('[INFO] Updating all downloaded images...')
        _update_all_images(config)

        click.echo('[INFO] Ready to take Jobs...')

        # Second, we are going to ask the remote, each x seconds, if they have new jobs for us
        while True:
            r = _perform_instance_action('ping', instance_uuid, config.token)

            # If they do have new jobs, we process them...
            jobs = r.json()
            num_jobs = len(jobs)
            if num_jobs > 0:
                click.echo('[INFO] {} job/s arrived, please be patient...'.format(num_jobs))

            processes = {}
            for job in jobs:
                # We extract some useful data about the job/instance that we are going to need
                job_uuid = job.get('job_uuid')
                click.echo('[INFO] Starting Job {}...'.format(job_uuid))

                job_requires_gpu = job.get('requires_gpu')
                job_image_registry_path = job.get('image_registry_path')
                job_wrapped_code = job.get('wrapped_code')

                processes[job_uuid] = multiprocessing.Process(target=_job_loop, name="_job_loop", args=(
                    config, job_uuid, job_requires_gpu, job_image_registry_path, job_wrapped_code))

            for job_uuid, process in processes.items():
                process.start()

            for job_uuid, process in processes.items():
                process.join(job_timeout)  # 30 minutes as default timeout

                if process.is_alive():
                    _update_job(
                        job_uuid, {
                            "status": JOB_STATUSES['TIMEOUT']
                        }, config.token
                    )
                    process.terminate()

            if num_jobs > 0:
                click.echo('[INFO] All jobs were completed.')

            # We wait 5 seconds until the next check
            time.sleep(5)

    except (Exception, KeyboardInterrupt) as e:
        click.echo(e)
        click.echo('Instance {} has just stopped!'.format(instance_uuid))
        _perform_instance_action('stop', instance_uuid, config.token)
        exit(1)
