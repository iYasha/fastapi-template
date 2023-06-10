<div align="center">

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

</div>

<br />
<div align="center">
  <h3 align="center">FastAPI Backend Template</h3>

  <p align="center">
    Production ready template for FastAPI backend using Asyncio, SQLAlchemy, PostgreSQL and Docker
    <br />
    <br />
    <a href="https://github.com/iYasha/fastapi-template/issues">Report Bug</a>
    ·
    <a href="https://github.com/iYasha/fastapi-template/issues">Request Feature</a>
  </p>
</div>

## Features
- Python 3.9
- **[FastAPI](https://fastapi.tiangolo.com/)** as a main web framework
- **[SQLAlchemy Core](https://docs.sqlalchemy.org/en/latest/core/)** for working with databases
- **[Alembic](https://alembic.sqlalchemy.org/en/latest/)** for database migrations
- **[PostgreSQL](https://www.postgresql.org/)** as main database
- **[Docker-Compose](https://docs.docker.com/compose/)** for development and production
- **[Poetry](https://python-poetry.org/)** for dependency management
- **[Pytest](https://docs.pytest.org/en/stable/)** for tests
- **[Black](https://github.com/psf/black)**, **[Flake8](https://flake8.pycqa.org/en/latest/)**, **[Mypy](http://mypy-lang.org/)** for code formatting and linting
- **[Sentry](https://sentry.io/welcome/)** for error tracking
- **[Uvicorn](https://www.uvicorn.org/)** as ASGI server
- **[Traefik](https://traefik.io/traefik/)** as reverse proxy and load balancer
- **[Redis](https://redis.io/)** as a message broker and for caching
- Ready to use **file management**, **OTP authentication** using **JWT**, **scheduled tasks** and **background tasks**
- Optional **[Celery](https://docs.celeryproject.org/en/stable/)** for background tasks
- Optional **Frontend** container configuration using **[Nginx](https://www.nginx.com/)**

## Getting Started:
First, install cookiecutter if you don't already have it:
```bash
pip3 install cookiecutter
```

Second, install docker and docker-compose if you don't already have it:\
Official **[Docker](https://docs.docker.com/engine/install/)** and **[Docker compose](https://docs.docker.com/compose/install/)** installation guide

Finally, generate your project:
```bash
cookiecutter https://github.com/iyasha/fastapi-template.git
```

## Development
* Install [Poetry](https://python-poetry.org/docs/#installation)
* Go to the project directory: 
```bash
cd your_project_name
```
* Install dependencies: 
```bash
poetry install
```
* Run database and celery (optional) containers:
```bash
docker-compose up -d db celeryworker
```
* Change database and redis host in `.env` file:
```
POSTGRES_HOST=localhost
REDIS_HOST=localhost
```
* Create database tables:
```bash
alembic revision --autogenerate -m "init"
alembic upgrade head
```

Next steps are optional and depends on your IDE. You can skip them if you don't need them.

### PyCharm configuration for development
* Install plugin [.env files support](https://plugins.jetbrains.com/plugin/9525--env-files-support)
* Open project in PyCharm and create interpreter from Poetry virtual environment
* Add **Python interpreter** to Run configurations: `Serve` and `Celery`(Optional)
  ![PyCharm Run Configurations](https://raw.githubusercontent.com/iYasha/fastapi-template/main/images/pycharm_run_configuration.png)
* Create file watcher for formatting and linting [Guide Here](https://melevir.medium.com/pycharm-loves-flake-671c7fac4f52):
  ![PyCharm File Watcher](https://raw.githubusercontent.com/iYasha/fastapi-template/main/images/pycharm_flake_file_watcher_configuration.png)
* Run `Serve` and `Celery`(Optional) configuration and go to http://localhost:8000/docs

### Other IDEs
* Create virtual environment using Poetry
* Run `uvicorn main:app --reload --port 8000` for development
* Run `celery worker -A src.tasks -l INFO -Q main-queue -c 1` for celery (optional)
* Go to http://localhost:8000/docs

### Install pre-commit hooks
```bash
pre-commit install
```

## Input variables
### Base project input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `project_name` | Project name              | `FastAPI Template`     |
| `enviroment` | Project environment       | `production`           |
| `version` | Project version           | `0.1.0`                |
| `author_name` | Author name               | None                   |
| `author_email` | Author email              | None                   |
| `full_domain` | Full domain name          | `http://localhost`     |
| `secret_key` | Secret key for JWT        | Generate random string |
| `docs_suffix` | Swagger docs suffix       | `docs`                 |
| `sentry_dsn` | [Sentry DSN](https://docs.sentry.io/product/sentry-basics/dsn-explainer/)                        | None                   |
| `traefik_public_network_is_external` | [Guide](https://community.traefik.io/t/setting-up-traefik-for-docker-and-external-services/14151) | `False`                |

### Database input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `db_user` | Database username         | `postgres`             |
| `db_password` | Database password         | Generate random string |
| `db_name` | Database name             | `app`                  |
| `db_host` | Database host             | `db`                   |
| `db_port` | Database port             | `5432`                 |

### Redis input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `redis_host` | Redis host                | `redis`                |
| `redis_port` | Redis port                | `6379`                 |
| `redis_db` | Redis database            | `0`                    |

### Email input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `email_sender` | Email sender              | None                   |
| `email_host` | Email smtp host           | None                   |
| `email_port` | Email smtp port           | None                   |
| `email_username` | Email smtp username     | None                   |
| `email_password` | Email smtp password     | None                   |

### Celery input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `celery_worker_concurrency` | Celery worker concurrency | `1`                    |
| `add_celery` | If 'y' then celery container and celery utils will be add to the project files                   | `y`                    |

### Other input variables
| Variable | Description               | Default value          |
| --- |---------------------------|------------------------|
| `create_frontend_container_configuration` | If 'y' then nginx container will be add to docker-compose files                                  | `y`                    |
| `create_watchtower_configuration` | If 'y' then watchtower container will be add to docker-compose files                              | `y`                    |

## Scheduler
For scheduling tasks you need to set up cron job in your server. For example:
```bash
* * * * * docker exec backend python manage.py schedule
```

## Project structure
```
.
├─ alembic
├─ database
├─ docker
├─ media
├─ redis
├─ src
│  ├─ api
│  │  ├─ v1
│  │  │  └─ module_name
│  │  │     ├─ models.py
│  │  │     ├─ enums.py
│  │  │     ├─ repositories.py
│  │  │     ├─ schemas.py
│  │  │     └─ services.py
│  │  └─ router.py
│  ├─ commands
│  │  ├─ base.py
│  │  ├─ schedule.py
│  │  └─ your_command.py
│  ├─ sdk
│  │  ├─ exceptions
│  │  │  ├─ exception_handler_mapping.py
│  │  │  ├─ exceptions.py
│  │  │  ├─ handlers.py
│  │  │  └─ helpers.py
│  │  ├─ models.py
│  │  ├─ ordering.py
│  │  ├─ pagination.py
│  │  ├─ repositories.py
│  │  ├─ responses.py
│  │  ├─ schemas.py
│  │  └─ utils.py
│  ├─ background.py
│  ├─ cache.py
│  ├─ config.py
│  ├─ database.py
│  ├─ dependencies.py
│  ├─ main.py
│  ├─ manage.py
│  ├─ sentry.py
│  └─ tasks.py
└─ tests
   ├─ api
   │  └─ v1
   │     └─ module_name
   │        ├─ test_views.py
   │        ├─ test_services.py
   │        ├─ test_repositories.py
   │        └─ test_schemas.py
   ├─ common.py
   ├─ conftest.py
   └─ utils.py
```

## Roadmap
 - [x] Add project structure description to README.md
 - [ ] Add tests
 - [ ] Add README.md to project template


## Contributing
Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact
If you have any questions, feel free to contact me via email: [ivan@simantiev.com](mailto:ivan@simantiev.com)

[contributors-shield]: https://img.shields.io/github/contributors/iyasha/fastapi-template.svg?style=for-the-badge
[contributors-url]: https://github.com/iyasha/fastapi-template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/iyasha/fastapi-template.svg?style=for-the-badge
[forks-url]: https://github.com/iyasha/fastapi-template/network/members
[stars-shield]: https://img.shields.io/github/stars/iyasha/fastapi-template.svg?style=for-the-badge
[stars-url]: https://github.com/iyasha/fastapi-template/stargazers
[issues-shield]: https://img.shields.io/github/issues/iyasha/fastapi-template.svg?style=for-the-badge
[issues-url]: https://github.com/iyasha/fastapi-template/issues
[license-shield]: https://img.shields.io/github/license/iyasha/fastapi-template.svg?style=for-the-badge
[license-url]: https://github.com/iyasha/fastapi-template/blob/master/LICENSE