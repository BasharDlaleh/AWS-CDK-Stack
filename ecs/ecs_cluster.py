from constructs import Construct
from vpc.vpc import Vpc
from ecs.ecs_service import ECSService
from rds.rds_mysql import RDSDatabase
from aws_cdk import (
    aws_ecs as ecs,
    aws_ec2 as ec2,
    Stack,
    CfnOutput
)

class ECSCluster(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        # create VPC

        self.vpc = Vpc(self, 'Aligent-VPC')

        # create DB

        self.rds = RDSDatabase(self, 'Aligent-RDS', self.vpc.vpc)

        # create Cache Cluster

        self.cache_cluster = ecs.Cluster(
            self, 'CachEcsCluster',
            vpc=self.vpc.vpc
        )
        
        self.cache_cluster.add_capacity('DefaultAutoScalingGroupCapacity', 
            instance_type= ec2.InstanceType("t2.micro"),
            desired_capacity= 1,
        );

        # create Backend Cluster

        self.nodejs_cluster = ecs.Cluster(
            self, 'NodejsEcsCluster',
            vpc=self.vpc.vpc
        )

        self.nodejs_cluster.add_capacity('DefaultAutoScalingGroupCapacity', 
            instance_type= ec2.InstanceType("t2.micro"),
            desired_capacity= 1,
        )
        
        # create Nodejs and Varnish services

        ECSService(self, "ECS-Service", vpc= self.vpc.vpc, cache_cluster=self.cache_cluster, nodejs_cluster=self.nodejs_cluster, database=self.rds.db_mysql)

        # output 
        
        CfnOutput(
            self, "CacheCluster",
            value=self.cache_cluster.cluster_name
        )

        CfnOutput(
            self, "NodejsCluster",
            value=self.nodejs_cluster.cluster_name
        )