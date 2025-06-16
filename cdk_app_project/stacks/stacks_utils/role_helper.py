from aws_cdk import aws_iam as iam
from constructs import Construct


def create_task_role(scope: Construct, role_id: str, service : str) -> iam.Role:
    # Create base role
    role = iam.Role(scope, role_id,
        assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
    )

    # Attach policies based on requested services

    if service.lower() == "s3":
       role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
       )
    elif service.lower() == "secretsmanager":
       role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("SecretsManagerReadWrite")
       )
    elif service.lower() == "sqs":
       role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSQSFullAccess")
       )
    elif service.lower() == "dynamodb":
       role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonDynamoDBReadOnlyAccess")
    )
    elif service.lower() == "ssm":
       role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMReadOnlyAccess")
       )
    else:
       raise Exception(f"Unsupported service: {service}")

    return role


def create_cluster_role(scope: Construct, role_id: str, ) -> iam.Role:
    role = iam.Role(scope, role_id,
           assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
           managed_policies=[
              iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ContainerServiceforEC2Role"),
              iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMManagedInstanceCore"),
              iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchAgentServerPolicy")
           ]
    )

    return role