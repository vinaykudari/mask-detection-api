# Pull base image
FROM python:3.8-buster

ARG DATABASE_URL
ARG SECRET_KEY=local-secret-key
ARG DEBUG=True

LABEL maintainer=vinay.kudari30@gmail.com \
    name=MaskDetectionAPI

ENV APP_USER=admin \
    APP_ROOT=/code \
    DJANGO_APP_ROOT=/code/mask_detection \
    LOG_LEVEL=info \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL=${DATABASE_URL} \
    DEBUG=${DEBUG} \
    SECRET_KEY=${SECRET_KEY}

RUN echo $DATABASE_URL

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
RUN pip install --default-timeout=10000 -r requirements.txt

# Copy project files
COPY . $APP_ROOT

# Set working directory
WORKDIR $APP_ROOT/mask_detection

# Download Models
RUN mkdir -p uploads/models/face-detection/
RUN mkdir -p uploads/models/mask-detection/

RUN wget -nc -O uploads/models/face-detection/yolov3-face.cfg \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.cfg; \
    exit 0

RUN wget -nc -O uploads/models/face-detection/yolov3-face.weights \
    https://storage.googleapis.com/maskdetection-api-files/models/face-detection/yolov3-face.weights; \
    exit 0

RUN wget -nc -O uploads/models/mask-detection/export.pkl \
    https://storage.googleapis.com/maskdetection-api-files/models/mask-detection/export.pkl; \
    exit 0

# Run Migrations
RUN python3 manage.py migrate --no-input; exit 0

RUN chown -R $APP_USER:$APP_USER $APP_ROOT

ENTRYPOINT ["../docker/entrypoint.sh"]

