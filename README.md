# Cogat-Docker
[![CircleCI](https://circleci.com/gh/poldracklab/cogat/tree/master.svg?style=svg)](https://circleci.com/gh/poldracklab/cogat/tree/master)

Light Django application and containers for Spark and Neo4j to serve the Cognitive Atlas and manage development.


## Getting started

This project uses docker and docker-compose:


Docker:  [https://docs.docker.com/installation/](https://docs.docker.com/installation/)<br />
Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

## Setting up social authentication

To set up the social auth backend, after starting the server you will need to [follow these instructions](https://django-allauth.readthedocs.io/en/latest/installation.html#post-installation).

## Create default user

Add `MAKE_DEFAULT_USER=True` to the `.env` file in the root of the project. The user specificed in scripts/create_superuser.py will then be created on startup of the uwsgi container.
