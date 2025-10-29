#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clinic.settings')  # عدل اسم المشروع إذا يختلف

    from django.core.management import execute_from_command_line

    # ✅ تلقائيًا استخدم المنفذ 8010 إن لم يُحدد أمر آخر
    if len(sys.argv) == 1:
        sys.argv += ["runserver", "127.0.0.1:8010"]

    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
