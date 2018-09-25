import os
import random
import re
import uuid

from click.testing import CliRunner

from sharedcloud import cli1, _read_token, function, run, instance, job, account, image
from tests.constants import Message


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

    # Functions
    @classmethod
    def create_function(
            cls,
            name=None,
            image_uuid=None,
            code=None,
            file=None):
        config = Config(token=_read_token())
        args = ['create']

        if name:
            args.append('--name')
            args.append(name)
        if image_uuid:
            args.append('--image-uuid')
            args.append(image_uuid)
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
                        image_uuid=None,
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
        if image_uuid:
            args.append('--image-uuid')
            args.append(image_uuid)
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

    # Images

    @classmethod
    def update_all_images(cls):
        config = Config(token=_read_token())
        args = ['update_all']

        return cls.runner.invoke(image, args, obj=config)

    @classmethod
    def list_images(cls, only_downloaded=False):
        config = Config(token=_read_token())
        args = ['list']
        if only_downloaded:
            args.append('--only-downloaded')

        return cls.runner.invoke(image, args, obj=config)

    @classmethod
    def download_image(cls,
        registry_path=None):
        config = Config(token=_read_token())
        args = ['download']

        if registry_path:
            args.append('--registry-path')
            args.append(registry_path)

        return cls.runner.invoke(image, args, obj=config)

    @classmethod
    def clean_image(cls,
        registry_path=None):
        config = Config(token=_read_token())
        args = ['clean']

        if registry_path:
            args.append('--registry-path')
            args.append(registry_path)

        return cls.runner.invoke(image, args, obj=config)

    # Runs
    @classmethod
    def list_runs(cls):
        config = Config(token=_read_token())
        return cls.runner.invoke(run, [
            'list',
        ], obj=config)

    @classmethod
    def create_run(
            cls,
            function_uuid=None,
            parameters=None):
        config = Config(token=_read_token())
        args =['create']

        if function_uuid:
            args.append('--function-uuid')
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
    def get_stderr_for_job(cls, uuid):
        config = Config(token=_read_token())
        args = ['stderr']

        if uuid:
            args.append('--uuid')
            args.append(uuid)

        return cls.runner.invoke(job, args, obj=config)

    # Instances
    @classmethod
    def create_instance(
            cls,
            name=None,
            type=None,
            price_per_minute=None,
            max_num_parallel_jobs=None):
        config = Config(token=_read_token())
        args =['create']

        if name:
            args.append('--name')
            args.append(name)
        if type:
            args.append('--type')
            args.append(type)
        if price_per_minute:
            args.append('--price-per-minute')
            args.append(price_per_minute)
        if max_num_parallel_jobs:
            args.append('--max-num-parallel-jobs')
            args.append(max_num_parallel_jobs)
        return cls.runner.invoke(instance, args, obj=config)

    @classmethod
    def update_instance(
            cls,
            uuid=None,
            name=None,
            type=None,
            price_per_minute=None,
            max_num_parallel_jobs=None):
        config = Config(token=_read_token())
        args = ['update']

        if uuid:
            args.append('--uuid')
            args.append(uuid)
        if name:
            args.append('--name')
            args.append(name)
        if type:
            args.append('--type')
            args.append(type)
        if price_per_minute:
            args.append('--price-per-minute')
            args.append(price_per_minute)
        if max_num_parallel_jobs:
            args.append('--max-num-parallel-jobs')
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
    def start_instance(cls, job_timeout=None):
        config = Config(token=_read_token())
        args =['start']

        if job_timeout:
            args.append('--job-timeout')
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
    def generate_uuid(cls):
        return str(uuid.uuid4())

    @classmethod
    def generate_credentials(cls):
        seed = cls.generate_random_seed()
        username = '{}'.format(seed)
        email = '{}@example.com'.format(seed)
        password = '{}blablabla'.format(seed)

        return email, username, password


class TestWrapper:
    # Account
    @classmethod
    def create_beta_account_successfully(cls):
        _, username, password = TestUtils.generate_credentials()
        email = 'test_user_555{}@example.com'.format(TestUtils.generate_random_seed())

        r = TestUtils.create_account(email=email, username=username, password=password)
        assert r.exit_code == 0
        return TestUtils.extract_uuid(r.output), email, username, password

    @classmethod
    def create_account_successfully(cls):
        email, username, password = TestUtils.generate_credentials()

        r = TestUtils.create_account(email=email, username=username, password=password)
        assert r.exit_code == 0
        return TestUtils.extract_uuid(r.output), email, username, password

    @classmethod
    def create_account_unsuccessfully(cls, email=None, username=None, password=None, error_code=None, msg=None):
        r = TestUtils.create_account(email=email, username=username, password=password)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def update_account_successfully(cls, uuid=None, email=None, username=None, password=None):
        r = TestUtils.update_account(uuid=uuid, email=email, username=username, password=password)
        assert r.exit_code == 0
        assert Message.LOGOUT_SUCCEEDED in r.output

    @classmethod
    def update_account_unsuccessfully(
            cls, uuid=None, email=None, username=None, password=None, error_code=None, msg=None):
        r = TestUtils.update_account(uuid=uuid, email=email, username=username, password=password)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def delete_account_successfully(cls, uuid=None):
        r = TestUtils.delete_account(uuid=uuid)
        assert r.exit_code == 0

    @classmethod
    def delete_account_unsuccessfully(cls, uuid=None, error_code=None, msg=None):
        r = TestUtils.delete_account(uuid=uuid)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def check_account_output(
            cls,
            expected_email=None,
            expected_username=None,
            expected_balance_is_zero=None,
            expected_logout_warning=False
    ):

        columns = ['UUID', 'EMAIL', 'USERNAME', 'BALANCE', 'DATE_JOINED', 'LAST_LOGIN']
        r = TestUtils.list_account()
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
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
    def logout_successfully(cls):
        r = TestUtils.logout()
        assert r.exit_code == 0
        assert Message.LOGOUT_SUCCEEDED in r.output

    @classmethod
    def logout_unsuccessfully(cls):
        r = TestUtils.logout()
        assert r.exit_code == 1
        assert Message.ALREADY_LOGGED_OUT in r.output

    @classmethod
    def login_successfully(cls, username=None, password=None):
        r = TestUtils.login(username=username, password=password)
        assert r.exit_code == 0
        assert Message.LOGIN_SUCCEEDED in r.output

    @classmethod
    def login_unsuccessfully(cls, username=None, password=None, error_code=None, msg=None):
        r = TestUtils.login(username=username, password=password)
        assert r.exit_code == error_code
        assert msg in r.output


    # Function
    @classmethod
    def create_function_successfully(cls, image_uuid=None, code=None, file=None):
        name = TestUtils.generate_random_seed()
        r = TestUtils.create_function(name=name, image_uuid=image_uuid, code=code, file=file)
        assert r.exit_code == 0
        return TestUtils.extract_uuid(r.output), name

    @classmethod
    def create_function_unsuccessfully(cls, name=None, image_uuid=None, code=None, file=None, error_code=None, msg=None):
        r = TestUtils.create_function(name=name, image_uuid=image_uuid, code=code, file=file)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def update_function_successfully(cls, uuid=None, name=None, image_uuid=None, code=None, file=None):
        r = TestUtils.update_function(uuid=uuid, name=name, image_uuid=image_uuid, code=code, file=file)
        assert r.exit_code == 0

    @classmethod
    def update_function_unsuccessfully(cls, uuid=None, name=None, image_uuid=None, code=None, file=None, error_code=None, msg=None):
        r = TestUtils.update_function(uuid=uuid, name=name, image_uuid=image_uuid, code=code, file=file)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def delete_function_successfully(cls, uuid=None):
        r = TestUtils.delete_function(uuid=uuid)
        assert r.exit_code == 0

    @classmethod
    def delete_function_unsuccessfully(cls, uuid=None, error_code=None, msg=None):
        r = TestUtils.delete_function(uuid=uuid)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def get_function_code_successfully(cls, uuid=None, expected_code=None):
        r = TestUtils.get_code_for_function(uuid=uuid)
        assert r.exit_code == 0
        assert expected_code in r.output

    @classmethod
    def check_list_functions_output(
            cls,
            expected_uuid=None,
            expected_name=None,
            expected_image=None,
            expected_num_runs=None,
            expected_num_functions=None,
            expected_logout_warning=False
    ):
        columns = ['UUID', 'NAME', 'IMAGE', 'NUM_RUNS', 'WHEN']
        r = TestUtils.list_functions()
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
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
                assert expected_uuid[inverse_idx] in fields[columns.index('UUID')]

            if expected_name:
                assert expected_name[inverse_idx] in fields[columns.index('NAME')]

            if expected_image:
                print(expected_image[inverse_idx], fields[columns.index('IMAGE')])
                assert expected_image[inverse_idx] in fields[columns.index('IMAGE')]

            if expected_num_runs:
                assert expected_num_runs[inverse_idx] in fields[columns.index('NUM_RUNS')]

        return r

    # Image
    @classmethod
    def update_all_images_successfully(cls):
        r = TestUtils.update_all_images()
        assert r.exit_code == 0
        assert 'Pulling from ' in r.output

    @classmethod
    def update_all_images_unsuccessfully(cls, error_code=None, msg=None):
        r = TestUtils.update_all_images()
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def download_image_successfully(cls, registry_path=None):
        r = TestUtils.download_image(registry_path=registry_path)
        assert r.exit_code == 0
        assert 'Pulling from ' in r.output

    @classmethod
    def download_image_unsuccessfully(cls, registry_path=None, error_code=None, msg=None):
        r = TestUtils.download_image(registry_path=registry_path)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def clean_image_successfully(cls, registry_path=None):
        r = TestUtils.clean_image(registry_path=registry_path)
        assert r.exit_code == 0
        assert 'Untagged' in r.output

    @classmethod
    def clean_image_unsuccessfully(cls, registry_path=None, error_code=None, msg=None):
        r = TestUtils.clean_image(registry_path=registry_path)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def check_list_images_output(
        cls,
        only_downloaded=False,
        expected_registry_path=None,
        expected_description=None,
        expected_requires_gpu=None,
        expected_num_images=None,
        expected_logout_warning=False
    ):
        columns = ['UUID', 'REGISTRY_PATH', 'DESCRIPTION',  'REQUIRES_GPU', 'WHEN']
        r = TestUtils.list_images(only_downloaded=only_downloaded)
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
            assert r.exit_code == 0

        for column in columns:
            assert column in r.output

        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them
        num_rows = len(rows)
        image_uuids = []
        if expected_num_images:
            assert num_rows == expected_num_images

        for idx, row in enumerate(rows):
            image_uuids.append(TestUtils.extract_uuid(row))

            inverse_order = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_registry_path:
                assert expected_registry_path[inverse_order] in fields[columns.index('REGISTRY_PATH')]

            if expected_description:
                assert expected_description[inverse_order] in fields[columns.index('DESCRIPTION')]

            if expected_requires_gpu:
                assert expected_requires_gpu[inverse_order] in fields[columns.index('REQUIRES_GPU')]

        return r, image_uuids

    # Run
    @classmethod
    def create_run_successfully(cls, function_uuid=None, parameters=None):
        r = TestUtils.create_run(function_uuid=function_uuid, parameters=parameters)
        assert r.exit_code == 0
        return TestUtils.extract_uuid(r.output)

    @classmethod
    def create_run_unsuccessfully(
            cls, function_uuid=None, parameters=None, error_code=None, msg=None):
        r = TestUtils.create_run(function_uuid=function_uuid, parameters=parameters)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def delete_run_successfully(cls, uuid=None):
        r = TestUtils.delete_run(uuid=uuid)
        assert r.exit_code == 0

    @classmethod
    def delete_run_unsuccessfully(
            cls, uuid=None, error_code=None, msg=None):
        r = TestUtils.delete_run(uuid=uuid)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def check_list_runs_output(cls,
                  expected_uuid=None,
                  expected_parameters=None,
                  expected_function=None,
                  expected_num_runs=None,
                  expected_logout_warning=False
    ):
        columns = ['UUID', 'PARAMETERS', 'WHEN', 'FUNCTION']
        r = TestUtils.list_runs()
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
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

            if expected_function:
                assert expected_function[inverse_order] in fields[columns.index('FUNCTION')]

        return r

    # Instance

    @classmethod
    def start_instance_unsuccessfully(cls, job_timeout=None, error_code=None, msg=None):
        r = TestUtils.start_instance(job_timeout=job_timeout)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def create_instance_successfully(cls, type=None, price_per_minute=None, max_num_parallel_jobs=None):
        name = TestUtils.generate_random_seed()
        r = TestUtils.create_instance(name=name, type=type, price_per_minute=price_per_minute,
                                      max_num_parallel_jobs=max_num_parallel_jobs)
        assert r.exit_code == 0
        return TestUtils.extract_uuid(r.output), name

    @classmethod
    def create_instance_unsuccessfully(
            cls, name=None, type=None, price_per_minute=None, max_num_parallel_jobs=None, error_code=None, msg=None):
        r = TestUtils.create_instance(name=name, type=type, price_per_minute=price_per_minute,
                                      max_num_parallel_jobs=max_num_parallel_jobs)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def update_instance_successfully(
            cls, uuid=None, name=None, type=None, price_per_minute=None, max_num_parallel_jobs=None):
        r = TestUtils.update_instance(
            uuid=uuid, name=name, type=type, price_per_minute=price_per_minute,
            max_num_parallel_jobs=max_num_parallel_jobs)
        assert r.exit_code == 0

    @classmethod
    def update_instance_unsuccessfully(
            cls, uuid=None, name=None, type=None, price_per_minute=None, max_num_parallel_jobs=None, error_code=None, msg=None):
        r = TestUtils.update_instance(uuid=uuid, name=name, type=type, price_per_minute=price_per_minute,
                                      max_num_parallel_jobs=max_num_parallel_jobs)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def delete_instance_successfully(cls, uuid=None):
        r = TestUtils.delete_instance(uuid=uuid)
        assert r.exit_code == 0

    @classmethod
    def delete_instance_unsuccessfully(cls, uuid=None, error_code=None, msg=None):
        r = TestUtils.delete_instance(uuid=uuid)
        assert r.exit_code == error_code
        assert msg in r.output

    @classmethod
    def check_list_instances_output(cls,
                       expected_uuid=None,
                       expected_name=None,
                       expected_status=None,
                       expected_price_per_minute=None,
                       expected_type=None,
                       expected_num_running_jobs=None,
                       expected_max_num_parallel_jobs=None,
                       expected_num_instances=None,
                       expected_logout_warning=False
        ):
        config = Config(token=_read_token())
        columns = ['UUID', 'NAME', 'STATUS', 'PRICE_PER_MINUTE', 'TYPE', 'NUM_RUNNING_JOBS', 'MAX_NUM_PARALLEL_JOBS' ,'LAST_CONNECTION']
        r = TestUtils.runner.invoke(instance, [
            'list',
        ], obj=config)
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
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

            if expected_price_per_minute:
                assert expected_price_per_minute[inverse_order] in fields[columns.index('PRICE_PER_MINUTE')]

            if expected_type:
                assert expected_type[inverse_order] in fields[columns.index('TYPE')]

            if expected_num_running_jobs:
                assert expected_num_running_jobs[inverse_order] in fields[columns.index('NUM_RUNNING_JOBS')]

            if expected_max_num_parallel_jobs:
                assert expected_max_num_parallel_jobs[inverse_order] in fields[columns.index('MAX_NUM_PARALLEL_JOBS')]

        return r

    # Job
    @classmethod
    def check_list_jobs_output(cls,
                  expected_status=None,
                  expected_num_jobs=None,
                  expected_logout_warning=False
    ):
        columns = ['UUID', 'ID', 'STATUS', 'COST', 'DURATION', 'WHEN', 'RUN_UUID', 'FUNCTION']
        r = TestUtils.list_jobs()
        if expected_logout_warning:
            assert r.exit_code == 1
            assert Message.YOU_ARE_LOGOUT_WARNING in r.output
            return
        else:
            assert r.exit_code == 0

        for column in columns:
            assert column in r.output

        job_uuids = []
        rows = r.output.split('\n')[2:-1]  # The first two rows are the title so we really don't care about them
        num_rows = len(rows)
        if expected_num_jobs:
            assert num_rows == expected_num_jobs

        for idx, row in enumerate(rows):
            job_uuids.append(TestUtils.extract_uuid(row))
            inverse_order = num_rows-(idx+1)
            fields = [field for field in row.split('  ') if field]

            if expected_status:
                assert expected_status[inverse_order] in fields[columns.index('STATUS')]

        return r, job_uuids

    @classmethod
    def check_jobs_attributes(cls, uuids=None, expected_logs=None, expected_results=None,
                              expected_stdouts=None, expected_stderrs=None):
        for idx, uuid in enumerate(uuids):
            inverse_order = len(uuids)-(idx+1)

            if expected_logs:
                r = TestUtils.get_logs_for_job(uuid)
                assert r.exit_code == 0
                assert expected_logs[inverse_order] in r.output

            if expected_results:
                r = TestUtils.get_result_for_job(uuid)
                assert r.exit_code == 0
                assert expected_results[inverse_order] in r.output

            if expected_stdouts:
                r = TestUtils.get_stdout_for_job(uuid)
                assert r.exit_code == 0
                assert expected_stdouts[inverse_order] in r.output

            if expected_stderrs:
                r = TestUtils.get_stderr_for_job(uuid)
                assert r.exit_code == 0
                assert expected_stderrs[inverse_order] in r.output