import dj_database_url
from environ import Env

env = Env()

SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DJ_DEBUG', default=False)  # noqa: F405
DATABASES = {
    'default': dj_database_url.config(
        default=env.str('DATABASE_URL')
    )
}
