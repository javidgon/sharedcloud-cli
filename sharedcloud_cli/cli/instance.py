import multiprocessing
import os
import subprocess
import time

import click
import requests
from click import pass_obj

from sharedcloud_cli.constants import SHAREDCLOUD_CLI_URL, INSTANCE_TYPES, SHAREDCLOUD_CLI_INSTANCE_CONFIG_FILENAME, \
    JOB_STATUSES
from sharedcloud_cli.mappers import _map_instance_status_to_human_representation, _map_instance_type_to_human_readable, \
    _map_datetime_obj_to_human_representation
from sharedcloud_cli.utils import _exit_if_user_is_logged_out, _create_resource, _list_resource, _update_resource, \
    _delete_resource, _update_image, _get_instance_token_or_exit_if_there_is_none, _perform_instance_action, \
    _update_all_images, _get_jobs


@click.group(help='List, create and modify your instances')
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
            r = _get_jobs(instance_uuid, config.token)

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
