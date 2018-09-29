import multiprocessing

import time

from tests.constants import Message, InstanceType, Gpu
from tests.test_utils import TestUtils, TestWrapper


# Workflow

def test_user_creates_a_cpu_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_type=['CPU'],
        expected_gpu=['n/a'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_creates_a_gpu_instance_successfully_passing_max_num_parallel_jobs_as_1():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        ask_price=1.5,
        max_num_parallel_jobs=1,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )


    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_type=['GPU'],
        expected_gpu=[Gpu.TITAN_V_12GB['name']],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_creates_a_gpu_instance_successfully_not_passing_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        ask_price=1.5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )


    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_type=['GPU'],
        expected_gpu=[Gpu.TITAN_V_12GB['name']],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_creates_an_instance_that_overrides_old_instance_as_the_active_one_in_the_system():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    first_instance_uuid, fist_instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[first_instance_uuid],
        expected_name=[fist_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    second_instance_uuid, second_instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)
    TestWrapper.check_list_instances_output(
        expected_uuid=[first_instance_uuid, second_instance_uuid],
        expected_name=[fist_instance_name, second_instance_name],
        expected_status=['NOT_AVAILABLE', 'AVAILABLE'],
        expected_ask_price=['1.5', '1.5'],
        expected_num_running_jobs=['0', '0'],
        expected_max_num_parallel_jobs=['3', '3'],
        expected_num_instances=2
    )

    p.terminate()

    TestWrapper.delete_instance_successfully(uuid=second_instance_uuid)

    TestWrapper.delete_instance_successfully(uuid=first_instance_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_creating_an_instance_while_being_logged_out():
    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )


# Missing fields
def test_user_gets_validation_error_when_creating_an_instance_with_missing_name():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Missing option "--name"'
    )
    TestWrapper.delete_account_successfully()


def test_user_doesnt_get_validation_error_when_creating_an_instance_with_missing_type_because_cpu_is_used_by_default():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_an_instance_with_missing_ask_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Missing option "--ask-price"'
    )

    TestWrapper.delete_account_successfully()


# Optional Fields with Default
def test_user_doesnt_get_validation_error_when_creating_an_instance_with_missing_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()

def test_user_gets_validation_error_when_creating_a_gpu_instance_with_missing_gpu():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.GPU,
        ask_price=1.5,
        error_code=1,
        msg='needs to be provided if the instance is type GPU"'
    )

    TestWrapper.delete_account_successfully()

# Invalid Fields

def test_user_get_validation_error_when_creating_an_instance_with_invalid_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type='blabla',
        ask_price=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--type"'
    )

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_an_instance_with_invalid_ask_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price='blabla',
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--ask-price"'
    )

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_an_instance_with_invalid_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs='blabla',
        error_code=2,
        msg='Invalid value for "--max-num-parallel-jobs"'
    )

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_by_providing_gpu_without_being_a_gpu_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=2,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is unnecessary because the instance is not, or not gonna be type GPU anymore'
    )

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_an_instance_with_a_too_low_ask_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=0.0001,
        max_num_parallel_jobs=2,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='cannot be smaller than $0.001'
    )

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_an_instance_with_a_max_num_parallel_jobs_bigger_than_one():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_instance_unsuccessfully(
        name=TestUtils.generate_random_seed(),
        type=InstanceType.GPU,
        ask_price=0.01,
        max_num_parallel_jobs=2,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is invalid. All GPU instances can only process one job at a time'
    )

    TestWrapper.delete_account_successfully()
