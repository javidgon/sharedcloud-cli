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

class ObjectNotFoundException(Exception):
    pass


now = datetime.datetime.now()

class Config(object):

    def __init__(self):
        self.token = None

pass_config = click.make_pass_decorator(Config, ensure=True)

def _read_token():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r') as f:
        token = f.read()
    return token

@click.group()
@pass_config
def cli1(config):
    # We check whether docker is installed
    try:
        check_output(
            ['docker', 'ps'])
    except CalledProcessError as pgrepexc:
        exit('Is the Docker daemon running in your machine?')

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

        print('Successfully logged in :)')
    else:
        print(r.content)

@cli1.group(help='Create/Delete/List Tasks')
@pass_config
def task(config):
    pass


@task.command(help='Creates a new Task')
@click.option('--name', required=True)
@click.option('--language', required=True)
@click.option('--code', required=True)
@pass_config
def create(config, name, language, code):
    # sharedcloud task create --name mything --language python --code "print('Hello')"
    if not config.token:
        print('Please log in first')
        return

    r = requests.post('{}/tasks/'.format(BASE_URL), data={
        'name': name,
        'language': language,
        'code': code
    }, headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 201:
        result = r.json()
        print('Task {} was created!'.format(result.get('uuid')))
    else:
        print(r.content)


@task.command(help='List Tasks')
@pass_config
def list(config):
    # sharedcloud task list"
    if not config.token:
        print('Please log in first')
        return

    r = requests.get('{}/tasks/'.format(BASE_URL),
                     headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 200:
        tasks = r.json()

        click.echo(tabulate([[
            task.get('uuid'),
            task.get('name'),
            task.get('programming_language'),
            timeago.format(datetime.datetime.strptime(task.get('created_at'), DATETIME_FORMAT), now),
        ] for task in tasks], headers=['UUID', 'NAME', 'LANGUAGE', 'CREATED']))
    else:
        print(r.content)


@task.command(help='Deletes a Task')
@click.option('--uuid', required=True)
@pass_config
def delete(config, uuid):
    # sharedcloud task delete --uuid <uuid>
    if not config.token:
        print('Please log in first')
        return
    r = requests.delete('{}/tasks/{}/'.format(BASE_URL, uuid),
                        headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 204:
        print('Task {} was deleted!'.format(uuid))
    elif r.status_code == 404:
        print('Not found Task with UUID {}'.format(uuid))
    else:
        print(r.content)


@cli1.group(help='Create/List Runs')
@pass_config
def run(config):
    pass


@run.command(help='Creates a new Run')
@click.option('--task_uuid', required=True)
@click.option('--parameters', required=True)
@pass_config
def create(config, task_uuid, parameters):
    # sharedcloud run create --task_uuid <uuid> --parameters "((1, 2, 3), (4, 5, 6))"
    if not config.token:
        print('Please log in first')
        return

    r = requests.post('{}/runs/'.format(BASE_URL), data={
        'task': task_uuid,
        'parameters': parameters
    }, headers={'Authorization':'Token {}'.format(config.token)})
    if r.status_code == 201:
        result = r.json()
        print('Run {} is running!'.format(result.get('uuid')))
    else:
        print(r.content)


@run.command(help='List Runs')
@pass_config
def list(config):
    # sharedcloud task list"
    if not config.token:
        print('Please log in first')
        return

    r = requests.get('{}/runs/'.format(BASE_URL),
                     headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 200:
        runs = r.json()

        click.echo(tabulate([[
            run.get('uuid'),
            run.get('parameters'),
            timeago.format(datetime.datetime.strptime(run.get('created_at'), DATETIME_FORMAT), now),
            run.get('task')
        ] for run in runs], headers=['UUID', 'PARAMETERS', 'CREATED', 'TASK_UUID']))
    else:
        print(r.content)


@cli1.group(help='List Jobs')
@pass_config
def job(config):
    pass

@job.command(help='List Jobs')
@pass_config
def list(config):
    def _map_status_to_description(status_id):
        for status_name, id in JOB_STATUSES.items():
            if id == status_id:
                return status_name

    # sharedcloud task list"
    if not config.token:
        print('Please log in first')
        return

    r = requests.get('{}/jobs/'.format(BASE_URL),
                     headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 200:
        jobs = r.json()

        click.echo(tabulate([[
            job.get('uuid'),
            job.get('incremental_id'),
            _map_status_to_description(job.get('status')),
            job.get('cmd_output'),
            timeago.format(datetime.datetime.strptime(job.get('created_at'), DATETIME_FORMAT), now),
            job.get('run')
        ] for job in jobs], headers=['UUID', 'ID', 'STATUS', 'CMD_OUTPUT', 'CREATED', 'RUN_UUID']))
    else:
        print(r.content)

@cli1.group(help='Register/Start/List Instances')
@pass_config
def instance(config):
    pass


@instance.command(help='Registers a new Instance')
@click.option('--name', required=True)
@click.option('--price_per_hour', required=True)
@click.option('--max_num_jobs', required=True)
@pass_config
def register(config, name, price_per_hour, max_num_jobs):
    # sharedcloud instance register --name blabla --price_per_hour 2.0 --max_num_jobs 3
    if not config.token:
        print('Please log in first')
        return

    r = requests.post('{}/instances/'.format(BASE_URL), data={
        'name': name,
        'price_per_hour': price_per_hour,
        'max_num_jobs': max_num_jobs,
    }, headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 201:
        result = r.json()
        print('Instance {} was registered!'.format(result.get('uuid')))
    else:
        print(r.content)


@instance.command(help='Deletes an Instance')
@click.option('--uuid', required=True)
@pass_config
def delete(config, uuid):
    # sharedcloud instance delete --uuid <uuid>
    if not config.token:
        print('Please log in first')
        return

    r = requests.delete('{}/instances/{}/'.format(BASE_URL, uuid),
                        headers={'Authorization':'Token {}'.format(config.token)})

    if r.status_code == 204:
        print('Instance {} was deleted!'.format(uuid))
    elif r.status_code == 404:
        print('Not found Instance with UUID {}'.format(uuid))
    else:
        print(r.content)


@instance.command(help='Starts an Instance')
@click.option('--uuid', required=True)
@pass_config
def start(config, uuid):
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

    instance_uuid = uuid

    # sharedcloud instance start --uuid <uuid>
    if not config.token:
        print('Please log in first')
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
                print('{} job/s arrived, please be patient...'.format(num_jobs))

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
                            int((datetime.datetime.now()-job_started_at).total_seconds()) * (instance_price_per_hour/3600), 3)
                    }, config.token)

            if num_jobs > 0:
                print('All jobs were completed!')

            # We wait 60 seconds until the next check
            time.sleep(60)

    except ObjectNotFoundException as e:
        print('Not found Instance with this UUID')
    except Exception as e:
        print('Instance stopped!')
        _make_put_request('stop', instance_uuid, config.token)
        print(e)

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
                        "cost": 0.0 # Failed jobs are free
                        }, config.token)
