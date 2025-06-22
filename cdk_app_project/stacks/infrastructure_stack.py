import json

from cdk_app_project.stacks.stacks_utils.basic_util import formulate_resource_id, load_configuration
from cdk_app_project.stacks.stacks_utils.cloudwatch_util import get_cloudwatch_config
from cdk_app_project.stacks.stacks_utils.constants_util import Constants
from cdk_app_project.stacks.stacks_utils.role_helper import create_cluster_role
from cdk_app_project.stacks.vpc_stack import VPCStack

from constructs import Construct
from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cw_actions,
    aws_logs as logs,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_ecs as ecs,
    aws_autoscaling as autoscaling,
    CfnOutput, Duration
)

def get_user_data(meta_data:dict[str,object]) -> ec2.UserData:
    cluster_name = str(meta_data.get("cluster_name"))
    cloudwatch_config = get_cloudwatch_config(cluster_name)

    user_data = ec2.UserData.for_linux()
    user_data.add_commands(
        "yum install -y amazon-cloudwatch-agent",
        "mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/"
    )

    user_data.add_commands(
        f'echo \'{json.dumps(cloudwatch_config)}\' > /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json',
        "/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s"
    )

    return user_data


class InfraStack(Stack):
    def __init__(self, scope: Construct, stack_id: str, vpc_stack: VPCStack, app_ports: [int],  **kwargs) -> None:
        super().__init__(scope, stack_id, **kwargs)

        self.vpc = vpc_stack.vpc
        self.security_group = vpc_stack.ec2_sg

        [self.security_group.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(p), f"Allow traffic on port {p}") for p
         in app_ports]

        self.ec2_role = create_cluster_role(self, formulate_resource_id(self, "EcsEc2ServiceRole"))

        ec2_features = load_configuration(self, 'ec2')
        env_name = self.node.try_get_context(Constants.DEPLOYMENT_ENVIRONMENT_KEY)
        self.cluster_name ="ecs-cluster_"+env_name
        user_data = get_user_data({"cluster_name":self.cluster_name})

        launch_template = ec2.LaunchTemplate(
            self, formulate_resource_id(self,"LaunchTemplate"),
            instance_type=ec2.InstanceType(ec2_features.get("instance_type")),
            machine_image=ecs.EcsOptimizedImage.amazon_linux2(),  # Or ec2.MachineImage.latest_amazon_linux2()
            role=self.ec2_role,
            security_group=self.security_group,
            user_data=user_data,
            require_imdsv2=True
        )

        self.auto_scaling_group = autoscaling.AutoScalingGroup(
            self, formulate_resource_id(self, "AutoScalingGroup"),
            vpc=self.vpc,
            # instance_type=ec2.InstanceType(ec2_features.get("instance_type")),
            #machine_image=ecs.EcsOptimizedImage.amazon_linux2(),
            #role=self.ec2_role,
            #security_group=self.security_group,
            #user_data=user_data,
            # require_imdsv2 = True,
            min_capacity=ec2_features.get("min_capacity", 1),
            max_capacity=ec2_features.get("max_capacity", 2),
            desired_capacity=ec2_features.get("desired_capacity", 1),
            vpc_subnets=ec2.SubnetSelection(
                subnets=self.vpc.public_subnets
                # Or, if locking down:
                # subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            launch_template=launch_template

        )

        self.add_target_tracking_scaling(target_cpu_utilization=50)

        self.cluster = ecs.Cluster(self, "EcsCluster", cluster_name=self.cluster_name,
                                   vpc=self.vpc, container_insights=True)

        self.capacity_provider = ecs.AsgCapacityProvider(self, "AsgCapacityProvider",
                                                         auto_scaling_group=self.auto_scaling_group,
                                                         enable_managed_scaling=True
                                                         )
        self.cluster.add_asg_capacity_provider(self.capacity_provider)

        cloudwatch.Alarm(
            self, "IncreaseEC2Alarm",
            alarm_name="increase-ec2-alarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            evaluation_periods=2,
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                statistic="Average",
                period=Duration.seconds(120),
                # note this is necessary for logging to cloudwatch rather than a topic
                dimensions_map={
                    "AutoScalingGroupName": self.auto_scaling_group.auto_scaling_group_name
                }
            ),
            threshold=70,
            alarm_description="This metric monitors ec2 cpu utilization, if it goes above 70% for 2 periods it will trigger an alarm.",
            ## for loging into a topic
            # alarm_actions=[
            #     topic.topic_arn,
            #     increase_policy.ref  # This will resolve to the ARN at deploy time
            # ],
        )

        # Reduce EC2 alarm
        cloudwatch.Alarm(
            self, "ReduceEC2Alarm",
            alarm_name="reduce-ec2-alarm",
            comparison_operator=cloudwatch.ComparisonOperator.LESS_THAN_OR_EQUAL_TO_THRESHOLD,
            evaluation_periods=2,
            metric=cloudwatch.Metric(
                namespace="AWS/EC2",
                metric_name="CPUUtilization",
                statistic="Average",
                period=Duration.seconds(120),
                # note this is necessary for logging to cloudwatch rather than a topic
                dimensions_map={
                    "AutoScalingGroupName": self.auto_scaling_group.auto_scaling_group_name
                }
            ),
            threshold=40,
            alarm_description="This metric monitors ec2 cpu utilization, if it goes below 40% for 2 periods it will trigger an alarm.",
            ## log to a topic
            # alarm_actions=[
            #     topic.topic_arn,
            #     increase_policy.ref  # Note: same policy as above (per Terraform)
            # ],
        )

        CfnOutput(
            self, "ClusterName",
            value=self.cluster.cluster_name
        )

    def add_target_tracking_scaling(self,
                                    target_cpu_utilization: int = 50,
                                    disable_scale_in: bool = False,
                                    cooldown_minutes: int = 5) -> None:
        """
        Adds a CPU-based target tracking scaling policy to the AutoScalingGroup.
        """
        self.auto_scaling_group.scale_on_cpu_utilization(
            id=formulate_resource_id(self, "TargetTrackingPolicy"),
            target_utilization_percent=target_cpu_utilization,
            cooldown=Duration.minutes(cooldown_minutes),
            disable_scale_in=disable_scale_in,
          #  policy_name=f"{name}CpuTargetTracking"
        )