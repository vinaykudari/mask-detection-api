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

if [ ! -f uploads/models/face-detection/yolov3-face.cfg ]; then
    echo "Downloading YoloV3 Architecture"
    wget -O uploads/models/face-detection/yolov3-face.cfg \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.cfg
    ls -l uploads/models/face-detection/yolov3-face.cfg
fi

if [ ! -f uploads/models/face-detection/yolov3-face.weights ]; then
    echo "Downloading YoloV3 Weights"
    wget -O uploads/models/face-detection/yolov3-face.weights \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.weights
    ls -l uploads/models/face-detection/yolov3-face.weights
fi

if [ ! -f uploads/models/mask-detection/export.pkl ]; then
    echo "Downloading Mask Detection Model Weights"
    wget -O uploads/models/mask-detection/export.pkl \
    https://storage.googleapis.com/maskdetection-api-files/models/mask-detection/export.pkl
    ls -l uploads/models/mask-detection/export.pkl
fi






chmod a+rwx uploads/

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

