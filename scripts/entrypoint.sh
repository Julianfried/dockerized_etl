#!/bin/bash

# Upgrade the Airflow database
if [ "$_AIRFLOW_DB_UPGRADE" = 'true' ]; then
  airflow db upgrade
  airflow db check
fi

# Create the admin user
if [ "$_AIRFLOW_WWW_USER_CREATE" = 'true' ]; then
  airflow users create \
    --username "$_AIRFLOW_WWW_USER_USERNAME" \
    --password "$_AIRFLOW_WWW_USER_PASSWORD" \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com
fi

# Execute the command passed to docker
exec airflow "$@"