from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.refresh_dashboard_cache.refresh_dashboard_cache")
def refresh_dashboard_cache():
    print("Refreshing payroll KPI cache in Redis...")
    return {"status": "refreshed"}
