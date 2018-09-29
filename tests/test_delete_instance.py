from tests.constants import InstanceType, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_delete_instance_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.CPU, ask_price=1.5, max_num_parallel_jobs=3)

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_deleting_an_instance_while_being_logged_out():
    TestWrapper.delete_instance_unsuccessfully(
        uuid=TestUtils.generate_random_seed(), error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_deleting_an_instance_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_instance_unsuccessfully(error_code=2, msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully()


# Invalid Fields
def test_user_get_validation_error_when_deleting_an_instance_with_invalid_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_instance_unsuccessfully(
        uuid=TestUtils.generate_random_seed(),
        error_code=2, msg='Invalid value for "--uuid"')

    TestWrapper.delete_account_successfully()
