#!/usr/bin/env python3
import aws_cdk as cdk

from ecs.ecs_cluster import ECSCluster

app = cdk.App()

cluster_stack = ECSCluster(app, "ECS-Stack")

app.synth()
