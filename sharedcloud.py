import multiprocessing
import subprocess

import click
import datetime

import psutil
import requests
import os
import time
import shutil
import timeago
from click import pass_obj
from tabulate import tabulate

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
    'STANDARD': 1,
    'GPU': 2
}

# Utils

class ObjectNotFoundException(Exception):
    pass

def _read_token():
    if not os.path.exists(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME):
        return None
    with open(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME, 'r') as f:
        token = f.read()
    return token


def _read_instance_uuid():
    if not os.path.exists(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME):
        return None
    with open(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, 'r') as f:
        uuid = f.read()
    return uuid


def _exit_if_user_is_logged_out(token):
    if not token:
        click.echo('You seem to be logged out. Please log in first')
        exit(1)

def _get_instance_uuid_or_exit_if_there_is_none():
    instance_uuid = _read_instance_uuid()
    if not instance_uuid:
        click.echo('We couldn\'t find an instance in this computer')
        exit(1)
    return instance_uuid


def _get_server_datetime(token):
    r = requests.get('{}/api/v1/server-datetime/'.format(SHAREDCLOUD_CLI_URL),
                     headers={'Authorization': 'Token {}'.format(token)})
    if r.status_code == 200:
        response = r.json()
        return datetime.datetime.strptime(response.get('datetime'), DATETIME_FORMAT)

# Generic methods

def _create_resource(url, token, data):
    if token:
        r = requests.post(url, data=data,
                          headers={'Authorization': 'Token {}'.format(token)})
    else:
        r = requests.post(url, data=data)

    if r.status_code == 201:
        resource = r.json()
        click.echo('Resource with UUID {} has been created.'.format(resource.get('uuid')))
    else:
        click.echo(r.content)
        exit(1)
    return r

def _list_resource(url, token, headers, keys, mappers=None):
    def _get_data(resource, key, token):
        value = resource.get(key)
        if key in mappers.keys():
            return mappers[key](value, token)
        return value

    r = requests.get(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        resources = r.json()
        click.echo(tabulate(
            [[_get_data(resource, key, token) for key in keys] for resource in resources],
            headers=headers))
    else:
        click.echo(r.content)
        exit(1)

    return r


def _show_field_value(url, token, field_name):
    r = requests.get(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        resource = r.json()
        click.echo(resource.get(field_name))
    else:
        click.echo(r.content)
        exit(1)

    return r


def _update_resource(url, token, data):
    # We discard None values
    cleaned_data = {}
    for key, value in data.items():
        if value:
            cleaned_data[key] = value

    r = requests.patch(url, data=cleaned_data, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        click.echo('Resource with UUID {} was updated.'.format(data.get('uuid')))
    elif r.status_code == 404:
        click.echo('Not found resource with UUID {}.'.format(data.get('uuid')))
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


def _delete_resource(url, token, data):
    r = requests.delete(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 204:
        click.echo('Resource with UUID {} was deleted.'.format(data.get('uuid')))
    elif r.status_code == 404:
        click.echo('Not found resource with UUID {}.'.format(data.get('uuid')))
        exit(1)
    else:
        click.echo(r.content)
        exit(1)
    return r


def _perform_instance_action(action, instance_uuid, token, data=None):
    if not data:
        data = {}

    r = requests.patch('{}/api/v1/instances/{}/{}/'.format(SHAREDCLOUD_CLI_URL, instance_uuid, action),
                     data=data, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 404:
        click.echo('Not found resource with UUID {}.'.format(data.get('uuid')))
        exit(1)
    elif r.status_code != 200:
        click.echo(r.content)
        exit(1)
    return r

# Mappers
def _map_datetime_obj_to_human_representation(datetime_obj, token):
    now = _get_server_datetime(token)

    if datetime_obj:  # It can be None for certain dates
        return timeago.format(datetime.datetime.strptime(datetime_obj, DATETIME_FORMAT), now)


def _map_job_status_to_description(status, token):
    for status_name, id in JOB_STATUSES.items():
        if id == status:
            return status_name

def _map_instance_status_to_description(status, token):
    for status_name, id in INSTANCE_STATUSES.items():
        if id == status:
            return status_name

def _map_instance_type_to_description(type, token):
    for type_name, id in INSTANCE_TYPES.items():
        if id == type:
            return type_name

def _map_code_to_reduced_version(code, token):
    if len(code) > 35:
        return code[:30] + '...'
    return code

def _map_cost_number_to_version_with_currency(cost, token):
    return '${}'.format(cost)

def _map_duration_to_readable_version(duration, token):
    if duration:
        return '{} seconds'.format(duration)

# Validators

def _validate_code(ctx, param, code):
    code_value = code
    if not code_value and 'file' not in ctx.params:
        raise click.BadParameter('Either "code" or "file" parameters need to be provided')
    if code_value and 'file' in ctx.params:
        raise click.BadParameter('Only one of "code" and "file" parameters need to be provided')

    return code


def _validate_file(ctx, param, file):
    file_value = file
    if not file_value and 'code' not in ctx.params:
        raise click.BadParameter('Either "code" or "file" parameters need to be provided')
    if file_value and 'code' in ctx.params:
        raise click.BadParameter('Only one of "code" and "file" parameters need to be provided')

    return file


def _validate_uuid(ctx, param, uuid):
    if not uuid and not os.path.exists(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME):
        raise click.BadParameter('This machine doesn\'t seem to contain an instance. If you still want to refer to one that you own, you need to provide the UUID')

    return uuid


class Config(object):
    def __init__(self):
        self.token = None

pass_config = click.make_pass_decorator(Config, ensure=True)

@click.group()
@pass_config
def cli1(config):
    # If Config folder doesn't exist, we create it
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    config.token = _read_token()


@cli1.group(help='Create/Update/Delete/List Account details')
@pass_obj
def account(config):
    pass

@account.command(help='Creates a new Account')
@click.option('--email', required=True)
@click.option('--username', required=True)
@click.option('--password', required=True)
@pass_obj
def create(config, email, username, password):
    # sharedcloud account create --email blabla@example.com--username blabla --password password
    _create_resource('{}/api/v1/users/'.format(SHAREDCLOUD_CLI_URL), None, {
        'email': email,
        'username': username,
        'password': password
    })
    click.echo('')
    click.echo('Welcome aboard! Why you just don\'t start by creating a function?')
    click.echo('>>> sharedcloud function create --name helloWorld --image <image_uuid> --code "def handler(event): print(\'HelloWorld\')"')
    click.echo('')


@account.command(help='Updates an Account')
@click.option('--uuid', required=True, type=click.UUID)
@click.option('--email', required=True)
@click.option('--username', required=False)
@click.option('--password', required=False)
@pass_obj
def update(config, uuid, email, username, password):
    # sharedcloud account update --email blabla@example.com--username blabla --password password
    _exit_if_user_is_logged_out(config.token)

    _update_resource('{}/api/v1/users/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid,
        'email': email,
        'username': username,
        'password': password
    })

    _logout()


@account.command(help='Deletes an Account')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    # sharedcloud account delete --uuid <uuid>
    _exit_if_user_is_logged_out(config.token)

    _delete_resource('{}/api/v1/users/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })

    _logout()

@account.command(help='List Account Information')
@pass_obj
def list(config):
    # sharedcloud account list"
    _exit_if_user_is_logged_out(config.token)

    _list_resource('{}/api/v1/users/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'EMAIL', 'USERNAME', 'BALANCE', 'DATE_JOINED', 'LAST_LOGIN'],
                   ['uuid', 'email', 'username', 'balance', 'date_joined', 'last_login'],
                   mappers={
                       'balance': _map_cost_number_to_version_with_currency,
                       'date_joined': _map_datetime_obj_to_human_representation,
                       'last_login': _map_datetime_obj_to_human_representation
                   })


def _login(username, password):
    r = requests.post('{}/api/v1/api-token-auth/'.format(SHAREDCLOUD_CLI_URL), data={
        'username': username,
        'password': password
    })

    if r.status_code == 200:
        result = r.json()
        with open(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME, 'w+') as f:
            f.write(result.get('token'))
    else:
        click.echo(r.content)
        exit(1)


@cli1.command(help='Login into Sharedcloud')
@click.option('--username', required=True)
@click.option('--password', required=True)
def login(username, password):
    # sharedcloud login username password
    _login(username, password)


def _logout():
    if os.path.exists(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME):
        click.echo('You have been logged out.')
        os.remove(SHAREDCLOUD_CLI_CLIENT_CONFIG_FILENAME)
    else:
        click.echo('You were already logged out.')
        exit(1)


@cli1.command(help='Logout from Sharedcloud')
def logout():
    # sharedcloud logout
    _logout()


@cli1.group(help='List/Clean/Download Images')
@pass_obj
def image(config):
    _exit_if_user_is_logged_out(config.token)

@image.command(help='List Images')
@click.option('--only-downloaded', is_flag=True)
@pass_obj
def list(config, only_downloaded):
    # sharedcloud image list"

    url = '{}/api/v1/images/'.format(SHAREDCLOUD_CLI_URL)
    if only_downloaded:
        instance_uuid = _get_instance_uuid_or_exit_if_there_is_none()

        url += '?instance={}'.format(instance_uuid)

    _list_resource(url,
                   config.token,
                   ['UUID', 'REGISTRY_PATH', 'DESCRIPTION', 'REQUIRES_GPU', 'WHEN'],
                   ['uuid', 'registry_path', 'description', 'requires_gpu', 'created_at'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })

@image.command(help='Clean Image from the system')
@click.option('--registry-path', required=True, type=click.STRING)
@pass_obj
def clean(config, registry_path):
    # sharedcloud image clean --registry-path <image>
    instance_uuid = _get_instance_uuid_or_exit_if_there_is_none()

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

@image.command(help='Download Image')
@click.option('--registry-path', required=True)
@pass_obj
def download(config, registry_path):
    # sharedcloud image download --registry-path <image>
    instance_uuid = _get_instance_uuid_or_exit_if_there_is_none()

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


def _update_all_images(config):
    instance_uuid = _get_instance_uuid_or_exit_if_there_is_none()

    r = requests.get(
        '{}/api/v1/images/?instance={}'.format(SHAREDCLOUD_CLI_URL, instance_uuid),
        headers={'Authorization': 'Token {}'.format(config.token)})

    if r.status_code == 200:
        images = r.json()

        for image in images:
            p = subprocess.Popen(
                ['docker', 'pull', image.get('registry_path')], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output, error = p.communicate()

            for line in (output + b'\n' + error).splitlines():
                click.echo(line + b'\n')
    else:
        click.echo(r.content)
        exit(1)

@image.command(help='Update All downloaded Images')
@pass_obj
def update_all(config):
    # sharedcloud image update_all
    _update_all_images(config)

@cli1.group(help='Create/Delete/Update/List Functions')
@pass_obj
def function(config):
    _exit_if_user_is_logged_out(config.token)


@function.command(help='Creates a new Function')
@click.option('--name', required=True)
@click.option('--image-uuid', required=True, type=click.UUID)
@click.option('--file', required=False, callback=_validate_file, type=click.File())
@click.option('--code', required=False, callback=_validate_code)
@pass_obj
def create(config, name, image_uuid, file, code):
    # sharedcloud function create --name mything --image-uuid <uuid> --code "def handler(event): return 2"
    # sharedcloud function create --name mything --image-uuid <uuid> --file "file.py"
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
    resource = r.json()
    function_uuid = resource.get('uuid')
    click.echo('')
    click.echo('Congrats! Now you have the following options to run your function:')
    click.echo('1) CLI: sharedcloud run create --function-uuid {} --parameters <parameters>'.format(function_uuid))
    click.echo('2) REST endpoint: {}/api/v1/runs/ (POST)'.format(SHAREDCLOUD_CLI_URL))
    click.echo('\t\t BODY: {"function": "' + function_uuid + '", "parameters": <parameters>}')
    click.echo('\t\t HEADER: "Authorization: Token {}"'.format(config.token))
    click.echo('')

@function.command(help='Update a Function')
@click.option('--uuid', required=True, type=click.UUID)
@click.option('--name', required=False)
@click.option('--image-uuid', required=False, type=click.UUID)
@click.option('--file', required=False, type=click.File())
@click.option('--code', required=False)
@pass_obj
def update(config, uuid, name, image_uuid, file, code):
    # sharedcloud function update --uuid <uuid> --name mything --image-uuid <uuid> --code "import sys; print(sys.argv)"
    # sharedcloud function update  --uuid <uuid> --name mything --image-uuid <uuid> --file "file.py"
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


@function.command(help='List Functions')
@pass_obj
def list(config):
    # sharedcloud function list"
    _list_resource('{}/api/v1/functions/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NAME', 'IMAGE', 'NUM_RUNS', 'WHEN'],
                   ['uuid', 'name', 'registry_path', 'num_runs', 'created_at'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@function.command(help='Deletes a Function')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    # sharedcloud function delete --uuid <uuid>
    _delete_resource('{}/api/v1/functions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })

@function.command(help='Display the Functions\'s code')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def code(config, uuid):
    _show_field_value(
        '{}/api/v1/functions/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'code')

@cli1.group(help='Create/List Runs')
@pass_obj
def run(config):
    _exit_if_user_is_logged_out(config.token)


@run.command(help='Creates a new Run')
@click.option('--function-uuid', required=True, type=click.UUID)
@click.option('--parameters', required=True)
@pass_obj
def create(config, function_uuid, parameters):
    # sharedcloud run create --function-uuid <uuid> --parameters "((1, 2, 3), (4, 5, 6))"
    _create_resource('{}/api/v1/runs/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'function': function_uuid,
        'parameters': parameters
    })


@run.command(help='Deletes a Run')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def delete(config, uuid):
    # sharedcloud run delete --uuid <uuid>
    _delete_resource('{}/api/v1/runs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })


@run.command(help='List Runs')
@pass_obj
def list(config):
    # sharedcloud function list"
    _list_resource('{}/api/v1/runs/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'PARAMETERS', 'WHEN', 'FUNCTION'],
                   ['uuid', 'parameters', 'created_at', 'function_name'],
                   mappers={
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@cli1.group(help='List Jobs')
@pass_obj
def job(config):
    _exit_if_user_is_logged_out(config.token)


@job.command(help='List Jobs')
@pass_obj
def list(config):
    _list_resource('{}/api/v1/jobs/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'ID', 'STATUS', 'COST', 'DURATION', 'WHEN', 'RUN_UUID', 'FUNCTION'],
                   ['uuid', 'incremental_id', 'status', 'cost', 'duration', 'created_at', 'run', 'function_name'],
                   mappers={
                       'cost': _map_cost_number_to_version_with_currency,
                       'duration': _map_duration_to_readable_version,
                       'status': _map_job_status_to_description,
                       'created_at': _map_datetime_obj_to_human_representation
                   })

@job.command(help='Display the Job\'s build logs')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def logs(config, uuid):
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'build_logs')


@job.command(help='Display the Job\'s result')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def result(config, uuid):
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'result')


@job.command(help='Display the Job\'s stdout')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def stdout(config, uuid):
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'stdout')


@job.command(help='Display the Job\'s stderr')
@click.option('--uuid', required=True, type=click.UUID)
@pass_obj
def stderr(config, uuid):
    _show_field_value(
        '{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, 'stderr')


@job.command(help='List Jobs')
@pass_obj
def list(config):
    _list_resource('{}/api/v1/jobs/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'ID', 'STATUS', 'COST', 'DURATION', 'WHEN', 'RUN_UUID', 'FUNCTION'],
                   ['uuid', 'incremental_id', 'status', 'cost', 'duration', 'created_at', 'run', 'function_name'],
                   mappers={
                       'cost': _map_cost_number_to_version_with_currency,
                       'duration': _map_duration_to_readable_version,
                       'status': _map_job_status_to_description,
                       'created_at': _map_datetime_obj_to_human_representation
                   })


@cli1.group(help='Create/Update/Start/List Instances')
@pass_obj
def instance(config):
    _exit_if_user_is_logged_out(config.token)


@instance.command(help='Creates a new Instance')
@click.option('--name', required=True)
@click.option('--type', required=True, type=click.Choice(['standard', 'gpu']))
@click.option('--price-per-minute', required=True, type=click.FLOAT)
@click.option('--max-num-parallel-jobs', default=1, type=click.INT)
@pass_obj
def create(config, name, type, price_per_minute, max_num_parallel_jobs):
    # sharedcloud instance create --name blabla --type standard --price-per-minute 2.0 --max-num-parallel-jobs 3

    r = _create_resource('{}/api/v1/instances/'.format(SHAREDCLOUD_CLI_URL), config.token, {
        'name': name,
        'type': INSTANCE_TYPES[type.upper()],
        'price_per_minute': price_per_minute,
        'max_num_parallel_jobs': max_num_parallel_jobs,
    })
    if r.status_code == 201:
        instance = r.json()
        with open(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, 'w') as f:
            f.write(instance.get('uuid'))


@instance.command(help='List Instances')
@pass_obj
def list(config):
    _list_resource('{}/api/v1/instances/'.format(SHAREDCLOUD_CLI_URL),
                   config.token,
                   ['UUID', 'NAME', 'STATUS', 'PRICE_PER_MINUTE', 'TYPE', 'NUM_RUNNING_JOBS', 'MAX_NUM_PARALLEL_JOBS' ,'LAST_CONNECTION'],
                   ['uuid', 'name', 'status', 'price_per_minute', 'type', 'num_running_jobs', 'max_num_parallel_jobs', 'last_connection'],
                   mappers={
                       'status': _map_instance_status_to_description,
                       'type': _map_instance_type_to_description,
                       'last_connection': _map_datetime_obj_to_human_representation
                   })


@instance.command(help='Update an Instance')
@click.option('--uuid', required=True, callback=_validate_uuid, type=click.UUID)
@click.option('--type', required=False, type=click.Choice(['standard', 'gpu']))
@click.option('--name', required=False)
@click.option('--price-per-minute', required=False, type=click.FLOAT)
@click.option('--max-num-parallel-jobs', required=False, type=click.INT)
@pass_obj
def update(config, uuid, type, name, price_per_minute, max_num_parallel_jobs):
    # sharedcloud instance update --name blabla --type standard --price-per-minute 2.0 --max-num-parallel-jobs 3

    _update_resource('{}/api/v1/instances/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid,
        'name': name,
        'type': INSTANCE_TYPES[type.upper()] if type else None,
        'price_per_minute': price_per_minute,
        'max_num_parallel_jobs': max_num_parallel_jobs,
    })


@instance.command(help='Deletes an Instance')
@click.option('--uuid', required=True, callback=_validate_uuid, type=click.UUID)
@pass_obj
def delete(config, uuid):
    # sharedcloud instance delete [--uuid <uuid>]

    r = _delete_resource('{}/api/v1/instances/{}/'.format(SHAREDCLOUD_CLI_URL, uuid), config.token, {
        'uuid': uuid
    })

    if r.status_code == 204:
        if os.path.exists(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME):
            os.remove(SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME)


@instance.command(help='Starts an Instance')
@click.option('--job-timeout', required=False, default=1800.0, type=click.FLOAT)
@pass_obj
def start(config, job_timeout):

    def _update_job_remotely(job_uuid, data, token):
        r = requests.patch('{}/api/v1/jobs/{}/'.format(SHAREDCLOUD_CLI_URL, job_uuid),
                           data=data, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code != 200:
            raise Exception(r.content)
        return r

    def _pull_image(job_image_path):
        # TODO: This output should probably be sent to us to analyse it. e.g., docker build errors
        build_logs = b''

        p = subprocess.Popen(
            ['docker', 'pull', job_image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        for line in (output + b'\n' + error).splitlines():
            build_logs += line + b'\n'
        return build_logs

    def _run_container(job_uuid, job_wrapped_code, job_requires_gpu, job_image_path):
        stdout = b''
        stderr = b''
        result = b''
        container_name = job_uuid
        has_failed = False
        def _extract_output(output):
            stdout = b''
            result = b''
            for line in output.splitlines():
                if 'ResponseHandler' in str(line):
                    start = str(line).find('|') - 1
                    end = str(line).find('?') - 2
                    result = line[start:end]
                else:
                    stdout += line + b'\n'

            return stdout, result

        args = ['docker', 'run', '--rm', '--memory=1024m', '--cpus=1', '--name',
             container_name, '-e', 'CODE={}'.format(job_wrapped_code), job_image_path]

        if job_requires_gpu:
            args.insert(2, '--runtime=nvidia')

        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        if p.returncode != 0:
            has_failed = True
            stderr = error
            stdout, _ = _extract_output(output)
        else:
            stdout, result = _extract_output(output)

        return stdout, stderr, result, has_failed

    def _exit_if_docker_daemon_is_not_running():
        p = subprocess.Popen(
            ['docker', 'ps'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = p.communicate()

        if error:
            exit('Is the Docker daemon running in your machine?')

    def _report_failure(job_uuid, stdout, stderr, result, build_logs):
        _update_job_remotely(
            job_uuid, {
                "build_logs": build_logs,
                "stdout": stdout,
                "stderr": stderr,
                "result": result,
                "status": JOB_STATUSES['FAILED']
            }, config.token)

    def _report_success(job_uuid, stdout, stderr, result, build_logs):
        _update_job_remotely(
            job_uuid, {
                "build_logs": build_logs,
                "stdout": stdout,
                "stderr": stderr,
                "result": result,
                "status": JOB_STATUSES['SUCCEEDED']
            }, config.token)

    def _report_timeout(job_uuid):
        _update_job_remotely(
            job_uuid, {
                "status": JOB_STATUSES['TIMEOUT']
            }, config.token)

    def _job_loop(
            config, job_uuid, job_requires_gpu, job_image_registry_path, job_wrapped_code):
        # We update the job in the remote, so it doesn't get assigned to other instances
        _update_job_remotely(
            job_uuid, {
                "status": JOB_STATUSES['IN_PROGRESS']
            }, config.token)

        build_logs = _pull_image(job_image_registry_path)

        # After the image has been generated, we run our container and calculate our result
        stdout, stderr, result, has_failed = _run_container(
            job_uuid, job_wrapped_code, job_requires_gpu, job_image_registry_path)
        if has_failed:
            _report_failure(job_uuid, stdout, stderr, result, build_logs)
        else:
            _report_success(job_uuid, stdout, stderr, result, build_logs)


    instance_uuid = _get_instance_uuid_or_exit_if_there_is_none()

    _exit_if_docker_daemon_is_not_running()

    # sharedcloud instance start --uuid <uuid>

    job_uuid = None
    try:
        # First, we let our remote know that we are starting the instance
        _perform_instance_action('start', instance_uuid, config.token)
        click.echo('Updating all downloaded images...')
        _update_all_images(config)

        click.echo('Ready to take Jobs...')

        # Second, we are going to ask the remote, each x seconds, if they have new jobs for us
        while True:
            r = _perform_instance_action('ping', instance_uuid, config.token)

            # If they do have new jobs, we process them...
            jobs = r.json()
            num_jobs = len(jobs)
            if num_jobs > 0:
                click.echo('{} job/s arrived, please be patient...'.format(num_jobs))

            processes = {}
            for job in jobs:
                # We extract some useful data about the job/instance that we are going to need
                job_uuid = job.get('job_uuid')
                click.echo('Starting Job {}...'.format(job_uuid))

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
                    _report_timeout(job_uuid)
                    process.terminate()

            if num_jobs > 0:
                click.echo('All jobs were completed!')

            # We reset the current job_uuid, as everything was processed successfully
            job_uuid = None

            # We wait 5 seconds until the next check
            time.sleep(5)

    except (Exception, KeyboardInterrupt) as e:
        click.echo(e)
        click.echo('Instance {} has just stopped!'.format(instance_uuid))
        _perform_instance_action('stop', instance_uuid, config.token)
        exit(1)
