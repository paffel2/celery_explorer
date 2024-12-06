===============
celery_explorer
===============

Simple manager for starting celery tasks

Quick start
-----------

1. Add "celery_explorer" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "celery_explorer",
    ]

2. Include the polls URLconf in your project urls.py like this::

    path("celery_explorer/", include("celery_explorer.urls")),


3. Visit the ``/celery_explorer/`` URL to see manger panel.