import json
import pytest
from unittest.mock import patch, mock_open
from aws_cdk import App, Stack, aws_ec2 as ec2, aws_ssm as ssm, CfnOutput, assertions
from constructs import Construct

from cdk_app_project.stacks.stacks_utils.constants_util import Constants
# Import your stack and utils functions
from cdk_app_project.stacks.vpc_stack import (VPCStack,
                                              formulate_resource_id, load_configuration, provision_cfnoutput)
#
# # Mock constant used in your utils
# class Constants:
#     DEPLOYMENT_ENVIRONMENT_KEY = "deployment_environment"

@pytest.fixture
def app():
    return App()

@pytest.fixture
def stack(app):
    # Pass context to app for env
    app.node.set_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY, "dev")
    return Stack(app, "TestStack")

def test_formulate_resource_id(stack):
    resource_id = formulate_resource_id(stack, "MyResource")
    expected = f"myresource-{stack.node.id}-dev".lower()
    assert resource_id == expected

@patch("builtins.open", new_callable=mock_open, read_data='{"dev": {"max_az_number": 2}}')
def test_load_configuration(mock_file, stack):
    # Set context explicitly
    stack.node.set_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY, "dev")

    config = load_configuration(stack, "az")

    mock_file.assert_called_once_with("config/az_config.json")
    assert config == {"max_az_number": 2}

def test_load_configuration_missing_env(stack):
    stack.node.set_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY, "prod")
    with patch("builtins.open", mock_open(read_data='{"dev": {"max_az_number": 2}}')):
        with pytest.raises(KeyError):
            load_configuration(stack, "az")

def test_provision_cfnoutput(stack, app):
    my_name = "MyOutput"
    provision_cfnoutput(stack, my_name, "my-value")

    outputs = [child for child in stack.node.children if isinstance(child, CfnOutput)]
    stack_name = stack.node.id
    env_name = app.node.get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
    assert any(
        my_name.lower() in o.node.id and
        stack_name.lower() in o.node.id and
        env_name.lower() in o.node.id and
        o.value == "my-value"
        for o in outputs
    ),"failing with non expected output"


#@patch("cdk_app_project.stacks.vpc_stack.load_configuration", return_value={"max_az_number": 2})
def test_vpc_stack_creation(stack, app):
    # Set context for environment
    # app.node.set_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY, "dev")

    # Patch load_configuration to avoid file I/O and return fixed config
    with patch("cdk_app_project.stacks.vpc_stack.load_configuration", return_value={"max_az_number": 2}):
        vpc_stack = VPCStack(app, "VPCStackTest")

    template = assertions.Template.from_stack(vpc_stack)

    # Check VPC resource exists with maxAzs = 2
    template.has_resource_properties("AWS::EC2::VPC", {})

    # Check SSM Parameter created with correct parameter name
    template.has_resource_properties("AWS::SSM::Parameter", {
        "Name": "vpcstack_vpc_vpc_id",
        # The value will be a Ref to the VPC resource, so we just check presence of 'Value'
        "Type": "String",
    })

    # Check Security Group exists and has ingress rules for SSH, HTTP, HTTPS
    template.has_resource_properties("AWS::EC2::SecurityGroup", {
        "SecurityGroupIngress": [
            {"IpProtocol": "tcp", "FromPort": 22, "ToPort": 22},
            {"IpProtocol": "tcp", "FromPort": 80, "ToPort": 80},
            {"IpProtocol": "tcp", "FromPort": 443, "ToPort": 443},
        ]
    })

    # Check Outputs created for VPC ID, public and private subnet IDs
    # template.has_output("cfnoutput_vpcid-vpcstacktest-dev", {})
    # template.has_output("cfnoutput_publicsubnetid-vpcstacktest-dev", {})
    # template.has_output("cfnoutput_privatesubnetid-vpcstacktest-dev", {})

