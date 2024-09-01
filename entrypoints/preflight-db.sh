#!/bin/bash

set -e

python ./manage.py wait_for_db
python ./manage.py migrate --noinput
python ./manage.py remove_stale_contenttypes --no-input  # remove potential mode from django_content_type table
python ./manage.py clearsessions  # clear django admin sessions
