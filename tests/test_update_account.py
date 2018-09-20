from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_updating_an_account_while_being_logged_out():
    email, username, password = TestUtils.generate_credentials()

    r = TestUtils.update_account(
        uuid='6166a825-00be-4f5c-837c-7d1a1ffc015e',
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_updating_an_account_with_missing_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.update_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields
