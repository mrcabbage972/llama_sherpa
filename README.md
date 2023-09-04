<h1 align="center">
<span>Llama Sherpa</span>
</h1>

<a href="https://github.com/mrcabbage972/llama_sherpa/actions/workflows/pre-commit.yml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/mrcabbage972/llama_sherpa/pre-commit.yml?label=pre-commit)</a>

<a href="https://github.com/mrcabbage972/llama_sherpa/actions/workflows/docker-image.yml">![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/mrcabbage972/llama_sherpa/docker-image.yml?label=build-docker)</a>


A simple scheduler of dockerized tasks, built with LLM use-cases in mind.

WARNING: This project is still a work in progress and is not released.

![Alt text](doc/home.png?raw=true "Screenshot")



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

# Setup
##  Pre-requisites
Docker and docker-compose are required.
For GPU support, please install [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker).

# Quick Start
For a quick glance at how the system works, run the following command:
``` docker compose up```.
The web UI will be available at http://localhost:8004.
Please note that this is for demonstration only - the system is not secure without configuration.


## Configuration
Please create a `.env` file in the root directory of the project. The following variables are required:
```
SECRET_KEY
FIRST_SUPERUSER_USERNAME # default: admin
FIRST_SUPERUSER_PASSWORD
FIRST_SUPERUSER_EMAIL
```
A secret key can be obtained with `openssl rand -hex 32`.

Optional variables:
```
REQUIRE_LOGIN_FOR_SUBMIT # default: True
```

# Usage
## Web UI
The web UI is available at http://localhost:8004. The following features are available:
1. Create a new task.
2. View running, scheduled and completed tasks.
3. View task details, including real-time logs.
4. Manage users: create, change password, delete.
5. Pre-configure commonly used tasks.

# Roadmap
1. Add support for GPU utilization monitoring.
2. Add support for requesting a number of GPU's.
3. Add support for multiple worker machines.


# Contributing
Contributions are welcome. Please open an issue to discuss your ideas before submitting a PR.
