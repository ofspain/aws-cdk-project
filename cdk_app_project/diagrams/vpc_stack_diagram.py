# vpc_stack_diagram.py
from diagrams import Diagram
from diagrams.aws.network import VPC, PublicSubnet, PrivateSubnet
from diagrams.aws.security import FirewallManager
from diagrams.aws.management import SystemsManagerParameterStore
from diagrams.custom import Custom
from diagrams.onprem.client import Users

with Diagram("VPCStack CDK Diagram", filename="./images/vpc_diagram",
             show=False, direction="TB"):
    # Main VPC
    vpc = VPC("VPC\n(Public & Private)")

    # Subnets inside VPC
    pub_subnet = PublicSubnet("Public Subnet")
    priv_subnet = PrivateSubnet("Private Subnet")

    # SSM Parameter Store
    ssm_param = SystemsManagerParameterStore("VPC ID Param\n(Parameter Store)")

    # Security Group
    sg = FirewallManager("EC2 Security Group")

    # Representing ingress rules as external users/services
    user = Users("Internet")

    # Diagram relationships
    vpc >> [pub_subnet, priv_subnet]
    vpc >> ssm_param
    vpc >> sg
    user >> sg  # Implicitly represents ingress (SSH, HTTP, HTTPS)
