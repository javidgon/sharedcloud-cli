from tests.test_utils import TestWrapper


# Workflow
def test_user_sees_his_account_information_successfully():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_listing_an_account_while_being_logged_out():
    TestWrapper.check_account_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid Fields
