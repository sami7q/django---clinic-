from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['name', 'age', 'gender', 'phone', 'diagnosis', 'notes']

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'أدخل اسم المريض',
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 placeholder-gray-400 transition outline-none'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': 'العمر',
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 placeholder-gray-400 transition outline-none'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 transition outline-none cursor-pointer',
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'رقم الهاتف',
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 placeholder-gray-400 transition outline-none'
            }),
            'diagnosis': forms.TextInput(attrs={
                'placeholder': 'التشخيص الطبي',
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 placeholder-gray-400 transition outline-none'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'أضف ملاحظات إضافية إن وجدت',
                'class': 'w-full border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-100 rounded-lg px-3 py-2 text-gray-800 placeholder-gray-400 transition outline-none resize-none'
            }),
        }
