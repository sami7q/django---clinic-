from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile


# ─────────────────────────────
# 1) إنشاء مستخدم جديد
# ─────────────────────────────
class UserCreateForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="الدور / الصلاحيات"
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "is_active", "role", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_style = (
            "w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-800 "
            "focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white text-sm"
        )
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "h-4 w-4 accent-blue-600"
            else:
                field.widget.attrs["class"] = common_style

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.is_staff = self.cleaned_data["is_staff"]
        user.is_active = self.cleaned_data["is_active"]
        if commit:
            user.save()
        role = self.cleaned_data["role"]
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        return user


# ─────────────────────────────
# 2) تعديل مستخدم موجود
# ─────────────────────────────
class UserEditForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        label="الدور / الصلاحيات"
    )

    class Meta:
        model = User
        fields = ["username", "email", "is_staff", "is_active", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            try:
                self.fields["role"].initial = self.instance.profile.role
            except UserProfile.DoesNotExist:
                pass
        common_style = (
            "w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-800 "
            "focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white text-sm"
        )
        for name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "h-4 w-4 accent-blue-600"
            else:
                field.widget.attrs["class"] = common_style

    def save(self, commit=True):
        user = super().save(commit=commit)
        role = self.cleaned_data["role"]
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        return user


# ─────────────────────────────
# 3) نموذج تغيير كلمة المرور بمظهر جميل
# ─────────────────────────────
class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        common_style = (
            "w-full border border-gray-300 rounded-lg px-3 py-2 text-gray-800 "
            "focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition bg-white text-sm"
        )
        for name, field in self.fields.items():
            field.widget.attrs["class"] = common_style
