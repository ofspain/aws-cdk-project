import json
from typing import Dict, Any

from aws_cdk import Stack, CfnOutput
from constructs import Construct

from cdk_app_project.stacks.stacks_utils.constants_util import Constants


def formulate_resource_id(parent: Stack, resource_type: str)->str:
    env = parent.node.try_get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
    resource_id = parent.node.id

    return f"{resource_type}-{resource_id}-{env}".lower()

def load_configuration(parent: Construct, entity: str) -> Dict[str, Any]:
    """Load configuration based on environment"""
    context = parent.node.get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
    env = parent.node.try_get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
    if not env:
        raise ValueError("Deployment environment is not set in context")

    with open(f"config/{entity}_config.json") as f:
        loaded_config = json.load(f)

    if env not in loaded_config:
        raise KeyError(f"Configuration for environment '{env}' not found in {entity}_config.json")

    return loaded_config[env]


def provision_cfnoutput(parent: Stack, name: str, value: str):
    CfnOutput(parent, formulate_resource_id(parent, f"CfnOutput_{name}"), value=value)

