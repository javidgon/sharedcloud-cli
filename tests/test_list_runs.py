import os

from tests.constants import Image
from tests.test_utils import TestWrapper


# Workflow
def test_user_sees_the_list_of_runs_successfully():
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
        expected_num_runs=1
    )

    TestWrapper.delete_run_successfully(uuid=run_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_gets_validation_error_when_listing_runs_while_being_logged_out():
    TestWrapper.check_list_runs_output(
        expected_logout_warning=True
    )
# Missing fields


# Invalid Fields
