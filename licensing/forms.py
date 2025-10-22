from django import forms

class ActivateForm(forms.Form):
    key = forms.CharField(label="كود التفعيل", max_length=64)
