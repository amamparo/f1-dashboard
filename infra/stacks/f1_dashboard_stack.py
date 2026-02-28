from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
    aws_certificatemanager as acm,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_efs as efs,
    aws_route53 as route53,
    aws_route53_targets as targets,
    aws_ecr_assets as ecr_assets,
    aws_s3 as s3,
    aws_secretsmanager as secretsmanager,
)
from constructs import Construct

CERT_ARN = "arn:aws:acm:us-east-1:388646735826:certificate/13746fc0-bc19-4a99-8151-187cacd349f3"
HOSTED_ZONE_NAME = "aaronmamparo.com"

UI_SUBDOMAIN = "f1-dashboard"
API_SUBDOMAIN = "f1-dashboard-api"


class F1DashboardStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        ui_domain = f"{UI_SUBDOMAIN}.{HOSTED_ZONE_NAME}"
        api_domain = f"{API_SUBDOMAIN}.{HOSTED_ZONE_NAME}"

        vpc = ec2.Vpc(
            self,
            "Vpc",
            max_azs=2,
            nat_gateways=1,
        )

        zone = route53.HostedZone.from_lookup(
            self, "Zone", domain_name=HOSTED_ZONE_NAME
        )
        cert = acm.Certificate.from_certificate_arn(self, "Cert", CERT_ARN)

        file_system = efs.FileSystem(
            self,
            "FileSystem",
            vpc=vpc,
            removal_policy=RemovalPolicy.DESTROY,
        )
        access_point = file_system.add_access_point(
            "AccessPoint",
            path="/data",
            create_acl=efs.Acl(owner_uid="1000", owner_gid="1000", permissions="755"),
            posix_user=efs.PosixUser(uid="1000", gid="1000"),
        )

        secret_key = secretsmanager.Secret(
            self,
            "JwtSecretKey",
            secret_name="f1-dashboard/secret-key",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                exclude_punctuation=True,
                password_length=64,
            ),
        )

        cluster = ecs.Cluster(
            self, "Cluster", cluster_name="f1-dashboard", vpc=vpc
        )

        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "Service",
            cluster=cluster,
            service_name="f1-dashboard",
            desired_count=1,
            runtime_platform=ecs.RuntimePlatform(
                cpu_architecture=ecs.CpuArchitecture.ARM64,
                operating_system_family=ecs.OperatingSystemFamily.LINUX,
            ),
            cpu=256,
            memory_limit_mib=512,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset(
                    "..",
                    exclude=["infra/cdk.out"],
                    platform=ecr_assets.Platform.LINUX_ARM64,
                    cache_from=[{"type": "gha"}],
                    cache_to={"type": "gha", "params": {"mode": "max"}},
                ),
                container_port=9000,
                command=["api-prod"],
                environment={
                    "PORT": "9000",
                    "DB_FILE": "/python-package/data/data.db",
                    "CORS_ORIGINS": f"https://{ui_domain}",
                },
                secrets={
                    "SECRET_KEY": ecs.Secret.from_secrets_manager(secret_key),
                },
            ),
            certificate=cert,
            domain_name=api_domain,
            domain_zone=zone,
            redirect_http=True,
            public_load_balancer=True,
        )

        fargate_service.target_group.configure_health_check(
            path="/ping",
            healthy_http_codes="200",
            interval=Duration.seconds(30),
        )

        task_def = fargate_service.task_definition
        task_def.add_volume(
            name="efs-data",
            efs_volume_configuration=ecs.EfsVolumeConfiguration(
                file_system_id=file_system.file_system_id,
                transit_encryption="ENABLED",
                authorization_config=ecs.AuthorizationConfig(
                    access_point_id=access_point.access_point_id, iam="ENABLED"
                ),
            ),
        )
        container = task_def.default_container
        container.add_mount_points(
            ecs.MountPoint(
                container_path="/python-package/data",
                source_volume="efs-data",
                read_only=False,
            )
        )

        file_system.connections.allow_default_port_from(
            fargate_service.service.connections
        )
        file_system.grant_root_access(task_def.task_role)

        site_bucket = s3.Bucket(
            self,
            "SiteBucket",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        distribution = cloudfront.Distribution(
            self,
            "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(
                    site_bucket
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            ),
            domain_names=[ui_domain],
            certificate=cert,
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",
                    ttl=Duration.seconds(0),
                ),
            ],
        )

        route53.ARecord(
            self,
            "SiteAliasRecord",
            zone=zone,
            record_name=ui_domain,
            target=route53.RecordTarget.from_alias(
                targets.CloudFrontTarget(distribution)
            ),
        )

        CfnOutput(self, "FrontendUrl", value=f"https://{ui_domain}")
        CfnOutput(self, "ApiUrl", value=f"https://{api_domain}")
        CfnOutput(self, "SiteBucketName", value=site_bucket.bucket_name)
        CfnOutput(
            self, "DistributionId", value=distribution.distribution_id
        )
