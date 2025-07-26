from django import forms
from .models import NightCheck, DeathEvent, Judgment, Player, PoliceIdentity, WerewolfProbabilityAdjustment, OppositionGroup

class NightCheckForm(forms.ModelForm):
    class Meta:
        model = NightCheck
        fields = ['checker', 'target', 'result', 'night_number']
        widgets = {
            'checker': forms.Select(attrs={'class': 'form-control'}),
            'target': forms.Select(attrs={'class': 'form-control'}),
            'result': forms.Select(attrs={'class': 'form-control'}),
            'night_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # 动态设置查验者选项，显示具体的警察身份
        try:
            police_identity = PoliceIdentity.objects.first()
            if police_identity:
                # 如果设置了警察身份，显示具体的玩家编号
                checker_choices = [
                    ('', '----------'),
                    ('A', f'警察A（{police_identity.police_a.number}号）'),
                ]
                if police_identity.police_b:
                    checker_choices.append(('B', f'警察B（{police_identity.police_b.number}号）'))
                else:
                    checker_choices.append(('B', '警察B（暂未设置）'))
            else:
                # 如果没有设置警察身份，显示默认选项
                checker_choices = [
                    ('', '----------'),
                    ('A', '警察A'),
                    ('B', '警察B'),
                ]
        except:
            # 如果出现异常，使用默认选项
            checker_choices = [
                ('', '----------'),
                ('A', '警察A'),
                ('B', '警察B'),
            ]
        
        self.fields['checker'].choices = checker_choices

class DeathEventForm(forms.ModelForm):
    class Meta:
        model = DeathEvent
        fields = ['player', 'event_type', 'night_number']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
            'night_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class JudgmentForm(forms.ModelForm):
    class Meta:
        model = Judgment
        fields = ['player', 'label', 'reason']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'label': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['number', 'nickname']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
            'nickname': forms.TextInput(attrs={'class': 'form-control'}),
        }

class PoliceIdentityForm(forms.ModelForm):
    class Meta:
        model = PoliceIdentity
        fields = ['police_a', 'police_b']
        widgets = {
            'police_a': forms.Select(attrs={'class': 'form-control'}),
            'police_b': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置police_b字段为可选
        self.fields['police_b'].required = False
        self.fields['police_b'].empty_label = "暂不设置警察B"

    def clean(self):
        cleaned_data = super().clean()
        police_a = cleaned_data.get('police_a')
        police_b = cleaned_data.get('police_b')

        if police_a and police_b and police_a == police_b:
            raise forms.ValidationError("警察A和警察B不能是同一个人！")

        return cleaned_data 

class WerewolfProbabilityAdjustmentForm(forms.ModelForm):
    class Meta:
        model = WerewolfProbabilityAdjustment
        fields = ['player', 'probability_increase', 'reason']
        widgets = {
            'player': forms.Select(attrs={'class': 'form-control'}),
            'probability_increase': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'max': 100, 
                'step': 0.01,
                'placeholder': '请输入增加的百分比，如10表示增加10%'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': '请输入增加匪徒概率的原因'
            }),
        } 

class OppositionGroupForm(forms.ModelForm):
    class Meta:
        model = OppositionGroup
        fields = ['player_a', 'player_b', 'reason']
        widgets = {
            'player_a': forms.Select(attrs={'class': 'form-control'}),
            'player_b': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': '请详细说明为什么认为这两个玩家是对立面'
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        player_a = cleaned_data.get('player_a')
        player_b = cleaned_data.get('player_b')
        
        if player_a and player_b and player_a == player_b:
            raise forms.ValidationError("不能选择同一个玩家作为对立面！")
        
        # 检查是否已经存在相同的对立组合
        if player_a and player_b:
            # 确保player_a的编号小于player_b
            if player_a.number > player_b.number:
                player_a, player_b = player_b, player_a
            
            if OppositionGroup.objects.filter(player_a=player_a, player_b=player_b).exists():
                raise forms.ValidationError("这对玩家已经存在对立关系！")
        
        return cleaned_data 