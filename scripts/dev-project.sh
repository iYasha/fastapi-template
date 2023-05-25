#!/bin/bash
set -e


if [ ! -d ./fastapi-template ] ; then
    echo "Run this script from outside the project, to generate a sibling dev project"
    exit 1
fi

cookiecutter --no-input --overwrite-if-exists -f ./fastapi-template --config-file ./fastapi-template/scripts/dev-project-template.yml

