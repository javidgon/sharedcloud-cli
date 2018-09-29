import multiprocessing
import os

import time

from tests.constants import Image, InstanceType
from tests.test_utils import TestUtils, TestWrapper


# Workflow

def test_user_start_instance_and_process_one_batch_of_jobs_that_end_up_timing_out():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_timeout_python36.py'
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
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0)

    TestWrapper.check_list_jobs_output(
        expected_status=['CREATED', 'CREATED', 'CREATED'],
        expected_num_jobs=3
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={
        'job_timeout': 10
    })
    p.start()
    time.sleep(5)
    TestWrapper.check_list_jobs_output(
        expected_status=['IN_PROGRESS', 'IN_PROGRESS', 'IN_PROGRESS'],
        expected_num_jobs=3
    )
    p.join(60.0)  # 60 seconds of timeout
    p.terminate()

    r, job_uuids = TestWrapper.check_list_jobs_output(
        expected_status=['TIMEOUT', 'TIMEOUT', 'TIMEOUT'],
        expected_num_jobs=3
    )

    TestWrapper.check_jobs_attributes(
        uuids=job_uuids,
        expected_logs=[
            '',
            '',
            ''
        ],
        expected_results=[
            '',
            '',
            ''
        ],
        expected_stdouts=[
            '',
            '',
            '',
        ]
    )

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=False
    )

    TestWrapper.clean_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()
