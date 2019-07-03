# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand

import os
app_name = os.environ.get("DJANGO_APPLICATION_NAME")
module_path = app_name + ".models"
from importlib import import_module
module = import_module(module_path)
MgrData = getattr(module, "MgrData")

class Command(BaseCommand):
    def handle(self, *args, **options):
        print("update ping_status all")
        for data in MgrData.objects.all():
            data.update_ping()
            print(data.ip + ": " + str(data.ping))
        print("update ping_status all is done")
