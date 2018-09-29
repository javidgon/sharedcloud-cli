import multiprocessing
import os
import time

from tests.constants import Image, InstanceType, Gpu
from tests.test_utils import TestWrapper, TestUtils


# Workflow
def test_user_sees_the_list_of_offers_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU, ask_price=1.5, max_num_parallel_jobs=3)

    TestWrapper.download_image_successfully(registry_path=Image.WEB_CRAWLING_PYTHON36['path'])

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(10)

    TestWrapper.check_list_offers_output(
        expected_instance_name=[instance_name],
        expected_type=[InstanceType.CPU.upper()],
        expected_gpu=['n/a'],
        expected_cuda_cores=['n/a'],
        expected_ask_price=['$1.800'],
    )

    p.terminate()

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


#Logged out
def test_user_gets_validation_error_when_listing_offers_while_being_logged_out():
    TestWrapper.check_list_offers_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid Fields
