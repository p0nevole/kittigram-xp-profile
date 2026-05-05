from django.contrib import admin

# Register your models here.
from .models import Achievement, AchievementCat, Cat, Profile, XPActionRule, XPEvent

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'xp', 'level', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('level', 'current_level_xp', 'xp_to_next_level')


@admin.register(XPActionRule)
class XPActionRuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'title', 'points', 'is_active', 'once_per_object')
    list_filter = ('is_active', 'once_per_object')
    search_fields = ('code', 'title')


@admin.register(XPEvent)
class XPEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'action', 'points', 'object_id', 'created_at')
    search_fields = ('user__username', 'action')
    list_filter = ('action', 'created_at')
    readonly_fields = ('user', 'rule', 'action', 'points', 'object_id', 'created_at')