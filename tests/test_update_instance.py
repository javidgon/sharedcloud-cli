from tests.constants import InstanceType, Message, Gpu
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_an_standard_instance_successfully():
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

    new_instance_name = TestUtils.generate_random_seed()
    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['5'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_updates_a_gpu_instance_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
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

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.GPU,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['5'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_updates_a_gpu_instance_to_standard_instance_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
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

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_minute=['2.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['5'],
        expected_num_instances=1
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Logged out
def test_user_get_validation_error_when_updating_an_instance_while_being_logged_out():
    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )


# Missing fields
def test_user_get_validation_error_when_updating_an_instance_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        error_code=2,
        msg='Missing option "--uuid"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_doesnt_get_validation_error_when_updating_a_gpu_instance_with_missing_gpu_because_was_previously_set():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
    )

    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        price_per_minute=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Invalid Fields

def test_user_gets_validation_error_when_changing_from_gpu_to_standard_and_still_providing_gpu():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU,
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid']
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

    new_instance_name = TestUtils.generate_random_seed()

    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is unnecessary because the instance is not, or not gonna be type GPU anymore'
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

def test_user_get_validation_error_when_updating_an_unknown_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg=Message.NO_RESOURCE_FOUND
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type='blabla',
        price_per_minute=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--type"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_price_per_minute():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_minute='blabla',
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--price-per-minute"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_minute=1.5,
        max_num_parallel_jobs='blabla',
        error_code=2,
        msg='Invalid value for "--max-num-parallel-jobs"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_gets_validation_error_when_updating_by_providing_gpu_without_being_a_gpu_instance():
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

    new_instance_name = TestUtils.generate_random_seed()
    TestWrapper.update_instance_unsuccessfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.STANDARD,
        price_per_minute=2.5,
        max_num_parallel_jobs=5,
        gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1,
        msg='is unnecessary because the instance is not, or not gonna be type GPU anymore'
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