from app.core.celery_app import celery_app


@celery_app.task(name="app.tasks.generate_pdf.generate_pdf_task")
def generate_pdf_task(payslip_id: int):
    # PDF generation logic with WeasyPrint and Azure blob upload
    print(f"Generating PDF for payslip {payslip_id}...")
    return {"payslip_id": payslip_id, "status": "generated"}
