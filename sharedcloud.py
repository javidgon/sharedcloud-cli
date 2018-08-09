import click
import requests
import os
import json
import time
from subprocess import Popen


BASE_URL = 'http://localhost:8000'
CONFIG_FOLDER = '{}/.sharedcloud'.format(os.path.expanduser('~'))
CONFIG_FILE = '{}/config'.format(CONFIG_FOLDER)

def _read_token():
    token = None
    with open(CONFIG_FILE, 'r') as f:
        token = f.read()
    return token

@click.group()
def cli1():
    pass

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
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)

        with open(CONFIG_FILE, 'w+') as f:
            f.write(content.get('token'))

        print('Successfully logged in :)')
    else:
        print(content)


@cli1.command(help='Creates a new Task')
@click.option('--name', required=True)
@click.option('--dockerfile', required=True)
def create_task(name, dockerfile):
    # sharedcloud create_task --name mything --dockerfile blabla/Dockerfile_python
    token = _read_token()
    r = requests.post('{}/tasks/'.format(BASE_URL), data={
        'name': name
    }, files={
        'dockerfile': open(dockerfile, 'r')
    }, headers={'Authorization':'Token {}'.format(token)})
    content = json.loads(r.content)

    if r.status_code == 201:
        print('Task {} was created!'.format(content.get('uuid')))
    else:
        print(content)


@cli1.command(help='Creates a new Run')
@click.option('--task', required=True)
@click.option('--num_jobs', required=True)
def create_run(task, num_jobs):
    # sharedcloud create_run --task <uuid> --num_jobs 3
    token = _read_token()
    r = requests.post('{}/runs/'.format(BASE_URL), data={
        'task': task,
        'num_jobs': num_jobs
    }, headers={'Authorization':'Token {}'.format(token)})
    content = json.loads(r.content)

    if r.status_code == 201:
        print('Run {} is running!'.format(content.get('uuid')))
    else:
        print(content)


@cli1.command(help='Registers a new Instance')
@click.option('--name', required=True)
@click.option('--price_per_hour', required=True)
@click.option('--max_num_jobs', required=True)
def register_instance(name, price_per_hour, max_num_jobs):
    # sharedcloud register_instance --name blabla --price_per_hour 2.0 --max_num_jobs 3

    token = _read_token()
    r = requests.post('{}/instances/'.format(BASE_URL), data={
        'name': name,
        'price_per_hour': price_per_hour,
        'max_num_jobs': max_num_jobs,
    }, headers={'Authorization':'Token {}'.format(token)})
    content = json.loads(r.content)

    if r.status_code == 201:
        print('Instance {} was registered!'.format(content.get('uuid')))
    else:
        print(content)


@cli1.command(help='Starts a new Instance')
@click.option('--instance', required=True)
def start_instance(instance):
    # sharedcloud start_instance --instance <uuid>

    token = _read_token()
    try:
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER)

        r = requests.put('{}/instances/{}/start/'.format(BASE_URL, instance),
                         data={}, headers={'Authorization': 'Token {}'.format(token)})
        print('Instance started! It will sync each 10 seconds')
        while True:
            r = requests.put('{}/instances/{}/ping/'.format(BASE_URL, instance),
                             data={}, headers={'Authorization': 'Token {}'.format(token)})
            jobs = json.loads(r.content)
            for job in jobs:
                dockerfile = job.get('dockerfile')
                p = Popen(['docker', 'build', '-t', 'test:latest'])  # something long running
            print(r.content)
            time.sleep(10)
    except KeyboardInterrupt:
        print('Instance stopped!')
        requests.put('{}/instances/{}/stop/'.format(BASE_URL, instance),
                     data={}, headers={'Authorization': 'Token {}'.format(token)})


cli = click.CommandCollection(sources=[cli1])

if __name__ == '__main__':
    cli()