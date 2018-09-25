from tests.constants import Message
from tests.test_utils import TestUtils, TestWrapper


# Worflow

def test_user_deletes_account_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


# Logged out
def test_user_get_validation_error_when_deleting_an_account_while_being_logged_out():
    TestWrapper.delete_account_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_deleting_an_account_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_unsuccessfully(error_code=2, msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully(uuid=account_uuid)

# Invalid Fields
