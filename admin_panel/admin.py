from django.contrib import admin
from admin_panel.models import ForgetPasswordTokens, Packages


# Register your models here.

class ForgetTokenAdmin(admin.ModelAdmin):
    list_display = ['id', 'email', 'token']

    class Meta:
        model = ForgetPasswordTokens
        fields = '__all__'


class PackagesAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'duration', 'price']


admin.site.register(ForgetPasswordTokens, ForgetTokenAdmin)
admin.site.register(Packages, PackagesAdmin)