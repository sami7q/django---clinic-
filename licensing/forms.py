from django import forms
from .models import LicenseKey

class LicenseActivationForm(forms.ModelForm):
    class Meta:
        model = LicenseKey
        fields = ['key']
        widgets = {
            'key': forms.TextInput(attrs={
                'class': 'w-full border rounded-lg p-2 focus:ring focus:ring-blue-300',
                'placeholder': 'أدخل كود التفعيل هنا...'
            })
        }
