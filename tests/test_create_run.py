import os

from tests.constants import Image, Message, Gpu
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_creates_a_run_without_gpu_requirements_successfully():
    parameter = '((1,),(2,))'
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameter)

    TestWrapper.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameter],
        expected_function=[function_name],
        expected_num_runs=1)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_creates_a_run_with_gpu_requirements_successfully():
    parameter = '((1,),(2,))'
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameter, base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    TestWrapper.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameter],
        expected_base_gpu=[Gpu.TITAN_V_12GB['name']],
        expected_function=[function_name],
        expected_num_runs=1)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

def test_user_tries_to_create_a_run_but_his_balance_is_insufficient():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=function_uuid, parameters='((1,),(2,))',
        error_code=1, msg='you need a balance higher than 0 to create new runs')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully(uuid=account_uuid)

# Logged out
def test_user_get_validation_error_when_creating_a_run_while_being_logged_out():
    parameter = '((1,),(2,))'

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_random_seed(), parameters=parameter,
        error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_creating_a_run_with_missing_function_uuid():
    parameter = '((1,),(2,))'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        parameters=parameter,
        error_code=2, msg='Missing option "--function-uuid"')

    TestWrapper.delete_account_successfully(uuid=account_uuid)



def test_user_get_validation_error_when_creating_a_run_with_missing_parameters():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_uuid(),
        error_code=2, msg='Missing option "--parameters"')

    TestWrapper.delete_account_successfully(uuid=account_uuid)
