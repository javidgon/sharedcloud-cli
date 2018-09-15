import os
from click.testing import CliRunner

from tests.test_utils import TestUtils

runner = CliRunner()


def test_customer_performs_a_complete_workflow_with_code():
    TestUtils.login()

    _, function_uuid = TestUtils.create_function()

    _ = TestUtils.list_functions()

    _, run_uuid = TestUtils.create_run(function_uuid=function_uuid)

    _ = TestUtils.list_runs()

    _ = TestUtils.list_jobs()

    _, run_uuid = TestUtils.delete_run(uuid=run_uuid)

    _, function_uuid = TestUtils.update_function(uuid=function_uuid)

    _, function_uuid = TestUtils.delete_function(uuid=function_uuid)

    TestUtils.logout()

def test_customer_performs_a_complete_workflow_with_file():
    filepath = os.path.dirname(os.path.abspath(__file__)) + '/../examples/simple_func_python36.py'

    TestUtils.login()

    _, function_uuid = TestUtils.create_function(code=None, file=filepath)

    _ = TestUtils.list_functions()

    _, run_uuid = TestUtils.create_run(function_uuid=function_uuid)

    _ = TestUtils.list_runs()

    _ = TestUtils.list_jobs()

    _, run_uuid = TestUtils.delete_run(uuid=run_uuid)

    _, function_uuid = TestUtils.update_function(uuid=function_uuid, code=None, file=filepath)

    _, function_uuid = TestUtils.delete_function(uuid=function_uuid)

    TestUtils.logout()


# def test_provider_performs_complete_workflow():
#     # TODO: Only the Start instance function is pending
#     # TODO: Clarify messages like: This machine seems to already contain an instance. Please delete it before creating a new one.
#     TestUtils.login()
#
#     # Delete existing machine in case that only exists in the system
#     _, instance_uuid = TestUtils.delete_instance()
#
#     _, instance_uuid = TestUtils.create_instance()
#
#     _, instance_uuid = TestUtils.delete_instance(instance_uuid)
#
#     TestUtils.logout()
