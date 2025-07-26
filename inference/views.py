from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Player, NightCheck, DeathEvent, Judgment, PoliceIdentity, WerewolfProbabilityAdjustment, OppositionGroup
from .forms import NightCheckForm, DeathEventForm, JudgmentForm, PlayerForm, PoliceIdentityForm, WerewolfProbabilityAdjustmentForm, OppositionGroupForm
from .logic_engine import compare_scenarios, analyze_solutions, get_recommendations, compare_scenarios_with_police_identity, apply_werewolf_probability_adjustments
import json

def index(request):
    """主页"""
    # 获取所有数据
    players = Player.objects.all().order_by('number')
    night_checks = NightCheck.objects.all()
    death_events = DeathEvent.objects.all()
    judgments = Judgment.objects.all()
    werewolf_adjustments = WerewolfProbabilityAdjustment.objects.all()
    opposition_groups = OppositionGroup.objects.all()
    
    # 获取警察身份设置
    police_identity = PoliceIdentity.objects.first()
    
    # 执行推理
    checks = []
    deaths = []
    judgments_data = []
    werewolf_adjustments_data = []
    
    for check in night_checks:
        checks.append({
            "checker": check.checker,
            "target": check.target.number,
            "result": check.result
        })
    
    for death in death_events:
        deaths.append({
            "player": death.player.number,
            "type": death.event_type
        })
    
    for judgment in judgments:
        judgments_data.append({
            "player": judgment.player.number,
            "label": judgment.label
        })
    
    for adjustment in werewolf_adjustments:
        werewolf_adjustments_data.append({
            "player": adjustment.player.number,
            "probability_increase": float(adjustment.probability_increase),
            "reason": adjustment.reason
        })
    
    # 执行推理 - 需要警察身份信息
    results = {"A": [], "B": []}
    analysis_A = {}
    analysis_B = {}
    recommendations = []
    
    if police_identity and players.count() >= 2:
        # 修改推理引擎调用，传入警察身份
        police_b_number = police_identity.police_b.number if police_identity.police_b else None
        results = compare_scenarios_with_police_identity(
            checks, deaths, judgments_data, 
            police_identity.police_a.number, 
            police_b_number
        )
        
        # 分析结果
        analysis_A = analyze_solutions(results["A"]) if results["A"] else {}
        analysis_B = analyze_solutions(results["B"]) if results["B"] else {}
        
        # 应用匪徒概率调整
        if werewolf_adjustments_data:
            print(f"应用匪徒概率调整：{len(werewolf_adjustments_data)}个调整")
            analysis_A = apply_werewolf_probability_adjustments(analysis_A, werewolf_adjustments_data)
            analysis_B = apply_werewolf_probability_adjustments(analysis_B, werewolf_adjustments_data)
        
        # 获取建议
        recommendations = get_recommendations(results)
    
    context = {
        'players': players,
        'night_checks': night_checks,
        'death_events': death_events,
        'judgments': judgments,
        'werewolf_adjustments': werewolf_adjustments,
        'opposition_groups': opposition_groups,
        'police_identity': police_identity,
        'results': results,
        'analysis_A': analysis_A,
        'analysis_B': analysis_B,
        'recommendations': recommendations,
    }
    
    return render(request, 'inference/index.html', context)

def add_player(request):
    """添加玩家"""
    if request.method == 'POST':
        form = PlayerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '玩家添加成功！')
            return redirect('index')
    else:
        form = PlayerForm()
    
    return render(request, 'inference/add_player.html', {'form': form})

def add_night_check(request):
    """添加夜晚查验"""
    if request.method == 'POST':
        form = NightCheckForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '夜晚查验记录添加成功！')
            return redirect('index')
    else:
        form = NightCheckForm()
    
    return render(request, 'inference/add_night_check.html', {'form': form})

def add_death_event(request):
    """添加死亡事件"""
    if request.method == 'POST':
        form = DeathEventForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '死亡事件添加成功！')
            return redirect('index')
    else:
        form = DeathEventForm()
    
    return render(request, 'inference/add_death_event.html', {'form': form})

def add_judgment(request):
    """添加主观判断"""
    if request.method == 'POST':
        form = JudgmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '主观判断添加成功！')
            return redirect('index')
    else:
        form = JudgmentForm()
    
    return render(request, 'inference/add_judgment.html', {'form': form})

def add_all_players(request):
    """一键添加12个玩家"""
    if request.method == 'POST':
        created = 0
        for i in range(1, 13):
            if not Player.objects.filter(number=i).exists():
                Player.objects.create(number=i, nickname='')
                created += 1
        if created:
            messages.success(request, f'已自动添加{created}个玩家！')
        else:
            messages.info(request, '1~12号玩家已全部存在，无需重复添加。')
        return redirect('index')
    return redirect('index')

def set_police_identity(request):
    """设置警察身份"""
    # 获取现有的警察身份设置，如果不存在则创建新的
    police_identity = PoliceIdentity.objects.first()
    
    if request.method == 'POST':
        if police_identity:
            # 编辑现有的警察身份
            form = PoliceIdentityForm(request.POST, instance=police_identity)
        else:
            # 创建新的警察身份
            form = PoliceIdentityForm(request.POST)
        
        if form.is_valid():
            form.save()
            messages.success(request, '警察身份设置成功！')
            return redirect('index')
    else:
        if police_identity:
            # 编辑现有的警察身份
            form = PoliceIdentityForm(instance=police_identity)
        else:
            # 创建新的警察身份
            form = PoliceIdentityForm()
    
    return render(request, 'inference/set_police_identity.html', {'form': form})

@csrf_exempt
@require_http_methods(["POST"])
def ajax_inference(request):
    """AJAX推理接口"""
    try:
        data = json.loads(request.body)
        
        # 获取所有数据
        night_checks = NightCheck.objects.all()
        death_events = DeathEvent.objects.all()
        judgments = Judgment.objects.all()
        werewolf_adjustments = WerewolfProbabilityAdjustment.objects.all()
        police_identity = PoliceIdentity.objects.first()
        
        # 转换数据格式
        checks = []
        deaths = []
        judgments_data = []
        werewolf_adjustments_data = []
        
        for check in night_checks:
            checks.append({
                "checker": check.checker,
                "target": check.target.number,
                "result": check.result
            })
        
        for death in death_events:
            deaths.append({
                "player": death.player.number,
                "type": death.event_type
            })
        
        for judgment in judgments:
            judgments_data.append({
                "player": judgment.player.number,
                "label": judgment.label
            })
        
        for adjustment in werewolf_adjustments:
            werewolf_adjustments_data.append({
                "player": adjustment.player.number,
                "probability_increase": float(adjustment.probability_increase),
                "reason": adjustment.reason
            })
        
        # 执行推理 - 需要警察身份信息
        results = {"A": [], "B": []}
        analysis_A = {}
        analysis_B = {}
        recommendations = []
        
        if police_identity:
            # 使用新的推理引擎，传入警察身份
            police_b_number = police_identity.police_b.number if police_identity.police_b else None
            results = compare_scenarios_with_police_identity(
                checks, deaths, judgments_data, 
                police_identity.police_a.number, 
                police_b_number
            )
            
            # 分析结果
            analysis_A = analyze_solutions(results["A"]) if results["A"] else {}
            analysis_B = analyze_solutions(results["B"]) if results["B"] else {}
            
            # 应用匪徒概率调整
            if werewolf_adjustments_data:
                analysis_A = apply_werewolf_probability_adjustments(analysis_A, werewolf_adjustments_data)
                analysis_B = apply_werewolf_probability_adjustments(analysis_B, werewolf_adjustments_data)
            
            # 获取建议
            recommendations = get_recommendations(results)
        
        return JsonResponse({
            'success': True,
            'results': {
                'A_count': len(results["A"]),
                'B_count': len(results["B"])
            },
            'analysis_A': analysis_A,
            'analysis_B': analysis_B,
            'recommendations': recommendations,
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

def initialize_and_clear_data(request):
    """初始化并清空所有数据"""
    if request.method == 'POST':
        # 清空所有数据
        NightCheck.objects.all().delete()
        DeathEvent.objects.all().delete()
        Judgment.objects.all().delete()
        WerewolfProbabilityAdjustment.objects.all().delete()
        OppositionGroup.objects.all().delete()
        Player.objects.all().delete()
        PoliceIdentity.objects.all().delete()
        messages.success(request, '所有数据已初始化并清空！游戏可以重新开始。')
        return redirect('index')
    
    return render(request, 'inference/initialize_and_clear_data.html')

def add_werewolf_probability(request):
    """增加匪徒概率"""
    if request.method == 'POST':
        form = WerewolfProbabilityAdjustmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '匪徒概率调整已保存！')
            return redirect('index')
    else:
        form = WerewolfProbabilityAdjustmentForm()
    
    return render(request, 'inference/add_werewolf_probability.html', {'form': form})

def add_opposition_group(request):
    """添加对立组合"""
    if request.method == 'POST':
        form = OppositionGroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '对立组合已保存！')
            return redirect('index')
    else:
        form = OppositionGroupForm()
    
    return render(request, 'inference/add_opposition_group.html', {'form': form})
