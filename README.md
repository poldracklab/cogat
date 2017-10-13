# Cogat-Docker
[![CircleCI](https://circleci.com/gh/poldracklab/cogat/tree/master.svg?style=svg)](https://circleci.com/gh/poldracklab/cogat/tree/master)

Django application and containers for Spark and Neo4j to serve the Cognitive Atlas and manage development.


## Getting started

This project uses docker and docker-compose:


Docker:  [https://docs.docker.com/installation/](https://docs.docker.com/installation/)<br />
Docker Compose: [https://docs.docker.com/compose/install/](https://docs.docker.com/compose/install/)

Docker file for neo4j taken from [https://github.com/kbastani/docker-neo4j](https://github.com/kbastani/docker-neo4j) and modified to do some data imports.

## Create default user

Add `MAKE_DEFAULT_USER=True` to the `.env` file in the root of the project. The user specificed in scripts/create_superuser.py will then be created on startup of the uwsgi container.

## Old users

The import contianer looks for an environment variable named `MYSQL_DUMP` and uses its value as the sql dump file to import into mysql. This variable should be defined in `.env`. The users will be imported when the import container is started. It should be started with docker-compose using the `docker-compose-import.yml` config file.
