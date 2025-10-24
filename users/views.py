from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .forms import UserCreateForm, UserEditForm, StyledPasswordChangeForm


def get_main_user():
    """إرجاع المستخدم الأساسي (superuser الأول في النظام)"""
    return User.objects.filter(is_superuser=True).order_by('id').first()


@login_required
def users_list(request):
    users = User.objects.all().order_by('-id')
    main_user = get_main_user()
    return render(request, 'users/list.html', {'users': users, 'main_user': main_user})


@login_required
def create_user(request):
    main_user = get_main_user()
    if request.user != main_user:
        messages.error(request, "🚫 فقط المستخدم الأساسي يمكنه إضافة مستخدمين.")
        return redirect('users:list')

    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم إضافة المستخدم بنجاح.')
            return redirect('users:list')
    else:
        form = UserCreateForm()

    return render(request, 'users/form.html', {'form': form})


@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    # حماية المستخدم الأساسي
    if user == get_main_user() and request.user != user:
        messages.error(request, "🚫 لا يمكنك تعديل المستخدم الأساسي.")
        return redirect('users:list')

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '✏️ تم تعديل بيانات المستخدم بنجاح.')
            return redirect('users:list')
    else:
        form = UserEditForm(instance=user)

    return render(request, 'users/form.html', {'form': form, 'edit_mode': True, 'user_obj': user})


@login_required
def delete_user(request, user_id):
    user_to_delete = get_object_or_404(User, id=user_id)
    main_user = get_main_user()

    # ممنوع حذف المستخدم الأساسي
    if user_to_delete == main_user:
        messages.error(request, "🚫 لا يمكن حذف المستخدم الأساسي للنظام.")
        return redirect('users:list')

    # فقط المستخدم الأساسي يستطيع الحذف
    if request.user != main_user:
        messages.error(request, "🚫 فقط المستخدم الأساسي يمكنه حذف المستخدمين.")
        return redirect('users:list')

    # ممنوع تحذف نفسك وأنت الأساسي (لو حاب نمنع الانتحار)
    if user_to_delete == request.user:
        messages.error(request, "❌ لا يمكنك حذف نفسك.")
        return redirect('users:list')

    if request.method == 'POST':
        username = user_to_delete.username
        user_to_delete.delete()
        messages.success(request, f"🗑️ تم حذف المستخدم {username} بنجاح.")
        return redirect('users:list')

    return render(request, 'users/delete.html', {'user': user_to_delete, 'main_user': main_user})


@login_required
def change_password(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    main_user = get_main_user()

    # من له السماح؟ المستخدم نفسه أو المستخدم الأساسي
    if request.user != main_user and request.user != target_user:
        messages.error(request, "🚫 فقط المستخدم الأساسي أو صاحب الحساب يمكنه تغيير كلمة المرور.")
        return redirect('users:list')

    if request.method == 'POST':
        form = StyledPasswordChangeForm(target_user, request.POST)
        if form.is_valid():
            form.save()
            # عشان ما يطلعه من السيشن لو غيّر كلمة مروره
            update_session_auth_hash(request, target_user)
            messages.success(request, "🔑 تم تغيير كلمة المرور بنجاح.")
            return redirect('users:list')
    else:
        form = StyledPasswordChangeForm(target_user)

    return render(request, 'users/change_password.html', {
        'form': form,
        'user': target_user,
    })
