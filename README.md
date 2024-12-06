# celery_explorer
Small service for executing celery tasks from browser


# Installation

    pip install git+https://github.com/paffel2/celery_explorer

# Launch worker

    celery --app=celery_manager worker -l DEBUG -Q default 

# Adding to your django project

1. Add "celery_explorer" to your INSTALLED_APPS setting like this::

        INSTALLED_APPS = [
            ...,
            "celery_explorer",
        ]

2. Include the polls URLconf in your project urls.py like this::

        path("celery_explorer/", include("celery_explorer.urls")),


3. Visit the ``/celery_explorer/`` URL to see manger panel.