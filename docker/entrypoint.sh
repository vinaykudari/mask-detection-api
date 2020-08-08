#!/bin/sh

set -e

echo "Database URL"
echo $DATABASE_URL

echo "Waiting for database ..."
#while ! pg_isready -h $DB_HOST -p $DB_PORT 2>/dev/null; do
#    sleep 1
#done

echo "Downloading Models"
gsutil -m cp -r gs://maskdetection-api-files/models/ .

echo "Migrating database ..."
python3 manage.py migrate --no-input

exec \
    gunicorn mask_detection.wsgi:application \
     --name=MaskDetectionAPI \
     --user=$APP_USER \
     --group=$APP_USER \
     --bind=0.0.0.0:80 \
     --log-level=$LOG_LEVEL \
     --log-file=- \
     --worker-class=gevent

