#!/usr/bin/env python3
import os
import aws_cdk as cdk
from cdk_app_project.cdk_app_project_stack import CdkAppProjectStack
from cdk_app_project.stacks.dependency_stacks.db_stack import RdsStack, DBEngineType
from cdk_app_project.stacks.infrastructure_stack import InfraStack
from cdk_app_project.stacks.stacks_utils.constants_util import Constants
from cdk_app_project.stacks.vpc_stack import VPCStack

app = cdk.App()

deployment_env_name = app.node.try_get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
if deployment_env_name is None:
    raise ValueError("Missing required context value: 'environment'. Pass via --context environment=dev")

valid_envs = {"dev", "staging", "prod"}
if deployment_env_name not in valid_envs:
    raise ValueError(f"Invalid environment '{deployment_env_name}'. Must be one of {valid_envs}")

# If you don't specify 'env', this stack will be environment-agnostic.
    # Account/Region-dependent features and context lookups will not work,
aws_env={
   'account': os.environ['CDK_DEFAULT_ACCOUNT'],
   'region': os.environ['CDK_DEFAULT_REGION']
}
# or: #account_details=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION'))

vpc_stack = VPCStack(app, "VPCStack", env=aws_env)
rds_stack = RdsStack(app,  DBEngineType.POSTGRES,"RDSStack", vpc_stack,  env=aws_env)
infra_stack = InfraStack(app, "InfraStack", vpc_stack, [],  env=aws_env)

app.synth()
#C:\Users\oluwafemi.ayeni\PycharmProjects\cdk_app_project\cdk_app_project\config
