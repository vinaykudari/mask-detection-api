#!/bin/sh

set -e

echo "Database URL"
echo $DATABASE_URL

echo "Waiting for database ..."
#while ! pg_isready -h $DB_HOST -p $DB_PORT 2>/dev/null; do
#    sleep 1
#done

echo "Downloading Models"
mkdir -p uploads/models/face-detection/
mkdir -p uploads/models/mask-detection/

curl -O\
 https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.cfg > uploads/models/face-detection/yolov3-face.cfg
curl -O \
https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.weights > uploads/models/face-detection/yolov3-face.cfg
curl -O \
https://storage.googleapis.com/maskdetection-api-files/models/mask_detection/export.pkl > uploads/models/mask-detection/export.pkl

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

