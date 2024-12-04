# celery_manager
Small service for executing celery tasks from browser


# Launch

    ./manage.py migrate
    ./manage.py runserver

# Launch worker

    celery --app=celery_manager worker -l DEBUG -Q default 