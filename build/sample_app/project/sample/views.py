from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from .models import MgrData

# Create your views here.

def index(request):
    request.session['name'] = request.user
    return redirect("main")

def forbidden(request):
    """
    403ページを表示するだけの関数
    """
    return render(request, '403.html', {})

def main(request):
    """
    IP一覧ページを表示する関数
    """
    ret = {
        'data': None,
        'today': timezone.localtime(timezone.now()),
        'free_num': len(MgrData.objects.filter(in_use=True)),
        'expired_num': len(MgrData.objects.filter(expired=True)),
    }
    
    # 管理者以外は、メールアドレスが一致したデータだけ表示
    from django.db.models import Q
    if request.user.is_superuser:
        ret['data'] = MgrData.objects.filter(
            Q(available=True)
        )
    elif not request.user.is_authenticated:
        ret['data'] = MgrData.objects.filter(
            Q(in_use=False), Q(available=True)
        )
    else:
        ret['data'] = MgrData.objects.filter(
            Q(Q(in_use=False), Q(available=True)) | Q(address=request.user.email)
        )
    
    return render(request, 'main.html', ret)

@login_required
def managed(request):
    """
    IP一覧ページを表示する関数
    """
    ret = {
        'data': None,
        'today': timezone.localtime(timezone.now()),
        'free_num': len(MgrData.objects.filter(in_use=True)),
        'expired_num': len(MgrData.objects.filter(expired=True)),
    }
    
    # 管理者以外は、メールアドレスが一致したデータだけ表示
    from django.db.models import Q
    if request.user.is_superuser:
        ret['data'] = MgrData.objects.filter(
            Q(available=False)
        )
    
    return render(request, 'main.html', ret)

@login_required
def export_csv(request):
    """
    DBをCSV形式でエクスポートする関数
    """
    if request.user.is_superuser:
        import io
        import os
        from django.http import HttpResponse
        from .admin import DataResource
        dataset = DataResource().export()
        now = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M%S")
        filename = "simplemgr_" + now + ".csv"
        os.makedirs("/export_csv", exist_ok=True)
        path = ("/export_csv/" + filename)
        with open(path, mode='w') as f:
            f.write(dataset.csv)
        output = io.StringIO()
        output.write(dataset.csv)
        response = HttpResponse(output.getvalue(), content_type="text/csv; charset=cp932")
        response["Content-Disposition"] = ("filename=" + filename)
        return response
    else:
        return redirect("main")

@login_required
def ping(request, num):
    """
    対象のIPに疎通確認をするAPI
    """
    if request.method == "GET":
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( num == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        obj.update_ping()
        
        return redirect(request.META['HTTP_REFERER'])

@login_required
def req(request, num):
    """
    各種申請を行う画面を表示する関数
    """
    if request.method == "GET":
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( num == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        # 継続申請の可否チェック
        increase_enable = False
        if obj.in_use:
            # 今日が返却日の1ヶ月前を過ぎていることの確認
            import datetime
            if obj.limit_date is not None and obj.checkout_date is not None:
                if datetime.date.today() > (obj.limit_date - relativedelta(months=1)):
                    increase_enable = True
        
        ret = {
            "obj": obj,
            "increase_enable": increase_enable,
        }
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")

def post_influxdb(measurement, type, ip, name):
    """
    InfluxDBにPostするAPI
    """
    import urllib.request
    import urllib.parse
    import os
    host = os.environ.get("APISERVER_HOST")
    port = os.environ.get("APISERVER_PORT")
    api_url = "http://" + host + ":" + port + "/add_influxdb"
    data = {
        "measurement": measurement,
        "type": type,
        "ip": ip,
        "name": name
    }
    encoded_data = urllib.parse.urlencode(data).encode('utf-8')
    req = urllib.request.Request(api_url, encoded_data)
    res = urllib.request.urlopen(req)
    print(res.read())
    print(res.msg)
    return res.msg

@login_required
def new_checkout(request):
    """
    新規にIPを借りるAPI
    """
    if request.method == "POST":
        num = request.POST.get("request_id", "0")
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( id == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        obj.in_use = True
        obj.dept = ""
        obj.name = request.user.username
        obj.address = request.user.email
        obj.checkout_date = timezone.now()
        obj.limit_date = (timezone.now() + relativedelta(months=3))
        obj.vm_name = ""
        obj.share = ""
        obj.purpose = ""
        obj.notes = ""
        
        obj.save()
        ret = {"obj": obj, "order": "new"}
        
        post_influxdb("request", "New", obj.ip, request.user.username)
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def clear_checkout(request):
    """
    借りているIPを開放するAPI
    """
    if request.method == "POST":
        num = request.POST.get("request_id", "0")
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( num == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        obj.update_ping()
        
        # 疎通確認が取れた場合は開放せずに元のページに戻す
        if obj.ping:
            ret = {"obj": obj}
            return render(request, 'req/req.html', ret)
        
        obj.initialize()
        
        ret = {"obj": obj, "order": "clear"}
        
        post_influxdb("request", "Clear", obj.ip, request.user.username)
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def increase_limit(request):
    """
    期限日を3ヶ月延長するAPI
    """
    if request.method == "POST":
        num = request.POST.get("request_id", "0")
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( num == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        import datetime
        # 今日が返却日の1ヶ月前を過ぎていた場合のみ実行
        if datetime.date.today() > (obj.limit_date - relativedelta(months=1)):
            obj.limit_date = (datetime.date.today() + relativedelta(months=3))
            obj.save()
            obj.update_expired()
        
        # 継続申請の可否チェック
        increase_enable = False
        
        ret = {
            "obj": obj,
            "increase_enable": increase_enable,
            "order": "increase",
        }
        
        post_influxdb("request", "Increase", obj.ip, request.user.username)
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def details(request, num):
    """
    詳細設定を行う画面を表示する関数
    """
    from .forms import details_form
    if request.method == "GET":
        obj = MgrData.objects.get(num=num)
        
        # 改竄等による不正な遷移の防止
        if( num == 0 ):
            return redirect("403")
        if( not request.user.is_superuser ):
            if( not obj.in_use ):
                return redirect("403")
            if( obj.in_use and obj.address != request.user.email ):
                return redirect("403")
        
        f = details_form(initial = {
            'vm_name': obj.vm_name,
            'share': obj.share,
            'purpose': obj.purpose,
            'notes': obj.notes,
        })
        ret = {"obj":obj, "form": f}
        
        return render(request, 'req/details.html', ret)
        
    else:
        return redirect("main")

@login_required
def set_details(request):
    """
    詳細設定を行うAPI
    """
    from .forms import details_form
    if request.method == "POST":
        form = details_form(data=request.POST)
        if form.is_valid():
            num = request.POST.get("request_id", "0")
            obj = MgrData.objects.get(num=num)
            
            # 改竄等による不正な遷移の防止
            if( num == 0 ):
                return redirect("403")
            if( not request.user.is_superuser ):
                if( obj.address != request.user.email ):
                    return redirect("403")
                    
            obj.vm_name = form.cleaned_data['vm_name']
            obj.purpose = form.cleaned_data['purpose']
            obj.share = form.cleaned_data['share']
            obj.notes = form.cleaned_data['notes']
            obj.save()
            post_influxdb("request", "detail", obj.ip, request.user.username)
            return redirect("main")
            
    else:
        form = details_form()
        return render(request, 'req/details.html', form)
