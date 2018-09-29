from tests.constants import InstanceType, Message, Gpu
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_a_cpu_instance_successfully():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()
    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['5'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_updates_a_gpu_instance_successfully_passing_max_num_parallel_jobs_as_1():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.GPU,
        ask_price=2.5,
        max_num_parallel_jobs=1,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_updates_a_gpu_instance_successfully_not_passing_max_num_parallel_jobs():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.GPU,
        ask_price=2.5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['1'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_updates_a_gpu_instance_to_cpu_instance_successfully():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['5'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_updating_an_instance_while_being_logged_out():
    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )


# Missing fields
def test_user_get_validation_error_when_updating_an_instance_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5,
        error_code=2,
        msg='Missing option "--uuid"'
    )

    TestWrapper.delete_account_successfully()

def test_user_doesnt_get_validation_error_when_updating_a_gpu_instance_with_missing_gpu_because_was_previously_set():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        ask_price=1.5,
        max_num_parallel_jobs=1,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        ask_price=2.5,
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


# Invalid Fields

def test_user_gets_validation_error_when_changing_from_cpu_to_gpu_and_still_providing_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3,
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.GPU,
        ask_price=2.5,
        max_num_parallel_jobs=3,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is invalid. All GPU instances can only process one job at a time'
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()

def test_user_gets_validation_error_when_changing_from_cpu_to_gpu_and_not_changing_a_previously_set_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3,
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.GPU,
        ask_price=2.5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='"current set value (3) is invalid for a GPU instance. Please set it to 1'
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()

def test_user_gets_validation_error_when_changing_from_gpu_to_cpu_and_still_providing_gpu():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is unnecessary because the instance is not, or not gonna be type GPU anymore'
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

def test_user_get_validation_error_when_updating_an_unknown_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg=Message.NO_RESOURCE_FOUND
    )

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_updating_an_instance_with_invalid_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type='blabla',
        ask_price=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--type"'
    )

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_updating_an_instance_with_invalid_ask_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price='blabla',
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--ask-price"'
    )

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_updating_an_instance_with_invalid_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs='blabla',
        error_code=2,
        msg='Invalid value for "--max-num-parallel-jobs"'
    )

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_updating_by_providing_gpu_without_being_a_gpu_instance():
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
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()
    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.CPU,
        ask_price=2.5,
        max_num_parallel_jobs=5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is unnecessary because the instance is not, or not gonna be type GPU anymore'
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_ask_price=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_updating_an_instance_with_a_too_low_ask_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU,
        ask_price=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=TestUtils.generate_random_seed(),
        type=InstanceType.CPU,
        ask_price=0.0001,
        max_num_parallel_jobs=2,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='cannot be smaller than $0.001'
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()
