from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_creating_a_function_while_being_logged_out():
    r = TestUtils.create_function(
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_a_function_with_missing_name():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Missing option "--name"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_missing_runtime():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Missing option "--runtime"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_missing_both_code_and_file():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        runtime='python36'
    )
    assert r.exit_code == 2
    assert 'Either "code" or "file" parameters need to be provided' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields
def test_user_get_validation_error_when_creating_a_function_with_invalid_code():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        runtime='python36',
        code='blabla'
    )
    assert r.exit_code == 1
    assert 'needs to have the following signature' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_invalid_runtime():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        runtime='python99',
        code='def handler(event): print(2)'
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--runtime":' in r.output

    _accountTearDown(account_uuid)
