from celery import Celery
from .settings import Worker


# celery = Celery('tasks', broker=Worker.broker_url, backend=Worker.result_backend)
# celery.config_from_object(Worker)

# celery_app.autodiscover_tasks()
def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=Worker.result_backend,
        broker=Worker.broker_url
    )
    celery.conf.update(app.config)
    celery.config_from_object(Worker)
    TaskBase = celery.Task

    class ContextTask(celery.Task):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery
