from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_starting_an_instance_while_being_logged_out():
    r = TestUtils.start_instance()

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_starting_an_instance_with_missing_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.start_instance()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    _accountTearDown(account_uuid)

def test_user_get_validation_error_when_starting_an_instance_with_missing_seconds():
    # TODO: This can only be done after we figure out how to stop the process
    pass

# Invalid Fields
def test_user_get_validation_error_when_starting_an_instance_with_invalid_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.start_instance(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9'
    )
    assert r.exit_code == 0
    assert 'Not found Instance' in r.output

    _accountTearDown(account_uuid)
