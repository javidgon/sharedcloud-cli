from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_updating_an_instance_while_being_logged_out():
    r = TestUtils.update_instance()

    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output


# Missing fields
def test_user_get_validation_error_when_updating_an_instance_with_missing_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.update_instance()
    assert r.exit_code == 2
    assert 'Missing option "--uuid"' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields
def test_user_get_validation_error_when_updating_an_instance_with_invalid_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.update_instance(
        uuid='4c3d399e-ec67-47a1-82e4-b979e534f3d9',
   )
    assert r.exit_code == 1
    assert 'Not found resource' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_price_per_hour():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.update_instance(
        name=account_uuid,
        price_per_hour='blabla',
        max_num_parallel_jobs=5
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--price_per_hour"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_updating_an_instance_with_invalid_max_num_parallel_jobs():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_instance(
        name=account_uuid,
        price_per_hour=1.5,
        max_num_parallel_jobs='blabla'
    )
    print(r.exit_code, r.output)
    assert r.exit_code == 2
    assert 'Invalid value for "--max_num_parallel_jobs"' in r.output

    _accountTearDown(account_uuid)



