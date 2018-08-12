import click
import datetime
import requests
import os
import time
import shutil
import timeago
from tabulate import tabulate
from subprocess import check_output, CalledProcessError

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'
BASE_URL = os.environ.get('BASE_URL', 'http://142.93.102.53:8000')
CONFIG_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))
CONFIG_FILE = '{}/config'.format(CONFIG_FOLDER)

JOB_STATUSES = {
    'WAITING': 1,
    'IN_PROGRESS': 2,
    'SUCCEEDED': 3,
    'FAILED': 4,
    'TIMEOUT': 5
}


# Generic methods

def _create_resource(url, token, data):
    if not token:
        click.echo('Please log in first')
        return

    r = requests.post(url, data=data,
                      headers={'Authorization': 'Token {}'.format(token)})
    if r.status_code == 201:
        result = r.json()
        click.echo('Resource with UUID {} has been created.'.format(result.get('uuid')))
    else:
        click.echo(r.content)


def _list_resource(url, token, headers, keys, mappers=None):
    def _get_data(resource, key):
        value = resource.get(key)
        if key in mappers.keys():
            return mappers[key](value)
        return value

    if not token:
        click.echo('Please log in first')
        return

    r = requests.get(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 200:
        resources = r.json()

        click.echo(tabulate(
            [[_get_data(resource, key) for key in keys] for resource in resources],
            headers=headers))
    else:
        click.echo(r.content)


def _delete_resource(url, token, data):
    if not token:
        click.echo('Please log in first')
        return

    r = requests.delete(url, headers={'Authorization': 'Token {}'.format(token)})

    if r.status_code == 204:
        click.echo('Resource with UUID {} was deleted.'.format(data.get('uuid')))
    elif r.status_code == 404:
        click.echo('Not found resource with UUID {}'.format(data.get('uuid')))
    else:
        click.echo(r.content)

# Mappers
def _map_created_at_to_human_representation(created_at):
    now = datetime.datetime.now()
    return timeago.format(datetime.datetime.strptime(created_at, DATETIME_FORMAT), now)


def _map_status_to_description(status):
    for status_name, id in JOB_STATUSES.items():
        if id == status:
            return status_name

def _map_code_to_reduced_version(code):
    if len(code) > 35:
        return code[:30] + '...'
    return code


class Config(object):

    def __init__(self):
        self.token = None


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@pass_config
def cli1(config):
    def _read_token():
        if not os.path.exists(CONFIG_FILE):
            return None
        with open(CONFIG_FILE, 'r') as f:
            token = f.read()
        return token

    # If Config folder doesn't exist, we create it
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    config.token = _read_token()


@cli1.command(help='Login into Sharedcloud')
@click.argument('username', required=True)
@click.argument('password', required=True)
def login(username, password):
    # sharedcloud login username password
    r = requests.post('{}/api-token-auth/'.format(BASE_URL), data={
        'username': username,
        'password': password
    })

    if r.status_code == 200:
        result = r.json()
        with open(CONFIG_FILE, 'w+') as f:
            f.write(result.get('token'))

        click.echo('Successfully logged in :)')
    else:
        click.echo(r.content)


@cli1.group(help='Create/Delete/List Tasks')
@pass_config
def task(config):
    pass


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


@task.command(help='Creates a new Task')
@click.option('--name', required=True)
@click.option('--language', required=True, type=click.Choice(['python']))
@click.option('--file', required=False, callback=_validate_file, type=click.File())
@click.option('--code', required=False, callback=_validate_code)
@pass_config
def create(config, name, language, file, code):
    # sharedcloud task create --name mything --language python --code "import sys; print(sys.argv)"
    # sharedcloud task create --name mything --language python --file "file.py"

    if file:
        code = ''
        while True:
            chunk = file.read(1024)
            if not chunk:
                break
            code += chunk

    _create_resource('{}/tasks/'.format(BASE_URL), config.token, {
        'name': name,
        'language': language,
        'code': code
    })


@task.command(help='List Tasks')
@pass_config
def list(config):
    # sharedcloud task list"
    _list_resource('{}/tasks/'.format(BASE_URL),
                   config.token,
                   ['UUID', 'NAME', 'LANGUAGE', 'CODE', 'CREATED'],
                   ['uuid', 'name', 'programming_language', 'code', 'created_at'],
                   mappers={
                       'code': _map_code_to_reduced_version,
                       'created_at': _map_created_at_to_human_representation
                   })


@task.command(help='Deletes a Task')
@click.option('--uuid', required=True, type=click.UUID)
@pass_config
def delete(config, uuid):
    # sharedcloud task delete --uuid <uuid>
    _delete_resource('{}/tasks/{}/'.format(BASE_URL, uuid), config.token, {
        'uuid': uuid
    })


@cli1.group(help='Create/List Runs')
@pass_config
def run(config):
    pass


def _validate_parameters(ctx, param, parameters):
    try:
        parameters_value = eval(parameters)
        if not isinstance(parameters_value, tuple):
            raise SyntaxError()
    except SyntaxError:
        raise click.BadParameter(
            '"parameters" needs to have the structure of a tuple of tuples. e.g., ((1, 2), (3, 4))')

    try:
        if len(parameters_value) == 0:
            raise SyntaxError(
                '"parameters" needs to contain at least one inner tuple. Don\'t forget the comma at the end: e.g., ((1, 2),)')
        else:
            for parameter in parameters_value:
                if not isinstance(parameter, tuple):
                    raise SyntaxError(
                        '"parameters" need to contain inner tuples. Don\'t forget the comma at the end: e.g., ((1, 2),)')
    except SyntaxError as e:
        raise click.BadParameter(e.msg)

    return parameters


@run.command(help='Creates a new Run')
@click.option('--task_uuid', required=True, type=click.UUID)
@click.option('--parameters', required=True, callback=_validate_parameters)
@pass_config
def create(config, task_uuid, parameters):
    # sharedcloud run create --task_uuid <uuid> --parameters "((1, 2, 3), (4, 5, 6))"
    _create_resource('{}/runs/'.format(BASE_URL), config.token, {
        'task': task_uuid,
        'parameters': parameters
    })


@run.command(help='List Runs')
@pass_config
def list(config):
    # sharedcloud task list"
    _list_resource('{}/runs/'.format(BASE_URL),
                   config.token,
                   ['UUID', 'PARAMETERS', 'CREATED', 'TASK_NAME'],
                   ['uuid', 'parameters', 'created_at', 'task_name'],
                   mappers={
                       'created_at': _map_created_at_to_human_representation
                   })


@cli1.group(help='List Jobs')
@pass_config
def job(config):
    pass


@job.command(help='List Jobs')
@pass_config
def list(config):
    _list_resource('{}/jobs/'.format(BASE_URL),
                   config.token,
                   ['UUID', 'ID', 'STATUS', 'CMD_OUTPUT', 'CREATED', 'RUN_UUID', 'TASK_NAME'],
                   ['uuid', 'incremental_id', 'status', 'cmd_output', 'created_at', 'run', 'task_name'],
                   mappers={
                       'status': _map_status_to_description,
                       'created_at': _map_created_at_to_human_representation
                   })


@cli1.group(help='Register/Start/List Instances')
@pass_config
def instance(config):
    pass


@instance.command(help='Registers a new Instance')
@click.option('--name', required=True)
@click.option('--price_per_hour', required=True, type=click.FLOAT)
@click.option('--max_num_jobs', required=True, type=click.INT)
@pass_config
def register(config, name, price_per_hour, max_num_jobs):
    # sharedcloud instance register --name blabla --price_per_hour 2.0 --max_num_jobs 3
    _create_resource('{}/instances/'.format(BASE_URL), config.token, {
        'name': name,
        'price_per_hour': price_per_hour,
        'max_num_jobs': max_num_jobs,
    })


@instance.command(help='Deletes an Instance')
@click.option('--uuid', required=True, type=click.UUID)
@pass_config
def delete(config, uuid):
    # sharedcloud instance delete --uuid <uuid>
    _delete_resource('{}/instances/{}/'.format(BASE_URL, uuid), config.token, {
        'uuid': uuid
    })


@instance.command(help='Starts an Instance')
@click.option('--uuid', required=True, type=click.UUID)
@pass_config
def start(config, uuid):
    class ObjectNotFoundException(Exception):
        pass

    def _make_put_request(action, instance_uuid, token):
        r = requests.put('{}/instances/{}/{}/'.format(BASE_URL, instance_uuid, action),
                         data={}, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code == 404:
            raise ObjectNotFoundException()
        elif r.status_code != 200:
            raise Exception(r.content)
        return r

    def _make_patch_request(job_uuid, data, token):
        r = requests.patch('{}/jobs/{}/'.format(BASE_URL, job_uuid),
                           data=data, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code == 404:
            raise ObjectNotFoundException()
        elif r.status_code != 200:
            raise Exception(r.content)
        return r

    def _create_file_from_data(data, to_file):
        with open(to_file, 'w') as text_file:
            text_file.write(data)

    def _generate_image(job_uuid, job_folder):
        build_output = b''
        image_tag = job_uuid

        docker_build = check_output(
            ['docker', 'build', '-t', '{}:latest'.format(image_tag),
             '-f', '{}/{}/Dockerfile'.format(CONFIG_FOLDER, job_uuid), job_folder])
        for line in docker_build.splitlines():
            build_output += line + b'\n'
        return image_tag, build_output

    def _run_container(image_tag):
        cmd_output = b''
        container_name = image_tag
        has_timeout = False

        try:
            docker_run = check_output(
                ['docker', 'run', '--memory=512m', '--cpus=1', '--name', container_name, '{}:latest'.format(image_tag)])
            for line in docker_run.splitlines():
                cmd_output += line + b'\n'
        except CalledProcessError as grepexc:
            # When it exists due to a timeout we don't exit the cli as it's kind of an expected error
            if grepexc.returncode == 124:
                has_timeout = True
            else:
                raise

        return container_name, cmd_output, has_timeout

    def _destroy_container(container_name, build_output):
        try:
            docker_destroy_container = check_output(
                ['docker', 'rm', container_name, '--force'])
            for line in docker_destroy_container.splitlines():
                build_output += line + b'\n'
        except CalledProcessError as rmpexc:
            # It's fine if it fails as the container probably doesn't exist
            pass

        return build_output

    def _destroy_image(image_tag, build_output):
        try:
            docker_destroy_image = check_output(
                ['docker', 'rmi', image_tag, '--force'])
            for line in docker_destroy_image.splitlines():
                build_output += line + b'\n'
        except CalledProcessError as rmipexc:
            # It's fine if it fails as the image probably doesn't exist
            pass

        return build_output

    def _exit_if_docker_daemon_is_not_running():
        try:
            check_output(
                ['docker', 'ps'])
        except CalledProcessError as pgrepexc:
            exit('Is the Docker daemon running in your machine?')

    instance_uuid = uuid

    _exit_if_docker_daemon_is_not_running()

    # sharedcloud instance start --uuid <uuid>
    if not config.token:
        click.echo('Please log in first')
        return

    job_uuid = None
    build_output = b''
    cmd_output = b''

    try:
        # First, we let our remote know that we are starting the instance
        _make_put_request('start', instance_uuid, config.token)

        # Second, we are going to ask the remote, each x seconds, if they have new jobs for us
        while True:
            r = _make_put_request('ping', instance_uuid, config.token)

            # If they do have new jobs, we process them...
            jobs = r.json()
            num_jobs = len(jobs)
            if num_jobs > 0:
                click.echo('{} job/s arrived, please be patient...'.format(num_jobs))

            for job in jobs:
                # We extract some useful data about the job/instance that we are going to need
                job_uuid = job.get('job_uuid')
                job_started_at = datetime.datetime.now()
                job_folder = CONFIG_FOLDER + '/{}'.format(job_uuid)
                instance_price_per_hour = job.get('instance_price_per_hour')

                # We update the job in the remote, so it doesn't get assigned to other instances
                _make_patch_request(
                    job_uuid, {
                        "status": JOB_STATUSES['IN_PROGRESS'],
                        "started_at": job_started_at
                    }, config.token)

                # Now we build the job folder in the local computer, so we can do the job

                # If the job folder already exists, we clean up before
                if os.path.exists(job_folder):
                    shutil.rmtree(job_folder)

                # Here we create an empty job folder
                os.makedirs(job_folder)

                # Here we create files from the received Dockerfile and Code
                _create_file_from_data(job.get('dockerfile'), '{}/Dockerfile'.format(job_folder))
                _create_file_from_data(job.get('code'), '{}/file.py'.format(job_folder))

                # After the files have been created, we can generate the image that we are going to
                # use to run our container
                image_tag, build_output = _generate_image(job_uuid, job_folder)
                # After the image has been generated, we run our container and calculate our result
                container_name, cmd_output, has_timeout = _run_container(image_tag)

                # After this has been done, we make sure to clean up the image, container and job folder
                build_output = _destroy_container(container_name, build_output)
                build_output = _destroy_image(image_tag, build_output)
                shutil.rmtree(job_folder)

                # Finally, we let our remote know that job's stats
                _make_patch_request(
                    job_uuid, {
                        "build_output": build_output,
                        "cmd_output": cmd_output,
                        "status": JOB_STATUSES['SUCCEEDED'] if not has_timeout else JOB_STATUSES['TIMEOUT'],
                        "finished_at": datetime.datetime.now(),
                        "cost": round(
                            int((datetime.datetime.now() - job_started_at).total_seconds()) * (
                                        instance_price_per_hour / 3600), 3)
                    }, config.token)

            if num_jobs > 0:
                click.echo('All jobs were completed!')

            # We reset the current job_uuid, as everything was processed successfully
            job_uuid = None
            # We wait 60 seconds until the next check
            time.sleep(60)

    except ObjectNotFoundException as e:
        click.echo('Not found Instance with this UUID')
    except Exception as e:
        click.echo('Instance stopped!')
        _make_put_request('stop', instance_uuid, config.token)
        click.echo(e)

        # If the error was provoked by a job, we update our remote with the output
        if job_uuid:
            # Just in case, we try to delete the container and the image, in case they were pending
            build_output = _destroy_container(job_uuid, build_output)
            build_output = _destroy_image(job_uuid, build_output)

            if build_output and cmd_output:
                _make_patch_request(
                    job_uuid, {
                        "build_output": build_output,
                        "cmd_output": cmd_output,
                        "status": JOB_STATUSES['FAILED'],
                        "finished_at": datetime.datetime.now(),
                        "cost": 0.0  # Failed jobs are free
                    }, config.token)
