import os

from tests.constants import Image, Message
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_delete_run_successfully():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameter = '((1,),(2,))'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameter, bid_price=2.0)

    TestWrapper.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameter],
        expected_function=[function_name],
        expected_num_runs=1)

    TestWrapper.delete_run_successfully(uuid=run_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_deleting_a_run_while_being_logged_out():
    TestWrapper.delete_run_unsuccessfully(
        uuid=TestUtils.generate_uuid(),
        error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_deleting_a_run_with_missing_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_run_unsuccessfully(error_code=2, msg='Missing option "--uuid"')

    TestWrapper.delete_account_successfully()


# Invalid Fields
def test_user_get_validation_error_when_deleting_a_run_with_invalid_uuid():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.delete_run_unsuccessfully(
        uuid=TestUtils.generate_random_seed(), error_code=2, msg='Invalid value for "--uuid"')

    TestWrapper.delete_account_successfully()
