from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.send_payslip_email.send_payslip_email_task")
def send_payslip_email_task(employee_email: str, payslip_id: int):
    print(f"Sending payslip email to {employee_email} for payslip {payslip_id}...")
    return {"status": "sent", "email": employee_email}
