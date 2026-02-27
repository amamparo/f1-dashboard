# Completed Challenges

## Improved Features (Option 5)
> Improve a backend/frontend feature of your choosing. If you choose this route, please include a brief description of the work completed.

I might be mis-interpreting this one, but I chose to make some general improvements that:
- would make tackling the other challenges easier,
- are things that I would do to any of my own repos that I intend to maintain long term, and/or
- demonstrate the value I think I could add to Excel SM's technical stack(s)

Improvements made:
- added CI check at `.github/workflows/check.yml` to ensure new changes passed lint and tests (github repo updated to block PR merges to `master` unless check passes)
- deployed to AWS: https://github.com/amamparo/f1-dashboard/pull/2
  - see it running at: https://f1-dashboard.aaronmamparo.com
  - used aws-cdk for IaC
  - API runs as an ECS Fargate service backed by an EFS volume (mounted sqlite db in EFS so that data persists through restarts)
  - UI is a static website in S3 behind a Cloudfront distrubtion