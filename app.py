#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_app_project.cdk_app_project_stack import CdkAppProjectStack


app = cdk.App()

deployment_env_name = app.node.try_get_context("environment")
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


CdkAppProjectStack(app, "CdkAppProjectStack",

    env=aws_env,
    env_name=deployment_env_name,  #

                   )

app.synth()
