import click
import requests
import os
import json
import time
from subprocess import Popen


BASE_URL = 'http://localhost:8000'
CONFIG_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))
CONFIG_FILE = '{}/config'.format(CONFIG_FOLDER)


class Config(object):

    def __init__(self):
        self.token = None

pass_config = click.make_pass_decorator(Config, ensure=True)

def _read_token():
    token = None
    with open(CONFIG_FILE, 'r') as f:
        token = f.read()
    return token

@click.group()
@pass_config
def cli1(config):
    config.token = _read_token()

    # If Config folder doesn't exist, we create it
    if not os.path.exists(CONFIG_FOLDER):
        os.makedirs(CONFIG_FOLDER)


@cli1.command(help='Login into the System')
@click.argument('username', required=True)
@click.argument('password', required=True)
def login(username, password):
    # sharedcloud login username password
    r = requests.post('{}/api-token-auth/'.format(BASE_URL), data={
        'username': username,
        'password': password
    })

    content = json.loads(r.content)
    if r.status_code == 200:
        with open(CONFIG_FILE, 'w+') as f:
            f.write(content.get('token'))

        print('Successfully logged in :)')
    else:
        print(content)


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
    content = json.loads(r.content)

    if r.status_code == 201:
        print('Task {} was created!'.format(content.get('uuid')))
    else:
        print(content)


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
    import pdb; pdb.set_trace()
    content = json.loads(r.content)
    if r.status_code == 201:
        print('Run {} is running!'.format(content.get('uuid')))
    else:
        print(content)


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
    content = json.loads(r.content)

    if r.status_code == 201:
        print('Instance {} was registered!'.format(content.get('uuid')))
    else:
        print(content)


@cli1.command(help='Starts a new Instance')
@click.option('--instance', required=True)
@pass_config
def start_instance(config, instance):
    # sharedcloud start_instance --instance <uuid>
    if not config.token:
        print('Please log in first')
        return

    try:
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)

        r = requests.put('{}/instances/{}/start/'.format(BASE_URL, instance),
                         data={}, headers={'Authorization': 'Token {}'.format(config.token)})
        print('Instance started! It will sync each 10 seconds')
        r = requests.put('{}/instances/{}/ping/'.format(BASE_URL, instance),
                         data={}, headers={'Authorization': 'Token {}'.format(config.token)})
        content = json.loads(r.content)
        if r.status_code == 200:
            jobs = json.loads(r.content)
            for job in jobs:
                job_uuid = job.get('job_uuid')
                job_folder = CONFIG_FOLDER + '/{}'.format(job_uuid)
                if not os.path.exists(job_folder):
                    os.makedirs(job_folder)

                with open('{}/Dockerfile'.format(job_folder), 'w') as text_file:
                    dockerfile = job.get('dockerfile')
                    text_file.write(dockerfile)

                with open('{}/file.py'.format(job_folder), 'w') as text_file:
                    code = job.get('code')
                    text_file.write(code)
                docker_build = Popen(
                    ['docker', 'build','-t', '{}:latest'.format(job_uuid),
                     '-f', '{}/{}/Dockerfile'.format(CONFIG_FOLDER, job_uuid), job_folder])
                docker_run = Popen(
                    ['docker', 'run','{}:latest'.format(job_uuid)])
                import pdb; pdb.set_trace()
                # Save log into remote

                # Destroy container

                # Destroy image

        else:
            print(content)
    except KeyboardInterrupt:
        print('Instance stopped!')
        requests.put('{}/instances/{}/stop/'.format(BASE_URL, instance),
                     data={}, headers={'Authorization': 'Token {}'.format(config.token)})


#cli = click.CommandCollection(sources=[cli1])
#
# if __name__ == '__main__':
#     cli()