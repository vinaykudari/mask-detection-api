# Pull base image
FROM python:3.8-buster

LABEL maintainer=vinay.kudari30@gmail.com \
    name=MaskDetectionAPI

ENV APP_USER=admin \
    APP_ROOT=/code \
    DJANGO_APP_ROOT=/code/mask_detection \
    LOG_LEVEL=info \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=localhost \
    DEBUG=True \
    SECRET_KEY=local-secret-key

# Set working directory
WORKDIR $APP_ROOT

# Create new non root user
RUN useradd -d $APP_ROOT -r $APP_USER

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    postgresql-client \
    wget \
    python-psycopg2 \
    && \
    apt-get clean

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt $APP_ROOT
RUN pip install --default-timeout=100 -r requirements.txt

# Copy project files
COPY . $APP_ROOT

# Set working directory
WORKDIR $APP_ROOT/mask_detection

#USER $APP_USER

RUN wget -O uploads/models/face-detection/yolov3-face.cfg \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.cfg

RUN wget -O uploads/models/face-detection/yolov3-face.weights \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.weights

RUN wget -O uploads/models/mask-detection/export.pkl \
    https://storage.googleapis.com/maskdetection-api-files/models/mask-detection/export.pkl

RUN python3 manage.py migrate --no-input

RUN chown -R $APP_USER:$APP_USER $APP_ROOT

ENTRYPOINT ["../docker/entrypoint.sh"]

