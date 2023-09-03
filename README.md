# Llama Sherpa
WARNING: This project is still a work in progress and is not released.


## Motivation
You spent a lot of $$$ for a brand new 8xA100 machine so that your Machine Learning team can train LLM's. A month later it turns out that:
1. Everyone is logging in with the "ubuntu" user and messing up each other's environments.
2. Some people leave their Jupyter notebooks running without releasing GPU's.
3. Getting an available GPU usually involves slacking the entire team and threatening them with a restaet.
4. IT department is complaining that your GPU utilization is too low.

Now you want to restore some semblance of order, which would involve fair and transparent allocation and good resource utilization. 
You begin to look into available tools and discover that they are either difficult to use, requires an entire team to maintain, or both.

This simple task scheduling system is designed to fill that gap. It provides the following features:
1. Very simple installation.
2. All actions can be done either via UI or a REST API.
3. Environment isolation is achieved by requiring every task to be a Docker container.
4. Tracking of running, scheduled and completed tasks.
5. Each task can request a number of GPU's. It will be queued until the requested resources are available.
6. Commonly used tasks can be pre-configured to be scheduled with one click.

# Quick Start
To start the system, run the following command:
``` docker compose up```.
The web UI will be available at http://localhost:8004.

# Contributing
Contributions are welcome. Please open an issue to discuss your ideas before submitting a PR.
