# Completed Challenges

# Other General Improvements
- added CI check at `.github/workflows/check.yml` to ensure new changes passed lint and tests (and updated github repo to block PR merges to `master` unless check passes)
- deployed to AWS: https://github.com/amamparo/f1-dashboard/pull/2
  - see it running at: https://f1-dashboard.aaronmamparo.com
  - [aws-cdk](https://aws.amazon.com/cdk/) for IaC
  - API runs as an ECS Fargate service backed by an EFS volume (mounted sqlite db in EFS so that data persists through restarts)
  - UI is a static website in S3 behind a Cloudfront distrubtion