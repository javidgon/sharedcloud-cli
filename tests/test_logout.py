from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_logs_out_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.logout_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)


def test_user_gets_logout_automatically_after_account_deletion():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

    TestWrapper.logout_unsuccessfully()


def test_user_gets_validation_error_if_he_is_already_logout():
    TestWrapper.logout_unsuccessfully()
