from constructs import Construct
from aws_cdk import (
    CfnOutput
)
import aws_cdk.aws_ec2 as ec2

class Vpc(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create vpc

        self.vpc = ec2.Vpc(self, "VPC-CDK",
                           max_azs=3,
                           cidr="10.42.0.0/16",
                           subnet_configuration=[
                              ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PUBLIC,
                               name="Public",
                               cidr_mask=24
                           ), ec2.SubnetConfiguration(
                               subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                               name="Private",
                               cidr_mask=24
                           )
                           ],
                           nat_gateways=1,
                           )
        # output

        CfnOutput(self, "VPC-ID",
                       value=self.vpc.vpc_id)