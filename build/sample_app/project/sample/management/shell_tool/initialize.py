app_name = os.environ.get("DJANGO_APPLICATION_NAME")
module_path = app_name + ".models"
from importlib import import_module
module = import_module(module_path)
MgrData = getattr(module, "MgrData")

MgrData.objects.all()

for i in range(254):
    MgrData.objects.create(
        # 固有情報
        num = i+1,
        ip = ("192.168.1." + str(i+1)),
        # ステータス
        in_use = False,
        available = True,
        ping = False,
        expired = False,
        # 利用者情報
        dept = None,
        name = None,
        address = None,
        # 詳細情報
        checkout_date = None,
        limit_date = None,
        vm_name = None,
        share = None,
        purpose = None,
        notes = None
    )
