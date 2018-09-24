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
    new_email, new_username, new_password= TestUtils.generate_credentials()
    TestWrapper.update_account_successfully(
        uuid=account_uuid,
        email=new_email,
        username=new_username,
        password=new_password
    )

    TestWrapper.login_successfully(username=new_username, password=new_password)

    TestWrapper.check_account_output(
        expected_email=[new_email],
        expected_username=[new_username],
        expected_balance_is_zero=True
    )

    TestWrapper.delete_account_successfully(uuid=account_uuid)

# Logged out
def test_user_gets_validation_error_when_updating_an_account_while_being_logged_out():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.update_account_unsuccessfully(
        uuid=account_uuid,
        email=email,
        username=username,
        password=password,
        error_code=1,
        msg=Message.YOU_ARE_LOGOUT_WARNING
    )
    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

# Missing fields

#Invalid Fields
def test_user_gets_validation_error_when_creating_an_account_with_invalid_password():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.update_account_unsuccessfully(
        uuid=account_uuid,
        email=email,
        username=username,
        password='blabla',
        error_code=1,
        msg='This password is too common'
    )
    TestWrapper.delete_account_successfully(uuid=account_uuid)