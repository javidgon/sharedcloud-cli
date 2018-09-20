from tests.test_utils import TestUtils


# Logged out
def test_user_doesnt_get_validation_error_when_creating_an_account_while_being_logged_out():
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

    r = TestUtils.delete_account(
        uuid=account_uuid
    )
    assert r.exit_code == 0
    assert 'was deleted' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_an_account_with_missing_email():
    email, username, password = TestUtils.generate_credentials()


    r = TestUtils.create_account(
        username=username,
        password=password
    )

    assert r.exit_code == 2
    assert 'Missing option "--email"' in r.output


def test_user_get_validation_error_when_creating_an_account_with_missing_username():
    email, username, password = TestUtils.generate_credentials()

    r = TestUtils.create_account(
        email=email,
        password=password
    )
    assert r.exit_code == 2
    assert 'Missing option "--username"' in r.output


def test_user_get_validation_error_when_creating_an_account_with_missing_password():
    email, username, password = TestUtils.generate_credentials()

    r = TestUtils.create_account(
        email=email,
        username=username
    )
    assert r.exit_code == 2
    assert 'Missing option "--password"' in r.output


#Invalid Fields
def test_user_get_validation_error_when_creating_an_account_with_invalid_password():
    pass
