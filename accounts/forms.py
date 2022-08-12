from django import forms
from .models import IPAddress


class IPAddressForm(forms.ModelForm):
    class Meta:
        model = IPAddress
        fields = ["ipaddress", "is_active", "in_router"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['ipaddress'].widget = forms.TextInput(attrs={
            "pattern": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            "class": "form-control"
        })
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={
            "class": "form-check-input mt-0"
        })
