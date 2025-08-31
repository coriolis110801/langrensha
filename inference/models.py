from django.db import models
from django.core.exceptions import ValidationError

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
    """对立组合记录"""
    player_a = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='opposition_as_a', verbose_name="玩家A")
    player_b = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='opposition_as_b', verbose_name="玩家B")
    reason = models.TextField(verbose_name="对立原因")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "对立组合"
        verbose_name_plural = "对立组合"
        ordering = ['-created_at']
        # 确保同一对玩家不会重复添加
        unique_together = ['player_a', 'player_b']
    
    def __str__(self):
        return f"{self.player_a} vs {self.player_b} - {self.reason[:20]}..."
    
    def clean(self):
        """验证玩家不能和自己对立"""
        if self.player_a == self.player_b:
            raise ValidationError("玩家不能和自己对立！")
    
    def save(self, *args, **kwargs):
        """确保player_a的编号总是小于player_b的编号，避免重复"""
        if self.player_a.number > self.player_b.number:
            self.player_a, self.player_b = self.player_b, self.player_a
        super().save(*args, **kwargs)

class GameplayGuide(models.Model):
    """玩法思路记录"""
    ROLE_CHOICES = [
        ('police', '预言家'),
        ('villager', '平民'),
        ('mafia', '狼人'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, verbose_name="角色")
    title = models.CharField(max_length=100, verbose_name="标题")
    content = models.TextField(verbose_name="内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    class Meta:
        verbose_name = "玩法思路"
        verbose_name_plural = "玩法思路"
        ordering = ['role', '-created_at']
    
    def __str__(self):
        return f"{self.get_role_display()} - {self.title}"
