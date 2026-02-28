# Completed Challenges

## Add Meaningful Visualizations To Dashboard (#3)

> The Web App does not display data in a meaningful way. Please add a dashboard that provides easy to digest insights. There should be at least 2 or more visualizations. You can find related code in `dashboard/src/pages/dashboard.tsx` and `esm_fullstack_challenge/routers/dashboard.py`.

- Championship Points Progression
  - Interactive line chart showing how drivers' championship points accumulate round-by-round throughout a season
  - Displays the top 10 drivers by final standings, making it easy to see lead changes and momentum shifts
- Season selector dropdown lets you browse any season from 1950 to present

- Constructor Wins by Season
  - Stacked bar chart showing race wins per constructor across all available seasons
  - Visualizes which constructors dominated each era and how competitive balance has shifted over time


# Other General Improvements
- added CI check at `.github/workflows/check.yml` to ensure new changes passed lint and tests (and updated github repo to block PR merges to `master` unless check passes)
- deployed to AWS: https://github.com/amamparo/f1-dashboard/pull/2
  - see it running at: https://f1-dashboard.aaronmamparo.com
  - [aws-cdk](https://aws.amazon.com/cdk/) for IaC
  - API runs as an ECS Fargate service backed by an EFS volume (mounted sqlite db in EFS so that data persists through restarts)
  - UI is a static website in S3 behind a Cloudfront distrubtion