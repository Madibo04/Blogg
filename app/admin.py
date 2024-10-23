from django.contrib import admin
from app.models import Blog, Contact, Comment


# Register your models here.
admin.site.register(Blog)
admin.site.register(Contact)
admin.site.register(Comment)