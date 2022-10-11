from constructs import Construct
from aws_cdk import (
    aws_rds as rds,
    aws_ec2 as ec2,
    CfnOutput,
    Duration,
    SecretValue
)

class RDSDatabase(Construct):

    def __init__(self, scope: Construct, id: str, vpc, **kwargs) -> None:
        super().__init__(scope, id, *kwargs)

        # create rds
        
        self.db_mysql = rds.DatabaseInstance(self, "MySQL8",
                                        engine=rds.DatabaseInstanceEngine.mysql(
                                            version=rds.MysqlEngineVersion.VER_8_0_21
                                        ),
                                        instance_type=ec2.InstanceType("t2.micro"),
                                        vpc=vpc,
                                        multi_az=False,
                                        publicly_accessible=True,
                                        allocated_storage=10,
                                        storage_type=rds.StorageType.GP2,
                                        deletion_protection=False,
                                        delete_automated_backups=True,
                                        backup_retention=Duration.days(0),
                                        database_name= 'aligent',
                                        credentials=rds.Credentials.from_password(username= "admin", password= SecretValue(value= "adminPassword123")),
                                        )
        
        # allow traffic from vpc 

        self.db_mysql.connections.security_groups[0].add_ingress_rule(
            peer = ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection = ec2.Port.tcp(3306),
            description="Allow inbound traffic from VPC"
        )

        # output 

        CfnOutput(
            self, "DBAddress",
            value=self.db_mysql.db_instance_endpoint_address
        )