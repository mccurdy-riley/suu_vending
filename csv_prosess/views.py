from django.http import HttpResponse
from django.shortcuts import render

from .forms import UploadFileForm
from .logic import (
    filter_data_to_six_day_window,
    generate_processed_csv,
    open_csv_from_upload,
    process_transaction_data,
    transaction_cleaning,
)


def upload_report(request):
    form = UploadFileForm(request.POST or None, request.FILES or None)

    if request.method == "POST" and form.is_valid():
        uploaded_file = request.FILES["csv_file"]

        # CASE 1: User clicked "Download Processed CSV"
        if "download_btn" in request.POST:
            raw = open_csv_from_upload(uploaded_file)
            filtered = filter_data_to_six_day_window(raw)
            cleaned = transaction_cleaning(filtered)
            csv_text = generate_processed_csv(cleaned)

            response = HttpResponse(csv_text, content_type="text/csv")
            response["Content-Disposition"] = (
                'attachment; filename="processed_report.csv"'
            )
            return response

        # CASE 2: User just uploaded and wants to see the Summary
        report_data = process_transaction_data(uploaded_file)
        # We pass the form back to the results page so the file input is available for the download button
        return render(
            request, "report_results.html", {"report": report_data, "form": form}
        )

    # Initial page load
    return render(request, "upload.html", {"form": form})
