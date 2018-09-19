import os
import multiprocessing
import time

from tests.test_utils import TestUtils

username = os.environ.get('SHAREDCLOUD_USERNAME')
password = os.environ.get('SHAREDCLOUD_PASSWORD')


def test_user_wants_to_see_his_account_information():
    # 1) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 2) Query his account details
    TestUtils.check_account_output(
        expected_email='superuser@example.com',
        expected_balance='$0.0'
    )

    # 3) Logout of the system
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'Successfully logged out' in r.output


def test_user_creates_updates_and_deletes_an_account():
    email = 'random555@example.com'
    username = 'random555'
    password = 'blabla12345'
    # 1) Create an account
    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    # 2) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 3) Query his account details
    TestUtils.check_account_output(
        expected_email=email,
        expected_username=username,
        expected_balance='$0.0'
    )

    # 4) Update his account
    new_email = 'random999@example.com'
    new_username = 'random999'
    new_password = 'new_password123'

    r = TestUtils.update_account(
        uuid=account_uuid,
        email=new_email,
        username=new_username,
        password=new_password
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output

    # 5) Check again for the new values
    TestUtils.check_account_output(
        expected_email=new_email,
        expected_username=new_username,
        expected_balance='$0.0'
    )

    # 6) Log out and try to login again with the new password
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'Successfully logged out' in r.output

    r = TestUtils.login(new_username, new_password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 7) Delete account
    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output
    assert 'Successfully logged out' in r.output

    # 8) If we try to logout now it should complain because
    # the account was logged out automatically
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'You were already logged out' in r.output

    # 9) Let's see now if we can login or the account is really deleted
    r = TestUtils.login(new_username, new_password)
    assert r.exit_code == 0
    assert '"Unable to log in with provided credentials' in r.output


def test_user_tries_to_create_a_run_but_his_balance_is_insufficient():
    email = 'random555@example.com'
    username = 'random555'
    password = 'blabla12345'
    # 1) Create an account
    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    # 2) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 3) Query his account details
    TestUtils.check_account_output(
        expected_email=email,
        expected_username=username,
        expected_balance='$0.0'
    )

    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'
    runtime = 'python36'
    parameters = '((1,), (2,))'

    # 4) Create a function to execute (by providing the code inline)
    r = TestUtils.create_function(
        name='example1',
        code=code,
        runtime=runtime
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 5) Create a run where we specify some parameters
    r = TestUtils.create_run(
        function_uuid=function_uuid,
        parameters=parameters
    )
    assert r.exit_code == 1
    assert 'you need a balance higher than 0 to create new runs' in r.output

    # 6) Delete account
    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output
    assert 'Successfully logged out' in r.output


def test_user_tries_to_change_his_password_but_his_password_is_too_weak():
    email = 'random555@example.com'
    username = 'random555'
    password = 'blabla12345'
    # 1) Create an account
    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    # 2) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 3) Query his account details
    TestUtils.check_account_output(
        expected_email=email,
        expected_username=username,
        expected_balance='$0.0'
    )

    # 4) Update his account
    new_email = 'random999@example.com'
    new_username = 'random999'
    new_password = '12345'

    r = TestUtils.update_account(
        uuid=account_uuid,
        email=new_email,
        username=new_username,
        password=new_password
    )
    assert r.exit_code == 1
    assert 'This password is too short. It must contain at least 9 characters' in r.output

    # 5) Delete account
    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output
    assert 'Successfully logged out' in r.output


def test_customer_performs_a_complete_workflow_with_code():
    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'
    runtime = 'python36'
    parameters = '((1,), (2,))'

    # 1) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output


    # 2) Create a function to execute (by providing the code inline)
    r = TestUtils.create_function(
        name='example1',
        code=code,
        runtime=runtime
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
        expected_name=['example1'],
        expected_runtime=runtime,
        expected_num_runs=['1'],
        expected_num_functions=1
    )

    # 5) List the run that we just created
    TestUtils.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_function_name=['example1'],
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
    r = TestUtils.update_function(
        uuid=function_uuid,
        name='example2'
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 9) We list the function we just updated
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=['example2'],
        expected_runtime=runtime,
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    # 10) Delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Logout of the system
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'Successfully logged out' in r.output


def test_customer_performs_a_complete_workflow_with_file():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/../examples/testing_func_python36.py'
    runtime = 'python36'
    parameters = '((1,), (2,))'

    # 1) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 2) Create a function to execute (by providing the filepath)
    r = TestUtils.create_function(
        name='example1',
        file=filepath,
        runtime=runtime
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
        expected_name=['example1'],
        expected_runtime=runtime,
        expected_num_runs=['1'],
        expected_num_functions=1
    )

    # 5) List the run that we just created
    TestUtils.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_function_name=['example1'],
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
    r = TestUtils.update_function(
        uuid=function_uuid,
        name='example2'
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    function_uuid = TestUtils.extract_uuid(r.output)

    # 9) We list the function we just updated
    TestUtils.check_list_functions_output(
        expected_uuid=[function_uuid],
        expected_name=['example2'],
        expected_runtime=runtime,
        expected_num_runs=['0'],
        expected_num_functions=1
    )

    # 10) Delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) Logout of the system
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'Successfully logged out' in r.output


def test_provider_performs_complete_workflow_with_a_job():
    code = 'def handler(event): print("Hello World {}".format(event[0])); return 42 + int(event[0])'
    runtime = 'python36'
    parameters = '((1,),)'

    # 1) Login into the system
    r = TestUtils.login(username, password)
    assert r.exit_code == 0
    assert 'Successfully logged in :)' in r.output

    # 2) Create a function to execute (by providing the code inline)
    r = TestUtils.create_function(
        name='example1',
        code=code,
        runtime=runtime
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
    r = TestUtils.create_instance(
        name='instance1',
        price_per_hour=1.5,
        max_num_jobs=5
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 5) List the instance we just created
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=['instance1'],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_jobs=['5'],
        expected_num_instances=1
    )

    # 6) Update the instance we just created
    r = TestUtils.update_instance(
        uuid=instance_uuid,
        name='instance2',
        price_per_hour=2.5,
        max_num_jobs=10
    )
    assert r.exit_code == 0
    assert 'was updated' in r.output
    instance_uuid = TestUtils.extract_uuid(r.output)

    # 7) List the instance we just updated
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=['instance2'],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_jobs=['10'],
        expected_num_instances=1
    )
    # 8) Start the instance so it starts listening from tasks.
    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={
        'uuid': instance_uuid
    })
    p.start()

    # Wait 10 seconds for start_instance to start and set some jobs to "IN_PROGRESS"
    time.sleep(10)
    TestUtils.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=['instance2'],
        expected_status=['AVAILABLE'],
        expected_price_per_hour=['2.5'],
        expected_num_running_jobs=['2'],
        expected_max_num_jobs=['10'],
        expected_num_instances=1
    )
    TestUtils.check_list_jobs_output(
        expected_status=['IN_PROGRESS'],
        expected_num_jobs = 1
    )

    # Now it should fail if we try to delete either the function or the Run,
    # because we have one Job in progress

    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    r = TestUtils.delete_run(uuid=run_uuid)
    assert r.exit_code == 1
    assert 'Please wait until they are finished' in r.output

    # We wait to give some time to the instance to process the jobs
    time.sleep(150)

    # Terminate foo
    p.terminate()

    # Cleanup
    p.join()

    # 9) List the jobs that were generated by the run. We check that the job was processed successfully
    TestUtils.check_list_jobs_output(
        expected_status=['SUCCEEDED'],
        expected_output=('Hello World 1'),
        expected_response=('43'),
        expected_num_jobs = 1,
    )

    # 10) Check balance
    TestUtils.check_account_output(
        expected_email='superuser@example.com',
        expected_balance='$-0.22'
    )

    # 10) Delete the function
    r = TestUtils.delete_function(uuid=function_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 11) It deletes the instance we created
    r = TestUtils.delete_instance(uuid=instance_uuid)
    assert r.exit_code == 0
    assert 'was deleted' in r.output

    # 12) Logout of the system
    r = TestUtils.logout()
    assert r.exit_code == 0
    assert 'Successfully logged out' in r.output