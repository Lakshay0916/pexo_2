from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "payroll_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.tasks.generate_pdf",
        "app.tasks.send_payslip_email",
        "app.tasks.refresh_dashboard_cache",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "refresh-dashboard-kpis-every-10-mins": {
            "task": "app.tasks.refresh_dashboard_cache.refresh_dashboard_cache",
            "schedule": 600.0,
        },
    },
)
