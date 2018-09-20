from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_updating_a_function_while_being_logged_out():
    r = TestUtils.update_function(
        runtime='python36'
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_updating_a_function_with_missing_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.update_function(
        runtime='python36'
    )
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields

def test_user_get_validation_error_when_updating_a_function_with_invalid_uuid():
    email, username, password, account_uuid = _accountSetUp()


    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name=account_uuid,
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 1
    assert 'Not found resource with UUID' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_updating_a_function_with_invalid_code():
    email, username, password, account_uuid = _accountSetUp()


    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name=account_uuid,
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 1
    assert 'Not found resource' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_updating_a_function_with_invalid_runtime():
    email, username, password, account_uuid = _accountSetUp()


    r = TestUtils.update_function(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
        name=account_uuid,
        runtime='python99',
        code='def handler(event): print(2)'
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--runtime":' in r.output

    _accountTearDown(account_uuid)


