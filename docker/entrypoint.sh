#!/bin/sh

set -e
echo "V1.0.1"

exec \
    gunicorn mask_detection.wsgi:application \
     --name=MaskDetectionAPI \
     --user=$APP_USER \
     --group=$APP_USER \
     --bind=0.0.0.0:80 \
     --log-level=$LOG_LEVEL \
     --log-file=- \
     --worker-class=gevent

