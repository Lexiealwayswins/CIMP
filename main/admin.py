from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User  # 这是你自定义的用户模型

# Register your models here.
admin.site.register(User, UserAdmin)