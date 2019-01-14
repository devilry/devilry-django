def generate_report(devilry_report_id):
    from devilry.devilry_report.models import DevilryReport
    devilry_report = DevilryReport.objects.get(id=devilry_report_id)
    devilry_report.generate()
