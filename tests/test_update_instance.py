from tests.constants import InstanceType, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_an_instance_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.STANDARD,
        price_per_hour=1.5,
        max_num_parallel_jobs=3
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['1.5'],
        expected_num_running_jobs=['0'],
        expected_max_num_parallel_jobs=['3'],
        expected_num_instances=1
    )

    new_instance_name = TestUtils.generate_random_seed()
    TestWrapper.update_instance_successfully(
        uuid=instance_uuid,
        name=new_instance_name,
        type=InstanceType.STANDARD,
        price_per_hour=2.5,
        max_num_parallel_jobs=5
    )

    TestWrapper.check_list_instances_output(
        expected_uuid=[instance_uuid],
        expected_name=[new_instance_name],
        expected_status=['NOT_AVAILABLE'],
        expected_price_per_hour=['2.5'],
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
        price_per_hour=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg='You seem to be logged out. Please log in first'
    )


# Missing fields
def test_user_get_validation_error_when_updating_an_instance_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        type=InstanceType.STANDARD,
        price_per_hour=2.5,
        max_num_parallel_jobs=5,
        error_code=2,
        msg='Missing option "--uuid"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Invalid Fields
def test_user_get_validation_error_when_updating_an_unknown_instance():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        type=InstanceType.STANDARD,
        price_per_hour=2.5,
        max_num_parallel_jobs=5,
        error_code=1,
        msg=Message.NO_RESOURCE_FOUND
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)

test_user_get_validation_error_when_updating_an_unknown_instance()
def test_user_get_validation_error_when_updating_an_instance_with_invalid_type():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type='blabla',
        price_per_hour=1.5,
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--type"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_get_validation_error_when_updating_an_instance_with_invalid_price_per_hour():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_hour='blabla',
        max_num_parallel_jobs=3,
        error_code=2,
        msg='Invalid value for "--price_per_hour"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_max_num_parallel_jobs():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_instance_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        name=TestUtils.generate_random_seed(),
        type=InstanceType.STANDARD,
        price_per_hour=1.5,
        max_num_parallel_jobs='blabla',
        error_code=2,
        msg='Invalid value for "--max_num_parallel_jobs"'
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)