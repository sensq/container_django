# -*- coding:utf-8 -*-
from django.core.management.base import BaseCommand

import os
app_name = os.environ.get("DJANGO_APPLICATION_NAME")
module_path = app_name + ".models"
from importlib import import_module
module = import_module(module_path)
MgrData = getattr(module, "MgrData")
import csv, json

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('csvpath', nargs='+', type=str)

    def handle(self, *args, **options):
        # CSVを読み込んでJSON化
        json_data = {}
        with open(options['csvpath'][0]) as f:    
            for i,line in enumerate(csv.DictReader(f)):
                json_data[str(i)] = json.loads(json.dumps(line, ensure_ascii=False))
        print('Loaded')
        
        # データをインポート
        for i in json_data:
            d = MgrData.objects.filter(ip=json_data[str(i)]["ip"]).first()
            d.num = json_data[str(i)]["num"]
            d.in_use = json_data[str(i)]["in_use"]
            d.available = json_data[str(i)]["available"]
            d.ping = json_data[str(i)]["ping"]
            d.expired = json_data[str(i)]["expired"]
            d.dept = json_data[str(i)]["dept"]
            d.name = json_data[str(i)]["name"]
            d.address = json_data[str(i)]["address"]
            if json_data[str(i)]["checkout_date"]:
                d.checkout_date = json_data[str(i)]["checkout_date"].replace("/", "-").replace("1900-01-00", "1900-01-01")
            if json_data[str(i)]["limit_date"]:
                d.limit_date = json_data[str(i)]["limit_date"].replace("/", "-").replace("1900-01-00", "1900-01-01")
            d.vm_name = json_data[str(i)]["vm_name"]
            d.purpose = json_data[str(i)]["purpose"]
            d.notes = json_data[str(i)]["notes"]
            d.save()
        print('Imported')
        
        # バリデート処理
        for i in json_data:
            d = MgrData.objects.filter(pk=i).first()
            if d:
                if(not d.in_use):
                    d.dept = None
                    d.name = None
                    d.address = None
                    d.checkout_date = None
                    d.limit_date = None
                    d.vm_name = None
                    d.purpose = None
                    d.notes = None
                d.save()
        print('Done')
