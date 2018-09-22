import os
import multiprocessing
import time

from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown, _accountWithSpecialPowersSetUp


def test_user_wants_to_download_and_clean_an_image():
    # 1) Create an account and login into the system
    email, username, password, account_uuid = _accountSetUp()

    # 2) Create instance
    instance_name = TestUtils.generate_random_seed()

    r = TestUtils.create_instance(
        name=instance_name,
        price_per_hour=1.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 3) Download Image
    r = TestUtils.download_image(
        instance_uuid=instance_uuid,
        registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Pulling from sharedcloud/web-crawling-python36' in r.output

    # 4) Clean Image
    r = TestUtils.clean_image(
        instance_uuid=instance_uuid,
        registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Untagged: sharedcloud/web-crawling-python36' in r.output
    assert 'Deleted' in r.output

    # 5) Delete Instance
    r = TestUtils.delete_instance(uuid=instance_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 6) Delete account
    _accountTearDown(account_uuid)

def test_user_wants_to_see_his_account_information():
    # 1) Create an account and login into the system
    email, username, password, account_uuid = _accountSetUp()

    # 2) Query his account details
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    # 3) Logout of the system
    r = TestUtils.logout()
    assert r.exit_code == 0

    # 4) Login again
    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    # 5) Delete his account
    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output

def test_user_creates_updates_and_deletes_an_account():
    # 1) Create account
    email, username, password, account_uuid = _accountSetUp()

    # 2) Query his account details
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    # 3) Update his account
    new_email, new_username, new_password = TestUtils.generate_credentials()

    r = TestUtils.update_account(
        uuid=account_uuid,
        email=new_email,
        username=new_username,
        password=new_password
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output

    # 4) Check again for the new values
    TestUtils.check_account_output(
        expected_email=[new_email],
        expected_username=[new_username],
        expected_balance_is_zero=True
    )

    # 5) Log out and try to login again with the new password
    r = TestUtils.logout()
    assert r.exit_code == 0

    r = TestUtils.login(new_username, new_password)
    assert r.exit_code == 0

    # 6) Delete account
    _accountTearDown(account_uuid)

    # 7) If we try to logout now it should complain because
    # the account was logged out automatically
    r = TestUtils.logout()
    assert r.exit_code == 1
    assert 'You were already logged out' in r.output

    # 8) Let's see now if we can login or the account is really deleted
    r = TestUtils.login(new_username, new_password)
    assert r.exit_code == 1
    assert '"Unable to log in with provided credentials' in r.output


def test_user_tries_to_create_a_run_but_his_balance_is_insufficient():
    # 1) Create an account
    email, username, password, account_uuid = _accountSetUp()

    # 2) Query his account details
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'
    parameters = '((1,), (2,))'

    # 3) Create a function to execute (by providing the code inline)
    function_name = TestUtils.generate_random_seed()
    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )
    r = TestUtils.create_function(
        name=function_name,
        code=code,
        image_uuid=uuids[0]  # We take the first image (inverse order)
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 4) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 1
    assert 'you need a balance higher than 0 to create new runs' in r.output

    # 5) Delete account
    _accountTearDown(account_uuid)


def test_user_tries_to_change_his_password_but_his_password_is_too_weak():
    # 1) Create an account
    email, username, password, account_uuid = _accountSetUp()


    # 2) Query his account details
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    # 3) Update his account
    new_email, new_username, new_password = TestUtils.generate_credentials()

    r = TestUtils.update_account(
        uuid=account_uuid,
        email=new_email,
        username=new_username,
        password='12345'
    )
    assert r.exit_code == 1
    assert 'This password is too short. It must contain at least 9 characters' in r.output

    # 4) Delete account
    _accountTearDown(account_uuid)

def test_customer_performs_a_complete_workflow_with_code():
    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'
    parameters = '((1,), (2,))'

    # 1) Create account with special powers (doesn't need money)
    email, username, password, account_uuid = _accountWithSpecialPowersSetUp(1)

    # 2) Create a function to execute (by providing the code inline)
    function_name = TestUtils.generate_random_seed()

    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=function_name,
        code=code,
        image_uuid=uuids[0]  # We take the first image (inverse order)
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 3) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    run_uuid = TestUtils.extract_uuid(r.output)

    # 4) List the function that we just created
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[function_name],
        expected_image=['sharedcloud/web-crawling-python36:latest'],
        expected_num_runs=['1'],
        expected_num_functions=1
    )

    r = TestUtils.get_code_for_function(function_uuid)
    assert r.exit_code == 0
    assert code in r.output

    # 5) List the run that we just created
    TestUtils.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_function=[function_name],
        expected_num_runs=1
    )

    # 6) List the jobs that were generated by the run
    TestUtils.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED'],
        expected_num_jobs=2
    )

    # 7) Delete the run we created
    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 8) Update the function with a different name
    new_function_name = TestUtils.generate_random_seed()

    r = TestUtils.update_function(
        uuid=function_uuid,
        name=new_function_name
    )
    print(r.output)
    assert r.exit_code == 0
    assert 'was updated' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 9) We list the function we just updated
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[new_function_name],
        expected_image=['sharedcloud/web-crawling-python36:latest'],
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    # 10) Delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Delete account
    _accountTearDown(account_uuid)


def test_customer_performs_a_complete_workflow_with_file():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,), (2,))'

    # 1) Create account with special powers (doesn't need money)
    email, username, password, account_uuid = _accountWithSpecialPowersSetUp(2)

    # 2) Create a function to execute (by providing the filepath)
    function_name = TestUtils.generate_random_seed()
    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=function_name,
        file=filepath,
        image_uuid=uuids[0]  # We take the first image (inverse order)
    )

    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 3) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    run_uuid = TestUtils.extract_uuid(r.output)

    # 4) List the function that we just created
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[function_name],
        expected_image=['sharedcloud/web-crawling-python36:latest'],
        expected_num_runs=['1'],
        expected_num_functions=1
    )

    # 5) List the run that we just created
    TestUtils.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_function=[function_name],
        expected_num_runs=1
    )

    # 6) List the jobs that were generated by the run
    TestUtils.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED'],
        expected_num_jobs=2
    )

    # 7) Delete the run we created
    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 8) Update the function with a different name
    new_function_name = TestUtils.generate_random_seed()

    r = TestUtils.update_function(
        uuid=function_uuid,
        name=new_function_name
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 9) We list the function we just updated
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=[new_function_name],
        expected_image=['sharedcloud/web-crawling-python36:latest'],
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    # 10) Delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Logout of the system
    _accountTearDown(account_uuid)


def test_provider_performs_complete_workflow_with_jobs_that_succeed():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,),(3,))'

    # 1) Create account with special powers (doesn't need money)
    email, username, password, account_uuid = _accountWithSpecialPowersSetUp(3)

    # 2) Create a function to execute (by providing the code inline)
    function_name = TestUtils.generate_random_seed()
    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=function_name,
        file=filepath,
        image_uuid=uuids[0]  # We take the first image (inverse order)
    )

    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 3) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    run_uuid = TestUtils.extract_uuid(r.output)

    # 4) Create an instance
    instance_name = TestUtils.generate_random_seed()

    r = TestUtils.create_instance(
        name=instance_name,
        price_per_hour=1.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 4b) Download Image
    r = TestUtils.download_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Pulling from sharedcloud/web-crawling-python36' in r.output

    # 5) List the instance we just created
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # 6) Update the instance we just created
    new_instance_name = TestUtils.generate_random_seed()

    r = TestUtils.update_instance(
        uuid=instance_uuid,
        name=new_instance_name,
        price_per_hour=2.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 7) List the instance we just updated
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )
    # 8) Start the instance so it starts listening from tasks.
    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={
        'uuid': instance_uuid
    })
    p.start()

    # Wait 5 seconds for start_instance to start and set some jobs to "IN_PROGRESS"
    time.sleep(5)
    TestUtils.check_list_jobs_output(
        expected_status=['IN_PROGRESS', 'IN_PROGRESS', 'CREATED'],
        expected_num_jobs = 3
    )

    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['2'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # Now it should fail if we try to delete either the function or the Run,
    # because we have one Job in progress

    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    # We wait until the process has finished
    p.join(30.0)  # 30 seconds of timeout
    p.terminate()

    # 9) List the jobs that were generated by the run. We check that the jobs were processed successfully
    _, uuids = TestUtils.check_list_jobs_output(
        expected_status=['SUCCEEDED', 'SUCCEEDED', 'SUCCEEDED'],
        expected_num_jobs = 3,
    )

    for uuid in uuids:
        r = TestUtils.get_stdout_for_job(uuid)
        assert r.exit_code == 0
        assert 'Hello World' in r.output

        r = TestUtils.get_result_for_job(uuid)
        assert r.exit_code == 0
        assert '42' in r.output

        r = TestUtils.get_logs_for_job(uuid)
        assert r.exit_code == 0
        assert 'Pulling' in r.output

    # 10) Check balance
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=False
    )

    # 11) Now we can delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Also the instance we created (and the image we downloaded)
    r = TestUtils.clean_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Untagged: sharedcloud/web-crawling-python36' in r.output
    assert 'Deleted' in r.output

    r = TestUtils.delete_instance(uuid=instance_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 12) Delete account
    _accountTearDown(account_uuid)


def test_provider_performs_complete_workflow_with_jobs_that_timeout():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),)'
    # 1) Create account with special powers (doesn't need money)
    email, username, password, account_uuid = _accountWithSpecialPowersSetUp(4)

    # 2) Create a function to execute (by providing the code inline)
    function_name = TestUtils.generate_random_seed()

    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=function_name,
        file=filepath,
        image_uuid=uuids[0]  # We take the image in the middle
    )

    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 3) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    run_uuid = TestUtils.extract_uuid(r.output)

    # 4) Create an instance
    instance_name = TestUtils.generate_random_seed()

    r = TestUtils.create_instance(
        name=instance_name,
        price_per_hour=1.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 4b) Download Image
    r = TestUtils.download_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Pulling from sharedcloud/web-crawling-python36' in r.output

    # 5) List the instance we just created
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # 6) Update the instance we just created
    new_instance_name = TestUtils.generate_random_seed()

    r = TestUtils.update_instance(
        uuid=instance_uuid,
        name=new_instance_name,
        price_per_hour=2.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 7) List the instance we just updated
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )
    # 8) Start the instance so it starts listening from tasks.
    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={
        'uuid': instance_uuid, 'job_timeout': 7.0
    })
    p.start()

    # Wait 5 seconds for start_instance to start and set some jobs to "IN_PROGRESS"
    time.sleep(5)
    TestUtils.check_list_jobs_output(
        expected_status=['IN_PROGRESS'],
        expected_num_jobs = 1
    )
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['1'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # Now it should fail if we try to delete either the function or the Run,
    # because we have one Job in progress

    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    # We wait until the process has finished
    p.join(30.0)  # 30 seconds of timeout
    p.terminate()

    # 9) List the jobs that were generated by the run. We check that the jobs were processed successfully
    _, uuids = TestUtils.check_list_jobs_output(
        expected_status=['TIMEOUT'],
        expected_num_jobs = 1,
    )

    # 10) Check balance
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=False
    )

    # 11) Now we can delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Also the instance we created (and the image we downloaded)
    r = TestUtils.clean_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Untagged: sharedcloud/web-crawling-python36' in r.output
    assert 'Deleted' in r.output

    r = TestUtils.delete_instance(uuid=instance_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 12) Delete account
    _accountTearDown(account_uuid)


def test_provider_performs_complete_workflow_with_jobs_that_fail():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/files/invalid_func_python36.py'
    parameters = '((1,),)'

    # 1) Create account with special powers (doesn't need money)
    email, username, password, account_uuid = _accountWithSpecialPowersSetUp(5)

    # 2) Create a function to execute (by providing the code inline)
    function_name = TestUtils.generate_random_seed()

    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=function_name,
        file=filepath,
        image_uuid=uuids[0]  # We take the last image (inverse order)
    )

    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 3) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    run_uuid = TestUtils.extract_uuid(r.output)

    # 4) Create an instance
    instance_name = TestUtils.generate_random_seed()

    r = TestUtils.create_instance(
        name=instance_name,
        price_per_hour=1.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 4b) Download Image
    r = TestUtils.download_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Pulling from sharedcloud/web-crawling-python36' in r.output

    # 5) List the instance we just created
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # 6) Update the instance we just created
    new_instance_name = TestUtils.generate_random_seed()

    r = TestUtils.update_instance(
        uuid=instance_uuid,
        name=new_instance_name,
        price_per_hour=2.5,
        max_num_parallel_jobs=2
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 7) List the instance we just updated
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )
    # 8) Start the instance so it starts listening from tasks.
    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={
        'uuid': instance_uuid
    })
    p.start()

    # Wait 5 seconds for start_instance to start and set some jobs to "IN_PROGRESS"
    time.sleep(5)
    TestUtils.check_list_jobs_output(
        expected_status=['IN_PROGRESS'],
        expected_num_jobs = 1
    )

    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['1'],
        expected_max_num_parallel_jobs=['2'],
        expected_num_instances=1
    )

    # Now it should fail if we try to delete either the function or the Run,
    # because we have one Job in progress

    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    # We wait until the process has finished
    p.join(30.0)  # 30 seconds of timeout
    p.terminate()

    # 9) List the jobs that were generated by the run. We check that the jobs were processed successfully
    _, uuids = TestUtils.check_list_jobs_output(
        expected_status=['FAILED'],
        expected_num_jobs = 1,
    )

    for uuid in uuids:
        r = TestUtils.get_stdout_for_job(uuid)
        assert r.exit_code == 0
        assert 'This is a test Exception' in r.output

        r = TestUtils.get_result_for_job(uuid)
        assert r.exit_code == 0
        assert len(r.output) == 1

        r = TestUtils.get_logs_for_job(uuid)
        assert r.exit_code == 0
        assert 'Pulling' in r.output

    # 10) Check balance
    TestUtils.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    # 11) Now we can delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Also the instance we created (and the image we downloaded)
    r = TestUtils.clean_image(instance_uuid=instance_uuid, registry_path='sharedcloud/web-crawling-python36:latest')
    assert r.exit_code == 0
    assert 'Untagged: sharedcloud/web-crawling-python36' in r.output
    assert 'Deleted' in r.output

    r = TestUtils.delete_instance(uuid=instance_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 12) Logout of the system
    _accountTearDown(account_uuid)
