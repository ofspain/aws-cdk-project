from aws_cdk import (
    Stack,
    aws_ec2 as ec2, CfnOutput,
    aws_ssm as ssm,
)
from constructs import Construct

class VPCStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = ec2.Vpc(
            self,
        )
