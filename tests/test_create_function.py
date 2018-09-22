from tests.test_utils import TestUtils, _accountSetUp, _accountTearDown


# Logged out
def test_user_get_validation_error_when_creating_a_function_while_being_logged_out():
    r = TestUtils.create_function(
        image_uuid='e7e2e061-444d-41c4-8a74-fe137947dfa7',
        code='blabla'
    )
    assert r.exit_code == 1
    assert 'You seem to be logged out. Please log in first' in r.output

# Missing fields
def test_user_get_validation_error_when_creating_a_function_with_missing_name():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        image_uuid='e7e2e061-444d-41c4-8a74-fe137947dfa7',
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Missing option "--name"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_missing_image_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        code='blabla'
    )
    assert r.exit_code == 2
    assert 'Missing option "--image_uuid"' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_missing_both_code_and_file():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        image_uuid='e7e2e061-444d-41c4-8a74-fe137947dfa7'
    )
    assert r.exit_code == 2
    assert 'Either "code" or "file" parameters need to be provided' in r.output

    _accountTearDown(account_uuid)


# Invalid Fields
def test_user_get_validation_error_when_creating_a_function_with_invalid_code():
    email, username, password, account_uuid = _accountSetUp()
    r, uuids = TestUtils.check_list_images_output(
        expected_name=['standard', 'web-crawling', 'web-crawling'],
        expected_runtime=['node8', 'python27', 'python36'],
        expected_description=[
            'An image with standard libraries',
            'An image with web crawling libraries',
            'An image with web crawling libraries',
        ],
        expected_num_installations=['0', '0', '0'],
        expected_num_images=3
    )

    r = TestUtils.create_function(
        name=account_uuid,
        image_uuid=uuids[0],
        code='blabla'
    )
    print(r.output)
    assert r.exit_code == 1
    assert 'needs to have the following signature' in r.output

    _accountTearDown(account_uuid)


def test_user_get_validation_error_when_creating_a_function_with_invalid_image_uuid():
    email, username, password, account_uuid = _accountSetUp()

    r = TestUtils.create_function(
        name=account_uuid,
        image_uuid='blabla',
        code='def handler(event): print(2)'
    )
    assert r.exit_code == 2
    assert 'Invalid value for "--image_uuid":' in r.output

    _accountTearDown(account_uuid)

test_user_get_validation_error_when_creating_a_function_with_invalid_code()