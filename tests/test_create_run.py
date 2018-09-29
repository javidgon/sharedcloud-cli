import multiprocessing
import os
import time

from tests.constants import Image, Message, Gpu, InstanceType
from tests.test_utils import TestUtils, TestWrapper


# Workflow
def test_user_creates_a_run_without_gpu_requirements_successfully():
    parameters = '((1,),(2,))'
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
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0)

    TestWrapper.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_function=[function_name],
        expected_num_runs=1)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_user_creates_a_run_with_gpu_requirements_successfully():
    parameters = '((1,),(2,))'
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'], file=file)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU, ask_price=1.0, max_num_parallel_jobs=1, gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    p = multiprocessing.Process(target=TestUtils.start_instance, name="start_instance", kwargs={})
    p.start()
    time.sleep(5)
    run_uuid = TestWrapper.create_run_successfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0, base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    TestWrapper.check_list_runs_output(
        expected_uuid=[run_uuid],
        expected_parameters=[parameters],
        expected_base_gpu=[Gpu.TITAN_V_12GB['name']],
        expected_function=[function_name],
        expected_num_runs=1)

    p.join(5.0)  # 5 seconds of timeout
    p.terminate()

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_when_creating_by_providing_a_gpu_without_being_available():
    parameters = '((1,),(2,))'
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'

    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.check_account_output(
        expected_email=[email],
        expected_username=[username],
        expected_balance_is_zero=True
    )

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'], file=file)

    instance_uuid, instance_name = TestWrapper.create_instance_successfully(
        type=InstanceType.GPU, ask_price=1.0, max_num_parallel_jobs=1, gpu_uuid=Gpu.TITAN_V_12GB['uuid'])

    run_uuid = TestWrapper.create_run_unsuccessfully(
        function_uuid=function_uuid, parameters=parameters, bid_price=2.0,
        base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'], error_code=1, msg='this GPU model is currently not available')

    TestWrapper.delete_instance_successfully(uuid=instance_uuid)

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


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
        function_uuid=function_uuid, parameters='((1,),(2,))', bid_price=2.0,
        error_code=1, msg='you need a balance higher than 0 to create new runs')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


# Logged out
def test_user_get_validation_error_when_creating_a_run_while_being_logged_out():
    parameters = '((1,),(2,))'

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_random_seed(), parameters=parameters, bid_price=2.0,
        error_code=1, msg=Message.YOU_ARE_LOGOUT_WARNING)


# Missing fields
def test_user_get_validation_error_when_creating_a_run_with_missing_function_uuid():
    parameters = '((1,),(2,))'

    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        parameters=parameters,
        bid_price=2.0,
        error_code=2, msg='Missing option "--function-uuid"')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_run_with_missing_parameters():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_uuid(),
        bid_price=2.0,
        error_code=2, msg='Missing option "--parameters"')

    TestWrapper.delete_account_successfully()


def test_user_get_validation_error_when_creating_a_run_with_missing_bid_price():
    parameters = '((1,),(2,))'
    account_uuid, email, username, password = TestWrapper.create_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_uuid(),
        parameters=parameters,
        error_code=2, msg='Missing option "--bid-price"')

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_a_run_with_gpu_requirements_with_missing_base_gpu():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,))'
    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.TENSORFLOW_PYTHON36['uuid'], file=file)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=function_uuid,
        parameters=parameters,
        bid_price=2.0,
        error_code=1, msg='this run uses an image that requires GPU. Therefore this field is mandatory')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()

# Invalid fields

def test_user_get_validation_error_when_creating_a_run_with_invalid_value_for_bid_price():
    account_uuid, email, username, password = TestWrapper.create_account_successfully()
    parameters = '((1,),(2,))'

    TestWrapper.login_successfully(username=username, password=password)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=TestUtils.generate_uuid(),
        parameters=parameters,
        bid_price='blabla',
        error_code=2, msg='Invalid value for "--bid-price"')

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_a_run_by_providing_base_gpu_without_relying_on_gpu_image():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,))'
    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=function_uuid,
        parameters=parameters,
        bid_price=2.0,
        base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1, msg='is unnecessary because the function is not using an image that requires GPU')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()


def test_user_gets_validation_error_when_creating_a_run_with_a_too_low_bid_price():
    file = os.path.dirname(os.path.abspath(__file__)) + '/files/func_python36.py'
    parameters = '((1,),(2,))'
    account_uuid, email, username, password = TestWrapper.create_beta_account_successfully()

    TestWrapper.login_successfully(username=username, password=password)

    function_uuid, function_name = TestWrapper.create_function_successfully(
        image_uuid=Image.WEB_CRAWLING_PYTHON36['uuid'], file=file)

    TestWrapper.create_run_unsuccessfully(
        function_uuid=function_uuid,
        parameters=parameters,
        bid_price=0.0001,
        base_gpu_uuid=Gpu.TITAN_V_12GB['uuid'],
        error_code=1, msg='cannot be smaller than $0.001')

    TestWrapper.delete_function_successfully(uuid=function_uuid)

    TestWrapper.delete_account_successfully()
