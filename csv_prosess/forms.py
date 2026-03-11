from django import forms


class UploadFileForm(forms.Form):
    csv_file = forms.FileField(
        label="Select Cashless Transactions CSV",
        help_text="Upload the raw export from your vending system.",
    )
