from django.db import models

# Create your models here.

class Player(models.Model):
    """玩家模型"""
    number = models.IntegerField(unique=True, verbose_name="玩家编号")
    nickname = models.CharField(max_length=50, blank=True, verbose_name="昵称")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "玩家"
        verbose_name_plural = "玩家"
    
    def __str__(self):
        return f"{self.number}号玩家"

class PoliceIdentity(models.Model):
    """警察身份设置"""
    police_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='police_a_identity', verbose_name="警察A")
    police_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='police_b_identity', verbose_name="警察B", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "警察身份"
        verbose_name_plural = "警察身份"
    
    def __str__(self):
        if self.police_b:
            return f"警察A: {self.police_a}, 警察B: {self.police_b}"
        else:
            return f"警察A: {self.police_a} (暂未设置警察B)"

class NightCheck(models.Model):
    """夜晚查验记录"""
    CHECKER_CHOICES = [
        ('A', '警察A'),
        ('B', '警察B'),
    ]
    RESULT_CHOICES = [
        ('good', '好人'),
        ('bad', '匪徒'),
    ]
    
    checker = models.CharField(max_length=1, choices=CHECKER_CHOICES, verbose_name="查验者")
    target = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="被查验者")
    result = models.CharField(max_length=4, choices=RESULT_CHOICES, verbose_name="查验结果")
    night_number = models.IntegerField(default=1, verbose_name="第几夜")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "夜晚查验"
        verbose_name_plural = "夜晚查验"
        ordering = ['night_number', 'created_at']
    
    def __str__(self):
        return f"第{self.night_number}夜 {self.get_checker_display()}查验{self.target}为{self.get_result_display()}"

class DeathEvent(models.Model):
    """死亡事件"""
    EVENT_TYPE_CHOICES = [
        ('kill', '夜晚被杀'),
        ('vote', '白天处决'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="死亡玩家")
    event_type = models.CharField(max_length=4, choices=EVENT_TYPE_CHOICES, verbose_name="事件类型")
    night_number = models.IntegerField(default=1, verbose_name="第几夜/天")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "死亡事件"
        verbose_name_plural = "死亡事件"
        ordering = ['night_number', 'created_at']
    
    def __str__(self):
        return f"第{self.night_number}{'夜' if self.event_type == 'kill' else '天'} {self.player}被{self.get_event_type_display()}"

class Judgment(models.Model):
    """主观判断记录"""
    LABEL_CHOICES = [
        ('good', '好人'),
        ('bad', '匪徒'),
    ]
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="玩家")
    label = models.CharField(max_length=4, choices=LABEL_CHOICES, verbose_name="判断")
    reason = models.TextField(blank=True, verbose_name="判断理由")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "主观判断"
        verbose_name_plural = "主观判断"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.player}判断为{self.get_label_display()}"

class WerewolfProbabilityAdjustment(models.Model):
    """匪徒概率调整记录"""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, verbose_name="目标玩家")
    probability_increase = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="增加概率(%)")
    reason = models.TextField(verbose_name="调整原因")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "匪徒概率调整"
        verbose_name_plural = "匪徒概率调整"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.player}增加匪徒概率{self.probability_increase}% - {self.reason[:20]}..."

class OppositionGroup(models.Model):
    """对立组合模型"""
    name = models.CharField(max_length=100, verbose_name="组合名称")
    players = models.ManyToManyField(Player, verbose_name="对立玩家")
    reason = models.TextField(blank=True, verbose_name="对立原因")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "对立组合"
        verbose_name_plural = "对立组合"
        ordering = ['-created_at']
    
    def __str__(self):
        player_numbers = [str(player.number) for player in self.players.all()]
        return f"{self.name} ({', '.join(player_numbers)}号)"
    
    def get_player_numbers(self):
        """获取玩家编号列表"""
        return [player.number for player in self.players.all().order_by('number')]
