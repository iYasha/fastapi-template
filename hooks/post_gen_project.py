#!/usr/bin/env python
import os
import shutil

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


def remove_dir(directory_name):
    frontend_dir = os.path.join(PROJECT_DIRECTORY, directory_name)
    shutil.rmtree(frontend_dir)


if __name__ == '__main__':

    if '{{ cookiecutter.create_frontend_container_configuration }}' != 'y':
        remove_dir('docker/frontend')

    if '{{ cookiecutter.add_celery }}' != 'y':
        # remove dir PROJECT_DIRECTORY/frontend
        remove_file('src/tasks.py')
        remove_file('src/background.py')
        # TODO: remove celery usage from src/api/v1/healthcheck
