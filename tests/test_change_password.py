from tests.constants import Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_changes_password_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    _, _, new_password = TestUtils.generate_credentials()

    TestWrapper.change_password_successfully(password=new_password)

    TestWrapper.login_successfully(username=username, password=new_password)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_changing_password_while_being_logged_out():
    TestWrapper.change_password_unsuccessfully(
        password=TestUtils.generate_random_seed(), error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields


# Invalid Fields

def test_user_gets_validation_error_when_password_is_too_common():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.change_password_unsuccessfully(password='blabla', error_code=1, msg=Message.PASSWORD_TOO_SHORT)

    TestWrapper.delete_account_successfully()

def test_user_gets_validation_error_when_password_is_too_short():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.change_password_unsuccessfully(password='short', error_code=1, msg=Message.PASSWORD_TOO_SHORT)

    TestWrapper.delete_account_successfully()
