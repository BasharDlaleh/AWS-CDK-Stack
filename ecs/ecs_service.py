from constructs import Construct
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecsPatterns,
    CfnOutput,
    aws_elasticloadbalancingv2 as elbv2,
)

class ECSService(Construct):

    def __init__(self, scope: Construct, id: str, vpc, cache_cluster, nodejs_cluster, database, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # create nodejs cluster service

        self.nodejs_ecs_service = ecsPatterns.ApplicationLoadBalancedEc2Service(
            self, "NodejsEcsService",
            cluster=nodejs_cluster, 
            desired_count=1,
            memory_limit_mib=512,
            listener_port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            task_image_options=ecsPatterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_registry("bashar1993/nodejs-ecs"),
                container_name="nodejs-container",
                container_port=3000,
                environment={
                    "DB_HOST": database.db_instance_endpoint_address,
                    "DB_NAME": "aligent",
                    "DB_USER": "admin",
                    "DB_PASSWORD": "adminPassword123",
                }
            )
        )

        # allow traffic coming from LB to backend service

        self.nodejs_ecs_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(3000),
            description="Allow http inbound from VPC"
        )

        # output 

        CfnOutput(
            self, "BackendLoadBalancerDNS",
            value=self.nodejs_ecs_service.load_balancer.load_balancer_dns_name
        )
        CfnOutput(
            self, "NodejsService",
            value=self.nodejs_ecs_service.service.service_name
        )

        # create varnish cluster service

        self.cache_ecs_service = ecsPatterns.ApplicationMultipleTargetGroupsEc2Service(self, "CacheEcsService",
            cluster=cache_cluster,
            desired_count=1,
            memory_limit_mib=512,
            task_image_options=ecsPatterns.ApplicationLoadBalancedTaskImageProps(
                image=ecs.ContainerImage.from_registry("bashar1993/varnish-nginx-ecs"),
                container_name="varnish-container",
                container_ports=[80, 8080],
                environment={
                    "ELB_URL": "http://"+self.nodejs_ecs_service.load_balancer.load_balancer_dns_name,
                }
            )
        )
        
        # allow traffic coming from LB to varnish service

        self.cache_ecs_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(80),
            description="Allow http inbound from VPC"
        )

        self.cache_ecs_service.service.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(8080),
            description="Allow http inbound from VPC"
        )

        # output 

        CfnOutput(
            self, "FrontendLoadBalancerDNS",
            value=self.cache_ecs_service.load_balancer.load_balancer_dns_name
        )