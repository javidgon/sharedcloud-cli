import os
import random
import re

from click.testing import CliRunner

from sharedcloud import cli1, _read_token, function, run, instance, job, account


def _accountSetUp():
    email, username, password = TestUtils.generate_credentials()

    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    return email, username, password, account_uuid

def _accountWithSpecialPowersSetUp(user_id):
    _, username, password = TestUtils.generate_credentials()
    email = 'runs_master{}@example.com'.format(user_id)
    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    return email, username, password, account_uuid

def _accountTearDown(account_uuid):
    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output


class Config():
    def __init__(self, token):
        self.token = token


class TestUtils:
    runner = CliRunner()

    @staticmethod
    def extract_uuid(output):
        return re.findall(r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})", output)[0]

    # Account
    @classmethod
    def create_account(
            cls,
            email=None,
            username=None,
            password=None):
        config = Config(token=_read_token())
        args = ['create']

        if email:
            args.append('--email')
            args.append(email)
        if username:
            args.append('--username')
            args.append(username)
        if password:
            args.append('--password')
            args.append(password)

        return cls.runner.invoke(account, args, obj=config)

    @classmethod
    def update_account(cls,
                        uuid=None,
                        email=None,
                        username=None,
                        password=None):
        config = Config(token=_read_token())
        args = ['update']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        if email:
            args.append('--email')
            args.append(email)
        if username:
            args.append('--username')
            args.append(username)
        if password:
            args.append('--password')
            args.append(password)

        return cls.runner.invoke(account, args, obj=config)

    @classmethod
    def delete_account(cls, uuid=None):
        config = Config(token=_read_token())
        args = ['delete']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        return cls.runner.invoke(account, args, obj=config)

    @classmethod
    def list_account(cls):
        config = Config(token=_read_token())
        return cls.runner.invoke(account, [
            'list',
        ], obj=config)

    @classmethod
    def check_account_output(
            cls,
            expected_email=None,
            expected_username=None,
            expected_balance_is_zero=None
    ):

        columns = ['UUID', 'EMAIL', 'USERNAME', 'BALANCE', 'DATE_JOINED', 'LAST_LOGIN']
        r = cls.list_account()
        assert r.exit_code == 0
        for column in columns:
            assert column in r.output

        rows = r.output.split('\n')[2:-1]
        num_rows = len(rows)

        for idx, row in enumerate(rows):
            inverse_idx = num_rows - (idx + 1)
            fields = [field for field in row.split('  ') if field]

            if expected_email:
                assert expected_email[inverse_idx] in fields[columns.index('EMAIL')]

            if expected_username:
                assert expected_username[inverse_idx] in fields[columns.index('USERNAME')]

            if expected_balance_is_zero:
                assert fields[columns.index('BALANCE')] == '$0.0'
            else:
                assert fields[columns.index('BALANCE')] != '$0.0'

        return r

    @classmethod
    def login(
            cls,
            username=None,
            password=None
    ):
        args = ['login']

        if username:
            args.append('--username')
            args.append(username)
        if password:
            args.append('--password')
            args.append(password)

        return cls.runner.invoke(cli1, args)


    @classmethod
    def logout(cls):
        return cls.runner.invoke(cli1, ['logout'])

    @classmethod
    def list_functions(cls):
        config = Config(token=_read_token())
        return cls.runner.invoke(function, [
            'list',
        ], obj=config)

    @classmethod
    def check_list_functions_output(
            cls,
            expected_uuid=None,
            expected_name=None,
            expected_runtime=None,
            expected_num_runs=None,
            expected_num_functions=None
    ):
        columns = ['UUID', 'NAME', 'RUNTIME', 'NUM_RUNS', 'WHEN']
        r = cls.list_functions()
        assert r.exit_code == 0
        for column in columns:
            assert column in r.output

        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them

        num_rows = len(rows)

        if expected_num_functions:
            assert num_rows == expected_num_functions

        # Due to the inverse order (last resources are displayed in the first positions of the list),
        # we check the expectations in the opposite order
        for idx, row in enumerate(rows):
            inverse_idx = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_uuid:
                assert expected_uuid[inverse_idx] in  fields[columns.index('UUID')]

            if expected_name:
                assert expected_name[inverse_idx] in  fields[columns.index('NAME')]

            if expected_runtime:
                assert expected_runtime[inverse_idx] in fields[columns.index('RUNTIME')]

            if expected_num_runs:
                assert expected_num_runs[inverse_idx] in fields[columns.index('NUM_RUNS')]

        return r

    # Functions
    @classmethod
    def create_function(
            cls,
            name=None,
            runtime=None,
            code=None,
            file=None):
        config = Config(token=_read_token())
        args = ['create']

        if name:
            args.append('--name')
            args.append(name)
        if runtime:
            args.append('--runtime')
            args.append(runtime)
        if code:
            args.append('--code')
            args.append(code)
        if file:
            args.append('--file')
            args.append(file)
        return cls.runner.invoke(function, args, obj=config)

    @classmethod
    def update_function(cls,
                        uuid=None,
                        name=None,
                        runtime=None,
                        code=None,
                        file=None):
        config = Config(token=_read_token())
        args = ['update']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        if name:
            args.append('--name')
            args.append(name)
        if runtime:
            args.append('--runtime')
            args.append(runtime)
        if code:
            args.append('--code')
            args.append(code)
        if file:
            args.append('--file')
            args.append(file)
        return cls.runner.invoke(function, args, obj=config)

    @classmethod
    def delete_function(cls, uuid=None):
        config = Config(token=_read_token())
        args = ['delete']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        return cls.runner.invoke(function, args, obj=config)

    @classmethod
    def get_code_for_function(cls, uuid):
        config = Config(token=_read_token())
        args = ['code']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(function, args, obj=config)

    # Runs
    @classmethod
    def list_runs(cls):
        config = Config(token=_read_token())
        return cls.runner.invoke(run, [
            'list',
        ], obj=config)

    @classmethod
    def check_list_runs_output(cls,
                  expected_uuid=None,
                  expected_parameters=None,
                  expected_function_name=None,
                  expected_num_runs=None
    ):
        columns = ['UUID', 'PARAMETERS', 'WHEN', 'FUNCTION_NAME']
        r = cls.list_runs()
        assert r.exit_code == 0
        for column in columns:
            assert column in r.output

        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them

        num_rows = len(rows)

        if expected_num_runs:
            assert num_rows == expected_num_runs

        for idx, row in enumerate(rows):
            inverse_order = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_uuid:
                assert expected_uuid[inverse_order] in fields[columns.index('UUID')]

            if expected_parameters:
                assert expected_parameters[inverse_order] in fields[columns.index('PARAMETERS')]

            if expected_function_name:
                assert expected_function_name[inverse_order] in fields[columns.index('FUNCTION_NAME')]

        return r

    @classmethod
    def create_run(
            cls,
            function_uuid=None,
            parameters=None):
        config = Config(token=_read_token())
        args =['create']

        if function_uuid:
            args.append('--function_uuid')
            args.append(function_uuid)
        if parameters:
            args.append('--parameters')
            args.append(parameters)

        return cls.runner.invoke(run, args, obj=config)

    @classmethod
    def delete_run(cls, uuid=None):
        config = Config(token=_read_token())
        args = ['delete']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(run, args, obj=config)

    # Jobs
    @classmethod
    def list_jobs(cls):
        config = Config(token=_read_token())
        return cls.runner.invoke(job, [
            'list',
        ], obj=config)

    @classmethod
    def get_logs_for_job(cls, uuid):
        config = Config(token=_read_token())
        args = ['logs']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(job, args, obj=config)

    @classmethod
    def get_result_for_job(cls, uuid):
        config = Config(token=_read_token())
        args = ['result']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(job, args, obj=config)

    @classmethod
    def get_stdout_for_job(cls, uuid):
        config = Config(token=_read_token())
        args = ['stdout']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(job, args, obj=config)

    @classmethod
    def check_list_jobs_output(cls,
                  expected_status=None,
                  expected_num_jobs=None,
    ):
        columns = ['UUID', 'ID', 'STATUS', 'COST', 'DURATION', 'WHEN', 'RUN_UUID', 'FUNCTION_NAME']
        r = cls.list_jobs()
        assert r.exit_code == 0
        for column in columns:
            assert column in r.output

        job_uuids = []
        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them
        num_rows = len(rows)
        if expected_num_jobs:
            assert num_rows == expected_num_jobs

        for idx, row in enumerate(rows):
            job_uuids.append(cls.extract_uuid(row))
            inverse_order = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_status:
                assert expected_status[inverse_order] in fields[columns.index('STATUS')]

        return r, job_uuids

    # Instances
    @classmethod
    def check_list_instances_output(cls,
                       expected_uuid=None,
                       expected_name=None,
                       expected_status=None,
                       expected_price_per_hour=None,
                       expected_num_running_jobs=None,
                       expected_max_num_parallel_jobs=None,
                       expected_num_instances=None):
        config = Config(token=_read_token())
        columns = ['UUID', 'NAME', 'STATUS', 'PRICE_PER_HOUR', 'NUM_RUNNING_JOBS', 'MAX_NUM_PARALLEL_JOBS' ,'LAST_CONNECTION']
        r = cls.runner.invoke(instance, [
            'list',
        ], obj=config)
        assert r.exit_code == 0
        for column in columns:
            assert column in r.output

        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them

        num_rows = len(rows)

        if expected_num_instances:
            assert num_rows == expected_num_instances

        for idx, row in enumerate(rows):
            inverse_order = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_uuid:
                assert expected_uuid[inverse_order] in fields[columns.index('UUID')]

            if expected_name:
                assert expected_name[inverse_order] in fields[columns.index('NAME')]

            if expected_status:
                assert expected_status[inverse_order] in fields[columns.index('STATUS')]

            if expected_price_per_hour:
                assert expected_price_per_hour[inverse_order] in fields[columns.index('PRICE_PER_HOUR')]

            if expected_num_running_jobs:
                assert expected_num_running_jobs[inverse_order] in fields[columns.index('NUM_RUNNING_JOBS')]

            if expected_max_num_parallel_jobs:
                assert expected_max_num_parallel_jobs[inverse_order] in fields[columns.index('MAX_NUM_PARALLEL_JOBS')]

        return r

    @classmethod
    def create_instance(
            cls,
            name=None,
            price_per_hour=None,
            max_num_parallel_jobs=None):
        config = Config(token=_read_token())
        args =['create']

        if name:
            args.append('--name')
            args.append(name)
        if price_per_hour:
            args.append('--price_per_hour')
            args.append(price_per_hour)
        if max_num_parallel_jobs:
            args.append('--max_num_parallel_jobs')
            args.append(max_num_parallel_jobs)
        return cls.runner.invoke(instance, args, obj=config)

    @classmethod
    def update_instance(
            cls,
            uuid=None,
            name=None,
            price_per_hour=None,
            max_num_parallel_jobs=None):
        config = Config(token=_read_token())
        args = ['update']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        if name:
            args.append('--name')
            args.append(name)
        if price_per_hour:
            args.append('--price_per_hour')
            args.append(price_per_hour)
        if max_num_parallel_jobs:
            args.append('--max_num_parallel_jobs')
            args.append(max_num_parallel_jobs)
        return cls.runner.invoke(instance, args, obj=config)

    @classmethod
    def delete_instance(cls, uuid=None):
        config = Config(token=_read_token())
        args = ['delete']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        return cls.runner.invoke(instance, args, obj=config)

    @classmethod
    def start_instance(cls, uuid=None, job_timeout=None):
        config = Config(token=_read_token())
        args =['start']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        if job_timeout:
            args.append('--job_timeout')
            args.append(job_timeout)
        return cls.runner.invoke(instance, args, obj=config)

    @classmethod
    def read_file(cls, filepath):
        output = None
        with open(filepath, 'r') as f:
            output = f.read()
        return output

    @classmethod
    def generate_random_seed(cls):
        return str(random.randint(1, 10000000))

    @classmethod
    def generate_credentials(cls):
        seed = cls.generate_random_seed()
        username = '{}'.format(seed)
        email = '{}@example.com'.format(seed)
        password = '{}blablabla'.format(seed)

        return email, username, password