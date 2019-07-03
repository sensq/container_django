from django.db import models
import datetime

# Create your models here.
class MgrData(models.Model):
    # 固有情報
    num = models.PositiveSmallIntegerField('No', unique=True)
    ip = models.GenericIPAddressField('IP', unique=True)
    
    # ステータス
    in_use = models.BooleanField('貸出中', default=True)
    available = models.BooleanField('貸出可能', default=True)
    ping = models.NullBooleanField('死活', default=None, blank=True)
    expired = models.NullBooleanField('期限切れ', default=None, blank=True)
    
    # 利用者情報
    dept = models.CharField('部署', max_length=10, blank=True, null=True)
    name = models.CharField('氏名', max_length=20, blank=True, null=True)
    address = models.EmailField('メールアドレス', max_length=50, blank=True, null=True)
    
    # 詳細情報
    checkout_date = models.DateField('貸出日', blank=True, null=True)
    limit_date = models.DateField('返却日', blank=True, null=True)
    vm_name = models.CharField('仮想マシン名', max_length=80, blank=True, null=True)
    purpose = models.TextField('目的', max_length=80, blank=True, null=True)
    notes = models.TextField('備考', max_length=80, blank=True, null=True)

    def initialize(self):
        """
        初期化関数
        """
        self.in_use = False
        self.available = True
        self.ping = None
        self.expired = None
        self.dept = None
        self.name = None
        self.address = None
        self.checkout_date = None
        self.limit_date = None
        self.vm_name = None
        self.purpose = None
        self.notes = None
        self.save()
        return self

    def update_expired(self):
        """
        期限切れフラグの更新をする関数
        """
        if self.limit_date:
            today = datetime.datetime.today()
            date = str(self.limit_date).split("-")
            limit_date = datetime.datetime(int(date[0]), int(date[1]), int(date[2])) 
            if limit_date < today:
                self.expired = True
            else:
                self.expired = False
        self.save()
        return self

    def update_ping(self):
        """
        死活フラグの更新をする関数
        """
        import pings
        p = pings.Ping()
        res = p.ping(self.ip)
        self.ping = res.is_reached()
        self.save()
        return self

    def __str__(self):
        return self.ip