# ESM FullStack Challenge
Challenge for ESM FullStack candidates

## Overview:
You are tasked with updating a Formula One Web App. The backend is written in Python (FastAPI), the frontend is written in JavaScript (React-Admin), and the underlying data is housed in a SQLite DB. There are multiple ways to complete this assessment, but we ask that you update both the frontend and backend so that we can comprehensively assess the skills required for this role. Please select one (or more) of the following options to complete:
1. The Web App is currently read-only. In order to keep data up-to-date, we would like you to upgrade the Web App from a read-only app to a simple CRUD app. Please update the 'Drivers' UI and API with the following capabilities: Create a new driver, Update a pre-existing driver, and Delete a pre-existing driver. You can find related code in `dashboard/src/pages/drivers.tsx` and `esm_fullstack_challenge/routers/drivers.py`.
2. The current UI/UX of the Web App feels disconnected. In order to remedy this, please update the 'Races' UI/UX. When clicking on a race for a more detailed view, please create a tabbed view displaying data related to the race. Please display data related to the race circuit, race drivers, and race constructors. You can find related code in `dashboard/src/pages/races.tsx` and `esm_fullstack_challenge/routers/races.py`.
3. The Web App does not display data in a meaningful way. Please add a dashboard that provides easy to digest insights. There should be at least 2 or more visualizations. You can find related code in `dashboard/src/pages/dashboard.tsx` and `esm_fullstack_challenge/routers/dashboard.py`.
4. The Web App currently uses a static JSON file for authentication. Please add proper user authentication and management. You can find related code in `dashboard/src/authProvider.ts`.
5. Improve a backend/frontend feature of your choosing. If you choose this route, please include a brief description of the work completed.

This challenge is meant to take anywhere from 1-4 hours and this will be taken into consideration when reviewing any work submitted.

## Getting Started
The easiest way to get started is by running the following command:
```
make run
```
This uses Docker Compose to launch two containerized services (`ui`, `api`) and mounts the `dashboard/src` and `esm_fullstack_challenge` folders which enables hot reload of the files as you work on them.


Alternatively, you can launch the applications individually by running:
```
make api
```
and (in a separate terminal)
```
make ui
```
This launches the applications without docker but requires you to have Python (v3.13+), NodeJS (v22.17.0+), and Yarn (v1.22.22+) installed.

## Submitting Work
Please create a public GitHub repo and share the link via email.

## Criteria
* The bare minimum requirement is that the Web App is able to run using the following command:
    ```
    make run
    ```
* Software development best practices are encouraged, but not required.
* Any documentation provided will help us better understand your work.
* Please take no longer than 72 hours to complete the challenge once you have begun.
