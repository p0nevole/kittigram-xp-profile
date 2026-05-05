import base64
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers
import webcolors


import datetime as dt

from .models import (
    Achievement,
    AchievementCat,
    Cat,
    Profile,
    XPActionRule,
    XPEvent,
)

User = get_user_model()
class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value
    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class AchievementSerializer(serializers.ModelSerializer):
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'achievement_name')


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class CatSerializer(serializers.ModelSerializer):
    achievements = AchievementSerializer(required=False, many=True)
    color = Hex2NameColor()
    age = serializers.SerializerMethodField()
    image = Base64ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Cat
        fields = (
            'id', 'name', 'color', 'birth_year', 'achievements', 'owner', 'age',
            'image'
            )
        read_only_fields = ('owner',)

    def get_age(self, obj):
        return dt.datetime.now().year - obj.birth_year
    
    def create(self, validated_data):
        if 'achievements' not in self.initial_data:
            cat = Cat.objects.create(**validated_data)
            return cat
        else:
            achievements = validated_data.pop('achievements')
            cat = Cat.objects.create(**validated_data)
            for achievement in achievements:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                    )
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat
                    )
            return cat
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.color = validated_data.get('color', instance.color)
        instance.birth_year = validated_data.get(
            'birth_year', instance.birth_year
            )
        instance.image = validated_data.get('image', instance.image)
        if 'achievements' in validated_data:
            achievements_data = validated_data.pop('achievements')
            lst = []
            for achievement in achievements_data:
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement
                    )
                lst.append(current_achievement)
            instance.achievements.set(lst)

        instance.save()
        return instance
    def validate_birth_year(self, value):
        current_year = dt.datetime.now().year
        if value > current_year:
            raise serializers.ValidationError(
                'Год рождения кота не может быть больше текущего года.'
            )
        if value < 1990:
            raise serializers.ValidationError(
                'Год рождения кота не может быть меньше 1990.'
            )
        return value

    def validate_achievements(self, value):
        names = [item['name'].lower() for item in value]
        if len(names) != len(set(names)):
            raise serializers.ValidationError(
                'Достижения в одной карточке не должны повторяться.'
            )
        return value
class XPActionRuleSerializer(serializers.ModelSerializer):
    code_display = serializers.CharField(source='get_code_display', read_only=True)

    class Meta:
        model = XPActionRule
        fields = (
            'id',
            'code',
            'code_display',
            'title',
            'points',
            'is_active',
            'once_per_object',
        )

    def validate_points(self, value):
        if value <= 0 or value > 500:
            raise serializers.ValidationError(
                'Количество XP должно быть в диапазоне от 1 до 500.'
            )
        return value


class ManualXPGrantSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    object_id = serializers.IntegerField(required=False, allow_null=True)
    multiplier = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=10,
        default=1,
    )

    def validate_user_id(self, value):
        try:
            return User.objects.get(id=value)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError(
                'Пользователь с указанным id не найден.'
            ) from exc


class XPEventSerializer(serializers.ModelSerializer):
    action_display = serializers.CharField(source='rule.title', read_only=True)

    class Meta:
        model = XPEvent
        fields = (
            'id',
            'action',
            'action_display',
            'points',
            'object_id',
            'created_at',
        )
        read_only_fields = fields


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    level = serializers.IntegerField(read_only=True)
    current_level_xp = serializers.IntegerField(read_only=True)
    xp_to_next_level = serializers.IntegerField(read_only=True)
    next_level_xp = serializers.IntegerField(read_only=True)
    recent_events = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'username',
            'xp',
            'level',
            'current_level_xp',
            'xp_to_next_level',
            'next_level_xp',
            'recent_events',
        )
        read_only_fields = fields

    def get_recent_events(self, obj):
        events = obj.user.xp_events.select_related('rule').all()[:10]
        return XPEventSerializer(events, many=True).data