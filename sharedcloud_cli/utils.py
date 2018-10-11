import os
import subprocess

import click
import requests
from tabulate import tabulate

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME, SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, \
    __VERSION__, SHAREDCLOUD_CLI_URL


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


def _get_jobs(instance_uuid, token):
    """
    Get Jobs for the instance.

    :param url: url to fetch the data
    :param token: user token
    """

    r = requests.get('{}/api/v1/instances/{}/get-jobs/'.format(SHAREDCLOUD_CLI_URL, instance_uuid),
                     headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
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


def _logout():
    if os.path.exists(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME):
        click.echo('Logout Succeeded')
        os.remove(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME)
    else:
        click.echo('You are already logged out')
        exit(1)


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
