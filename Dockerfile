# Pull base image
FROM python:3.8-buster

LABEL maintainer=vinay.kudari30@gmail.com \
    name=MaskDetectionAPI

ENV APP_USER=admin \
    APP_ROOT=/code \
    DJANGO_APP_ROOT=/code/mask_detection \
    LOG_LEVEL=info \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory
WORKDIR $APP_ROOT

# Create new non root user
RUN useradd -d $APP_ROOT -r $APP_USER

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    sqlite3 \
    postgresql-client \
    python-psycopg2 \
    && \
    apt-get clean

# Install dependencies
RUN pip install --upgrade pip
COPY requirements.txt $APP_ROOT
RUN pip install -r requirements.txt

# Copy project files
COPY . $APP_ROOT

EXPOSE 7000

CMD ["./docker/entrypoint.sh"]

