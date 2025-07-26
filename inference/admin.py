from django.contrib import admin
from .models import Player, NightCheck, DeathEvent, Judgment, PoliceIdentity, WerewolfProbabilityAdjustment, OppositionGroup

# Register your models here.
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['number', 'nickname', 'created_at']
    search_fields = ['number', 'nickname']
    ordering = ['number']

@admin.register(NightCheck)
class NightCheckAdmin(admin.ModelAdmin):
    list_display = ['checker', 'target', 'result', 'night_number', 'created_at']
    list_filter = ['checker', 'result', 'night_number']
    search_fields = ['target__number', 'target__nickname']
    ordering = ['-night_number', '-created_at']

@admin.register(DeathEvent)
class DeathEventAdmin(admin.ModelAdmin):
    list_display = ['player', 'event_type', 'night_number', 'created_at']
    list_filter = ['event_type', 'night_number']
    search_fields = ['player__number', 'player__nickname']
    ordering = ['-night_number', '-created_at']

@admin.register(Judgment)
class JudgmentAdmin(admin.ModelAdmin):
    list_display = ['player', 'label', 'reason', 'created_at']
    list_filter = ['label']
    search_fields = ['player__number', 'player__nickname', 'reason']
    ordering = ['-created_at']

@admin.register(PoliceIdentity)
class PoliceIdentityAdmin(admin.ModelAdmin):
    list_display = ['police_a', 'police_b', 'created_at']
    search_fields = ['police_a__number', 'police_a__nickname', 'police_b__number', 'police_b__nickname']

@admin.register(WerewolfProbabilityAdjustment)
class WerewolfProbabilityAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['player', 'probability_increase', 'reason', 'created_at']
    list_filter = ['probability_increase']
    search_fields = ['player__number', 'player__nickname', 'reason']
    ordering = ['-created_at']

@admin.register(OppositionGroup)
class OppositionGroupAdmin(admin.ModelAdmin):
    list_display = ['player_a', 'player_b', 'reason', 'created_at']
    search_fields = ['player_a__number', 'player_a__nickname', 'player_b__number', 'player_b__nickname', 'reason']
    ordering = ['-created_at']
