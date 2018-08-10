import click
import datetime
import requests
import os
import time
import shutil
from subprocess import check_output


BASE_URL = os.environ['BASE_URL']
CONFIG_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))
CONFIG_FILE = '{}/config'.format(CONFIG_FOLDER)


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
    # If Config folder doesn't exist, we create it
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)

    config.token = _read_token()


@cli1.command(help='Login into the System')
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


@cli1.command(help='Creates a new Task')
@click.option('--name', required=True)
@click.option('--language', required=True)
@click.option('--code', required=True)
@pass_config
def create_task(config, name, language, code):
    # sharedcloud create_task --name mything --language python --code "print('Hello')"
    # Future: sharedcloud create_task --name mything2 --language python --file "myfile.py" --cmd "python myfile.py"
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


@cli1.command(help='Creates a new Run')
@click.option('--task', required=True)
@click.option('--num_jobs', required=True)
@pass_config
def create_run(config, task, num_jobs):
    # sharedcloud create_run --task <uuid> --num_jobs 3
    if not config.token:
        print('Please log in first')
        return

    r = requests.post('{}/runs/'.format(BASE_URL), data={
        'task': task,
        'num_jobs': num_jobs
    }, headers={'Authorization':'Token {}'.format(config.token)})
    if r.status_code == 201:
        result = r.json()
        print('Run {} is running!'.format(result.get('uuid')))
    else:
        print(r.content)


@cli1.command(help='Registers a new Instance')
@click.option('--name', required=True)
@click.option('--price_per_hour', required=True)
@click.option('--max_num_jobs', required=True)
@pass_config
def register_instance(config, name, price_per_hour, max_num_jobs):
    # sharedcloud register_instance --name blabla --price_per_hour 2.0 --max_num_jobs 3
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


@cli1.command(help='Starts a new Instance')
@click.option('--instance', required=True)
@pass_config
def start_instance(config, instance):
    # sharedcloud start_instance --instance <uuid>
    if not config.token:
        print('Please log in first')
        return

    try:
        r = requests.put('{}/instances/{}/start/'.format(BASE_URL, instance),
                         data={}, headers={'Authorization': 'Token {}'.format(config.token)})

        while True:
            r = requests.put('{}/instances/{}/ping/'.format(BASE_URL, instance),
                             data={}, headers={'Authorization': 'Token {}'.format(config.token)})
            if r.status_code == 200:
                jobs = r.json()
                if len(jobs) > 0:
                    print('{} job/s arrived, please be patient...'.format(len(jobs)))
                for job in jobs:
                    job_uuid = job.get('job_uuid')
                    job_started_at = datetime.datetime.now()
                    instance_price_per_hour = job.get('instance_price_per_hour')
                    job_folder = CONFIG_FOLDER + '/{}'.format(job_uuid)
                    if not os.path.exists(job_folder):
                        os.makedirs(job_folder)
                    r = requests.patch('{}/jobs/{}/'.format(BASE_URL, job_uuid),
                        data={
                            "status": 2,
                            "started_at": job_started_at
                        }, headers={'Authorization': 'Token {}'.format(config.token)})
                    if r.status_code != 200:
                        raise Exception('The remote could not be updated. Please try later.')

                    with open('{}/Dockerfile'.format(job_folder), 'w') as text_file:
                        dockerfile = job.get('dockerfile')
                        text_file.write(dockerfile)

                    with open('{}/file.py'.format(job_folder), 'w') as text_file:
                        code = job.get('code')
                        text_file.write(code)

                    output = b''
                    result = b''

                    docker_build = check_output(
                        ['docker', 'build','-t', '{}:latest'.format(job_uuid),
                         '-f', '{}/{}/Dockerfile'.format(CONFIG_FOLDER, job_uuid), job_folder])
                    for line in docker_build.splitlines():
                        output += line + b'\n'

                    docker_run = check_output(
                        ['docker', 'run', '--name', job_uuid, '{}:latest'.format(job_uuid)])
                    for line in docker_run.splitlines():
                        result += line + b'\n'

                   # Destroy container
                    docker_destroy_container = check_output(
                        ['docker', 'rm', job_uuid, '--force'])
                    for line in docker_destroy_container.splitlines():
                        output += line + b'\n'

                    # Destroy image
                    docker_destroy_image = check_output(
                        ['docker', 'rmi', job_uuid, '--force'])
                    for line in docker_destroy_image.splitlines():
                        output += line + b'\n'

                    # Save details into remote
                    r = requests.patch('{}/jobs/{}/'.format(BASE_URL, job_uuid),
                        data={
                            "log_output": output,
                            "result": result,
                            "status": 3,
                            "finished_at": datetime.datetime.now(),
                            "cost": round(
                                int((datetime.datetime.now()-job_started_at).total_seconds()) * (instance_price_per_hour/3600), 3)
                        }, headers={'Authorization': 'Token {}'.format(config.token)})
                    if r.status_code != 200:
                        raise Exception('The remote could not be updated. Please try later.')
                    # Remove local folder
                    shutil.rmtree('{}/{}'.format(CONFIG_FOLDER, job_uuid))

                if len(jobs) > 0:
                    print('All jobs were completed!')
            else:
                print(r.content)

            time.sleep(60)
    except KeyboardInterrupt:
        print('Instance stopped!')
        requests.put('{}/instances/{}/stop/'.format(BASE_URL, instance),
                     data={}, headers={'Authorization': 'Token {}'.format(config.token)})

