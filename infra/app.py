#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.f1_dashboard_stack import F1DashboardStack

app = cdk.App()
F1DashboardStack(app, "F1DashboardStack")
app.synth()
