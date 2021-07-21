from django.contrib import admin

from users.models import CustomUser


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        )
    search_fields = (
        'username',
        'email')
    list_filter = ('username',)


admin.site.register(CustomUser, UserAdmin)