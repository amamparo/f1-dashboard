#!/usr/bin/env python3
import os

import aws_cdk as cdk

from stacks.f1_dashboard_stack import F1DashboardStack

app = cdk.App()
F1DashboardStack(
    app,
    "F1DashboardStack",
    env=cdk.Environment(
        account=os.environ["CDK_DEFAULT_ACCOUNT"],
        region=os.environ["CDK_DEFAULT_REGION"],
    ),
)
app.synth()
