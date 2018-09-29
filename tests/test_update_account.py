from tests.constants import Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_updates_his_account_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )
    new_email, new_username, _ = TestUtils.generate_credentials()
    TestWrapper.update_account_successfully(
        email=new_email,
        username=new_username,
    )

    TestWrapper.login_successfully(username=new_username, password=password)

    TestWrapper.check_account_output(
        expected_email=[new_email],
        expected_username=[new_username],
        expected_balance_is_zero=True
    )

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_updating_an_account_while_being_logged_out():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.update_account_unsuccessfully(
        email=email,
        username=username,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )
    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully()
