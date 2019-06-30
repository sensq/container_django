from django.contrib import admin
from .models import MgrData
from import_export import resources

# Register your models here.

class MgrAdmin(admin.ModelAdmin):
    """
    管理画面の一覧表示のカスタマイズ
    """
    list_display = ('num', 'ip', 'in_use', 'available', 'ping', 'expired', 'dept', 'name', 'address')
    ordering = ('pk',)

admin.site.register(MgrData, MgrAdmin)

class DataResource(resources.ModelResource):

    class Meta:
        model = MgrData