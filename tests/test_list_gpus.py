from tests.test_utils import TestWrapper


# Workflow
def test_user_sees_the_list_of_gpus_successfully():
    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    _, uuids = TestWrapper.check_list_gpus_output(
        expected_codename=[
            'titanv',
            'teslak80',
            'titanxp',
            '1080_ti',
            'titanx',
            '1080',
            '1070',
            '1060'
        ],
        expected_num_gpus=8,
    )

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_listing_gpus_while_being_logged_out():
    TestWrapper.check_list_gpus_output(
        expected_logout_warning=True
    )

# Missing fields


# Invalid Fields
