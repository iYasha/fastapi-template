#! /usr/bin/env bash
set -e
set -o errexit
set -o nounset

celery worker -A .tasks -l info -Q main-queue -c "$CELERY_WORKER_CONCURRENCY"
