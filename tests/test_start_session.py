import multiprocessing
import os

import time

from tests.constants import Message, InstanceType, Image, Gpu
from tests.test_utils import TestWrapper, TestUtils


# Workflow
def test_start_session_can_fetch_a_session_from_another_user():
    instance_owner_account_uuid, instance_owner_email, instance_owner_username, instance_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=instance_owner_username, password=instance_owner_password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        ask_price=1.5,
        max_num_parallel_jobs=1
    )

    TestWrapper.download_dependencies_successfully()

    TestWrapper.download_image_successfully(registry_path=Image.TENSORFLOW_PYTHON36['path'])

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(10)

    TestWrapper.logout_successfully()

    session_owner_uuid, session_owner_email, session_owner_username, session_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=session_owner_username, password=session_owner_password)

    TestWrapper.check_account_output(
        expected_email=[session_owner_email],
        expected_username=[session_owner_username],
        expected_balance_is_zero=True
    )

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'])

    session_uuid  = TestWrapper.start_session_successfully(
        notebook_uuid=notebook_uuid, bid_price=2.0,
        password='blabla12345', base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    TestWrapper.check_list_sessions_output(
        expected_uuid=[session_uuid],
        expected_status=['CREATED'],
        expected_notebook_name=[notebook_name]
    )

    time.sleep(30)

    TestWrapper.check_list_sessions_output(
        expected_uuid=[session_uuid],
        expected_status=['IN_PROGRESS'],
        expected_notebook_name=[notebook_name]
    )

    TestWrapper.stop_session_successfully(
        uuid=session_uuid
    )
    time.sleep(10)

    TestWrapper.check_list_sessions_output(
        expected_uuid=[session_uuid],
        expected_status=['FINISHED'],
        expected_notebook_name=[notebook_name]
    )

    TestWrapper.delete_account_successfully()

    TestWrapper.login_successfully(username=instance_owner_username, password=instance_owner_password)

    p.join(0)
    p.terminate()

    # It takes very long to fetch this image, so this is why I don't clean it afterwards
    # TestWrapper.clean_image_successfully(registry_path=Image.TENSORFLOW_PYTHON36['path'])

    TestWrapper.stop_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_start_session_doesnt_pick_up_sessions_if_it_doesnt_have_the_right_image():
    instance_owner_account_uuid, instance_owner_email, instance_owner_username, instance_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=instance_owner_username, password=instance_owner_password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        ask_price=1.5,
        max_num_parallel_jobs=1
    )

    TestWrapper.download_dependencies_successfully()

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(10)

    TestWrapper.logout_successfully()

    session_owner_uuid, session_owner_email, session_owner_username, session_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=session_owner_username, password=session_owner_password)

    TestWrapper.check_account_output(
        expected_email=[session_owner_email],
        expected_username=[session_owner_username],
        expected_balance_is_zero=True
    )

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'])

    session_uuid  = TestWrapper.start_session_successfully(
        notebook_uuid=notebook_uuid, bid_price=2.0,
        password='blabla12345', base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    TestWrapper.check_list_sessions_output(
        expected_uuid=[session_uuid],
        expected_status=['CREATED'],
        expected_notebook_name=[notebook_name]
    )

    time.sleep(30)

    TestWrapper.check_list_sessions_output(
        expected_uuid=[session_uuid],
        expected_status=['CREATED'],
        expected_notebook_name=[notebook_name]
    )

    TestWrapper.delete_account_successfully()

    TestWrapper.login_successfully(username=instance_owner_username, password=instance_owner_password)

    p.join(0)
    p.terminate()

    TestWrapper.stop_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_trying_to_start_a_session_because_gpu_is_not_available():
    session_owner_uuid, session_owner_email, session_owner_username, session_owner_password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=session_owner_username, password=session_owner_password)

    TestWrapper.check_account_output(
        expected_email=[session_owner_email],
        expected_username=[session_owner_username],
        expected_balance_is_zero=True
    )

    notebook_uuid, notebook_name = TestWrapper.create_notebook_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'])

    session_uuid  = TestWrapper.start_session_unsuccessfully(
        notebook_uuid=notebook_uuid, bid_price=2.0,
        password='blabla12345', base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'], error_code=1, msg=Message.NO_GPU_AVAILABLE)

    TestWrapper.delete_notebook_successfully(uuid=notebook_uuid)

    TestWrapper.delete_account_successfully()

# Logout
def test_user_gets_validation_error_when_trying_to_start_a_session_logged_out():
    TestWrapper.start_session_unsuccessfully(notebook_uuid='b4d84e23-f7fe-4148-b32a-c880c1f95a6e', bid_price=2.0,
        password='blabla12345', base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'], error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


def test_user_gets_validation_error_when_trying_to_start_a_session_without_having_a_notebook():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.start_session_unsuccessfully(notebook_uuid='b4d84e23-f7fe-4148-b32a-c880c1f95a6e', bid_price=2.0,
        password='blabla12345', base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'], error_code=1, msg=Message.NO_ENTITY_FOUND)

    TestWrapper.delete_account_successfully()
