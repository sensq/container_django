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
    import datetime
    ret = {
        'data': None,
        'today': timezone.localtime(timezone.now()),
        'free_num': len(MgrData.objects.filter(in_use=True)),
        'expired_num': len(MgrData.objects.filter(expired=True)),
    }
    
    # 管理者以外は、メールアドレスが一致したデータだけ表示
    if request.user.is_superuser:
        ret['data'] = MgrData.objects.all()
    elif not request.user.is_authenticated:
        ret['data'] = MgrData.objects.filter(in_use=False)
    else:
        from django.db.models import Q
        ret['data'] = MgrData.objects.filter(
            Q(in_use=False) | Q(address=request.user.email)
        )
    
    return render(request, 'main.html', ret)

@login_required
def export_csv(request):
    """
    DBをCSV形式でエクスポートする関数
    """
    if request.user.is_superuser:
        import io
        from django.http import HttpResponse
        from .admin import DataResource
        dataset = DataResource().export()
        now = timezone.localtime(timezone.now()).strftime("%Y%m%d_%H%M%S")
        filename = "simplemgr_" + now + ".csv"
        path = ("/codes/export_csv/" + filename)
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
        decrease_enable = False
        if obj.in_use:
            # 今日が返却日の1ヶ月前を過ぎていることの確認
            import datetime
            if obj.limit_date is not None and obj.checkout_date is not None:
                if datetime.date.today() > (obj.limit_date - relativedelta(months=1)):
                    increase_enable = True
                # 今日と貸出日が返却日の3ヶ月前よりも前であることの確認
                if datetime.date.today() < (obj.limit_date - relativedelta(months=3)):
                    if obj.checkout_date < (obj.limit_date - relativedelta(months=3)):
                        decrease_enable = True
        
        ret = {
            "obj": obj,
            "increase_enable": increase_enable,
            "decrease_enable": decrease_enable,
        }
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")

@login_required
def new_checkout(request):
    """
    新規にIPを借りる関数
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
        obj.purpose = ""
        obj.notes = ""
        
        obj.save()
        ret = {"obj": obj, "order": "new"}
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def clear_checkout(request):
    """
    借りているIPを開放する関数
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
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def increase_limit(request):
    """
    期限日を3ヶ月延長する関数
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
            obj.limit_date = (obj.limit_date + relativedelta(months=3))
            obj.save()
            obj.update_expired()
        
        ret = {"obj": obj, "order": "increase"}
        
        return render(request, 'req/req.html', ret)
        
    else:
        return redirect("main")


@login_required
def reduce_limit(request):
    """
    期限日を3ヶ月短縮する関数
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
                    
        execute = False
        
        # 今日が返却日の3ヶ月前よりも前の場合のみ実行
        import datetime
        if datetime.date.today() < (obj.limit_date - relativedelta(months=3)):
            # 貸出日が返却日の3ヶ月前よりも前の場合のみ実行
            if obj.checkout_date < (obj.limit_date - relativedelta(months=3)):
                obj.limit_date = (obj.limit_date - relativedelta(months=3))
                obj.save()
        
        ret = {"obj": obj, "order": "reduce"}
        
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
    詳細設定を行う画面
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
            obj.notes = form.cleaned_data['notes']
            obj.save()
            return redirect("main")
            
    else:
        form = details_form()
        return render(request, 'req/details.html', form)
