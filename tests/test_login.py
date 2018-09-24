from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_logs_in_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_doesnt_get_logged_in_automatically_after_account_creation():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.logout_unsuccessfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

# Missing fields
def test_user_gets_validation_error_when_login_with_missing_username():
    TestWrapper.login_unsuccessfully(
        password=TestUtils.generate_random_seed(), error_code=2, msg='Missing option "--username"')

def test_user_gets_validation_error_when_login_with_missing_password():
    TestWrapper.login_unsuccessfully(
        username=TestUtils.generate_random_seed(), error_code=2, msg='Missing option "--password"')

# Invalid fields
def test_user_login_and_get_validation_error_with_invalid_credentials():
    TestWrapper.login_unsuccessfully(
        username=TestUtils.generate_random_seed(), password=TestUtils.generate_random_seed(), error_code=1, msg='Unable to log in with provided credentials')
