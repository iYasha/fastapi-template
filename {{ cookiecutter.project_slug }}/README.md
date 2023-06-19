# {{ cookiecutter.project_name }}

## Getting started
1. install docker and docker-compose if you don't already have it:\
Official **[Docker](https://docs.docker.com/engine/install/)** and **[Docker compose](https://docs.docker.com/compose/install/)** installation guide

2. Build and run the docker container:
```bash
docker-compose up --build
```

3. Visit http://localhost/docs to see the API documentation.


## Useful commands

### Run tests
```bash
make test
```

### Format code
```bash
make format
```

### Lint code
```bash
make lint
```

### Run migrate 
```bash
make migrate
```

### Install pre-commit hooks
```bash
pre-commit install
```
