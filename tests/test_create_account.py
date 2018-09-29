from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_creates_an_account_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_doesnt_get_validation_error_when_creating_an_account_while_being_logged_out():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully()


# Missing fields
def test_user_gets_validation_error_when_creating_an_account_with_missing_email():
    email, username, password = TestUtils.generate_credentials()

    TestWrapper.create_account_unsuccessfully(username=username, password=password, error_code=2,
                                              msg='Missing option "--email"')


def test_user_gets_validation_error_when_creating_an_account_with_missing_username():
    email, username, password = TestUtils.generate_credentials()

    TestWrapper.create_account_unsuccessfully(
        email=email, password=password, error_code=2, msg='Missing option "--username"')


# Invalid Fields
def test_user_gets_validation_error_when_creating_an_account_with_invalid_password():
    email, username, password = TestUtils.generate_credentials()

    TestWrapper.create_account_unsuccessfully(
        email=email, username=username, password='blabla', error_code=1, msg='This password is too common')
