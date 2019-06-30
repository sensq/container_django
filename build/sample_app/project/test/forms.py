from django import forms

class details_form(forms.Form):
    """
    詳細設定のフォーム
    """
    vm_name = forms.CharField(
        label = '仮想マシン名 入力欄（必須）',
        required = False,
        max_length = 80,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'cols': 80,
                'style': 'width:1200px'
            }
        ),
    )
    
    purpose = forms.CharField(
        label = '利用目的 入力欄（任意）',
        required = False,
        max_length = 80,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'cols': 80,
                'style': 'width:1200px'
            }
        ),
    )
    
    notes = forms.CharField(
        label = '備考 入力欄（任意）',
        required = False,
        max_length = 80,
        widget = forms.TextInput(
            attrs={
                'class': 'form-control',
                'cols': 80,
                'style': 'width:1200px'
            }
        ),
    )
