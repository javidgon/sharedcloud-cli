import multiprocessing
import os

import time

from tests.constants import Message, InstanceType, Image
from tests.test_utils import TestWrapper, TestUtils


# Workflow
def test_start_instance_can_fetch_a_job_from_another_user():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,),(3,))'

    job_owner_account_uuid, job_owner_email, job_owner_username, job_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=job_owner_username, password=job_owner_password)

    TestWrapper.check_account_output(
        expected_email=[job_owner_email],
        expected_username=[job_owner_username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0)

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )

    TestWrapper.logout_successfully()

    instance_owner_account_uuid, instance_owner_email, instance_owner_username, instance_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=instance_owner_username, password=instance_owner_password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    p.join(60.0)  # 60 seconds of timeout
    p.terminate()

    TestWrapper.check_account_output(
        expected_email=[instance_owner_email],
        expected_username=[instance_owner_username],
        expected_balance_is_zero=False
    )

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()

    TestWrapper.login_successfully(username=job_owner_username, password=job_owner_password)

    TestWrapper.check_list_jobs_output(
        expected_status=['SUCCEEDED', 'SUCCEEDED', 'SUCCEEDED'],
        expected_num_jobs=3
    )

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_start_instance_doesnt_pick_up_jobs_if_it_doesnt_have_the_right_image():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,),(3,))'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )
    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON27['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0)

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )

    p.join(3.0)  # 3 seconds of timeout
    p.terminate()

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logout
def test_user_gets_validation_error_when_trying_to_start_an_instance_logged_out():
    TestWrapper.start_instance_unsuccessfully(error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


def test_user_gets_validation_error_when_trying_to_start_an_instance_without_having_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.start_instance_unsuccessfully(error_code=1, msg=Message.NO_INSTANCE_FOUND)

    TestWrapper.delete_account_successfully()
