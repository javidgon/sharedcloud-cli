import click
import datetime
import requests
import os
import time
import shutil
from subprocess import check_output, CalledProcessError


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
    def _make_put_request(action, instance_uuid, token):
        r = requests.put('{}/instances/{}/{}/'.format(BASE_URL, instance_uuid, action),
                         data={}, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code != 200:
            raise Exception(r.content)
        return r

    def _make_patch_request(job_uuid, data, token):
        r = requests.patch('{}/jobs/{}/'.format(BASE_URL, job_uuid),
                           data=data, headers={'Authorization': 'Token {}'.format(token)})
        if r.status_code != 200:
            raise Exception('The remote could not be updated. Please try later.')
        return r

    def _create_file_from_data(data, to_file):
        with open(to_file, 'w') as text_file:
            text_file.write(data)

    def _generate_image(job_uuid, job_folder):
        output = b''
        image_tag = job_uuid

        docker_build = check_output(
            ['docker', 'build', '-t', '{}:latest'.format(image_tag),
             '-f', '{}/{}/Dockerfile'.format(CONFIG_FOLDER, job_uuid), job_folder])
        for line in docker_build.splitlines():
            output += line + b'\n'
        return image_tag, output

    def _run_container(image_tag):
        result = b''
        container_tag = image_tag

        try:
            docker_run = check_output(
                ['docker', 'run', '--memory=512m', '--cpus=1', '--name', container_tag, '{}:latest'.format(image_tag)])
            for line in docker_run.splitlines():
                result += line + b'\n'
        except CalledProcessError as grepexc:
            # When it exists due to a timeout we don't exit the cli as it's kind of an expected error
            if grepexc.returncode != 124:
                raise
        return container_tag, result

    def _destroy_container(container_tag, output):
        docker_destroy_container = check_output(
            ['docker', 'rm', container_tag, '--force'])
        for line in docker_destroy_container.splitlines():
            output += line + b'\n'

        return output

    def _destroy_image(image_tag, output):
        docker_destroy_image = check_output(
            ['docker', 'rmi', image_tag, '--force'])
        for line in docker_destroy_image.splitlines():
            output += line + b'\n'

        return output

    JOB_STATUS_WAITING = 1
    JOB_STATUS_IN_PROGRESS = 2
    JOB_STATUS_FINISHED = 3

    # sharedcloud start_instance --instance <uuid>
    if not config.token:
        print('Please log in first')
        return

    job_uuid = None
    output = b''
    result = b''

    try:
        # First, we let our remote know that we are starting the instance
        _make_put_request('start', instance, config.token)

        # Second, we are going to ask the remote, each x seconds, if they have new jobs for us
        while True:
            r = _make_put_request('ping', instance, config.token)

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
                        "status": JOB_STATUS_IN_PROGRESS,
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
                image_tag, output = _generate_image(job_uuid, job_folder)
                # After the image has been generated, we run our container and calculate our result
                container_tag, result = _run_container(image_tag)

                # After this has been done, we make sure to clean up the image, container and job folder
                output = _destroy_container(container_tag, output)
                output = _destroy_image(image_tag, output)
                shutil.rmtree(job_folder)

                # Finally, we let our remote know that job's stats
                _make_patch_request(
                    job_uuid, {
                        "log_output": output,
                        "result": result,
                        "status": JOB_STATUS_FINISHED,
                        "finished_at": datetime.datetime.now(),
                        "cost": round(
                            int((datetime.datetime.now()-job_started_at).total_seconds()) * (instance_price_per_hour/3600), 3)
                    }, config.token)

            if num_jobs > 0:
                print('All jobs were completed!')

            # We wait 60 seconds until the next check
            time.sleep(60)

    except Exception as e:
        # If the error was provoked by a job, we update our remote with the output
        if job_uuid and output and result:
            _make_patch_request(
                job_uuid, {
                    "log_output": output,
                    "result": result,
                    "status": JOB_STATUS_FINISHED,
                    "finished_at": datetime.datetime.now(),
                    "cost": 0.0 # Failed jobs are free
                    }, config.token)

        print(e)
        print('Instance stopped!')
        _make_put_request('stop', instance, config.token)
