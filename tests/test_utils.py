import os
import re

from click.testing import CliRunner

from sharedcloud import cli1, _read_token, function, run, instance, job


class Config():
    def __init__(self, token):
        self.token = token


class TestUtils:
    runner = CliRunner()

    @staticmethod
    def extract_uuid(output):
        return re.findall(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", output)[0]

    @classmethod
    def login(
            cls,
            username=os.environ.get('SHAREDCLOUD_USERNAME', 'superuser'),
            password=os.environ.get('SHAREDCLOUD_PASSWORD', 'password')):
        r = cls.runner.invoke(cli1, ['login', username, password])
        assert r.exit_code == 0
        return r

    @classmethod
    def logout(cls):
        r = cls.runner.invoke(cli1, ['logout'])
        assert r.exit_code == 0
        return r

    @classmethod
    def list_functions(cls):
        config = Config(token=_read_token())
        keywords = ['UUID', 'NAME', 'RUNTIME', 'CODE', 'CREATED']
        r = cls.runner.invoke(function, [
            'list',
        ], obj=config)
        assert r.exit_code == 0
        for keyword in keywords:
            assert keyword in r.output

        return r

    # Functions
    @classmethod
    def create_function(
            cls,
            name='example',
            runtime='python36',
            code='def handler(event): print(2)',
            file=None):
        config = Config(token=_read_token())
        if code:
            args = [
                'create',
                '--name',
                name,
                '--runtime',
                runtime,
                '--code',
                code
            ]
        else:
            args = [
                'create',
                '--name',
                name,
                '--runtime',
                runtime,
                '--file',
                file
            ]
        r = cls.runner.invoke(function, args, obj=config)
        assert r.exit_code == 0
        assert 'has been created' in r.output

        return r, cls.extract_uuid(r.output)

    @classmethod
    def update_function(cls,
                        uuid=None,
                        name='example',
                        runtime='python36',
                        code='def handler(event): print(2)',
                        file=None):
        config = Config(token=_read_token())
        if code:
            args = [
                'update',
                '--uuid',
                uuid,
                '--name',
                name,
                '--runtime',
                runtime,
                '--code',
                code
            ]
        else:
            args = [
                'update',
                '--uuid',
                uuid,
                '--name',
                name,
                '--runtime',
                runtime,
                '--file',
                file
            ]
        r = cls.runner.invoke(function, args, obj=config)
        assert r.exit_code == 0
        assert 'was updated' in r.output

        return r, cls.extract_uuid(r.output)

    @classmethod
    def delete_function(cls, uuid=None):
        config = Config(token=_read_token())
        r = cls.runner.invoke(function, [
            'delete',
            '--uuid',
            uuid
        ], obj=config)
        assert r.exit_code == 0
        assert 'was deleted' in r.output

        return r, cls.extract_uuid(r.output)


    # Runs
    @classmethod
    def list_runs(cls):
        config = Config(token=_read_token())
        keywords = ['UUID', 'PARAMETERS', 'CREATED', 'FUNCTION_NAME']
        r = cls.runner.invoke(run, [
            'list',
        ], obj=config)
        assert r.exit_code == 0
        for keyword in keywords:
            assert keyword in r.output

        return r

    @classmethod
    def create_run(
            cls,
            function_uuid=None,
            parameters='((1, 2), (3, 4))'):
        config = Config(token=_read_token())

        r = cls.runner.invoke(run, [
            'create',
            '--function_uuid',
            function_uuid,
            '--parameters',
            parameters
        ], obj=config)
        assert r.exit_code == 0
        assert 'has been created' in r.output

        return r, cls.extract_uuid(r.output)

    @classmethod
    def delete_run(cls, uuid=None):
        config = Config(token=_read_token())
        r = cls.runner.invoke(run, [
            'delete',
            '--uuid',
            uuid
        ], obj=config)
        assert r.exit_code == 0
        assert 'was deleted' in r.output

        return r, cls.extract_uuid(r.output)


    # Jobs
    @classmethod
    def list_jobs(cls):
        config = Config(token=_read_token())
        keywords = ['UUID', 'ID', 'STATUS', 'FUNCTION_OUTPUT', 'FUNCTION_RESPONSE', 'COST', 'DURATION', 'CREATED', 'RUN_UUID', 'FUNCTION_NAME']
        r = cls.runner.invoke(job, [
            'list',
        ], obj=config)
        assert r.exit_code == 0
        for keyword in keywords:
            assert keyword in r.output

        return r


    # Instances
    @classmethod
    def list_instances(cls):
        config = Config(token=_read_token())
        keywords = ['UUID', 'NAME', 'STATUS', 'PRICE_PER_HOUR', 'NUM_RUNNING_JOBS', 'MAX_NUM_JOBS' ,'LAST_CONNECTION']
        r = cls.runner.invoke(instance, [
            'list',
        ], obj=config)
        assert r.exit_code == 0
        for keyword in keywords:
            assert keyword in r.output

        return r

    @classmethod
    def create_instance(
            cls,
            name='instance_name',
            price_per_hour=1.0,
            max_num_jobs=5):
        config = Config(token=_read_token())

        r = cls.runner.invoke(instance, [
            'create',
            '--name',
            name,
            '--price_per_hour',
            price_per_hour,
            '--max_num_jobs',
            max_num_jobs
        ], obj=config)
        assert r.exit_code == 0
        assert 'has been created' in r.output

        return r, cls.extract_uuid(r.output)

    @classmethod
    def update_instance(
            cls,
            name='instance_name',
            price_per_hour=1.0,
            max_num_jobs=5):
        config = Config(token=_read_token())

        r = cls.runner.invoke(instance, [
            'update',
            '--name',
            name,
            '--price_per_hour',
            price_per_hour,
            '--max_num_jobs',
            max_num_jobs
        ], obj=config)
        assert r.exit_code == 0
        assert 'was updated' in r.output

        return r, cls.extract_uuid(r.output)


    @classmethod
    def delete_instance(cls, uuid=None):
        config = Config(token=_read_token())
        r = cls.runner.invoke(instance, [
            'delete',
            '--uuid',
            uuid
        ], obj=config)
        assert r.exit_code == 0
        #assert 'was deleted' in r.output

        return r, cls.extract_uuid(r.output)

    @classmethod
    def start_instance(cls, uuid=None):
        config = Config(token=_read_token())
        r = cls.runner.invoke(instance, [
            'start',
            '--uuid',
            uuid
        ], obj=config)
        assert r.exit_code == 0
        assert 'Ready to take Jobs' in r.output

        return r, cls.extract_uuid(r.output)