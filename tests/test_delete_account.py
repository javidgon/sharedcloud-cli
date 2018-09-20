from tests.test_utils import TestUtils


# Logged out
def test_user_get_validation_error_when_deleting_an_account_while_being_logged_out():
    r = TestUtils.delete_account(
        uuid='6166a825-00be-4f5c-837c-7d1a1ffc015e',
    )

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_deleting_an_account_with_missing_uuid():
    email, username, password = TestUtils.generate_credentials()

    r = TestUtils.create_account(
        email=email,
        username=username,
        password=password
    )
    assert r.exit_code == 0
    assert 'has been created' in r.output
    account_uuid = TestUtils.extract_uuid(r.output)

    r = TestUtils.login(username, password)
    assert r.exit_code == 0

    r = TestUtils.delete_account()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output


# Invalid Fields