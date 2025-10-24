from django import template

# تسجيل كائن مكتبة Django لتفعيل الفلاتر
register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    """
    فلتر مخصص يضيف كلاس CSS لأي عنصر form داخل القالب.
    مثال:
      {{ form.username|add_class:"input-class" }}
    """
    return field.as_widget(attrs={"class": css_class})
