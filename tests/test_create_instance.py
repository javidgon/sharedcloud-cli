import multiprocessing

import time

from tests.constants import Message, InstanceType
from tests.test_utils import TestUtils, TestWrapper


# Workflow

def test_user_creates_an_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_creates_an_instance_that_overrides_old_instance_as_the_active_one_in_the_system():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    first_instance_uuid, fist_instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[first_instance_uuid],
        expected_name=[fist_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    second_instance_uuid, second_instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs=3
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)
    TestWrapper.check_list_instances_output(
        expected_uuid=[first_instance_uuid, second_instance_uuid],
        expected_name=[fist_instance_name, second_instance_name],
        expected_status=['NOT_AVAILABLE', 'AVAILABLE'],
        expected_price_per_minute=['1.5', '1.5'],
        expected_num_running_jobs=['0', '0'],
        expected_max_num_parallel_jobs=['3', '3'],
        expected_num_instances=2
    )

    p.terminate()

    TestWrapper.delete_instance_successfully(uuid=second_instance_uuid)

    TestWrapper.delete_instance_successfully(uuid=first_instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Logged out
def test_user_gets_validation_error_when_creating_an_instance_while_being_logged_out():
    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )


# Missing fields
def test_user_gets_validation_error_when_creating_an_instance_with_missing_name():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Missing option "--name"'
    )
    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_gets_validation_error_when_creating_an_instance_with_missing_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Missing option "--type"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_gets_validation_error_when_creating_an_instance_with_missing_price_per_minute():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Missing option "--price-per-minute"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Optional Fields with Default
def test_user_doesnt_get_validation_error_when_creating_an_instance_with_missing_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Invalid Fields

def test_user_get_validation_error_when_creating_an_instance_with_invalid_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type='blabla',
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--type"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_creating_an_instance_with_invalid_price_per_minute():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_minute='blabla',
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--price-per-minute"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_creating_an_instance_with_invalid_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs='blabla',
        error_code=2,
        msg='Invalid value for "--max-num-parallel-jobs"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)
