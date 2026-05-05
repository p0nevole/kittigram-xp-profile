from django.db import transaction
from django.db.models import F

from .models import Profile, XPActionRule, XPEvent


DEFAULT_XP_RULES = {
    XPActionRule.CAT_CREATED: {
        'title': 'Создание карточки кота',
        'points': 50,
        'once_per_object': True,
    },
    XPActionRule.CAT_UPDATED: {
        'title': 'Редактирование карточки кота',
        'points': 10,
        'once_per_object': False,
    },
    XPActionRule.ACHIEVEMENT_ADDED: {
        'title': 'Добавление достижения кота',
        'points': 20,
        'once_per_object': False,
    },
    XPActionRule.IMAGE_UPLOADED: {
        'title': 'Добавление изображения кота',
        'points': 30,
        'once_per_object': True,
    },
}


def get_or_create_rule(action):
    defaults = DEFAULT_XP_RULES[action]
    rule, _ = XPActionRule.objects.get_or_create(
        code=action,
        defaults={
            'title': defaults['title'],
            'points': defaults['points'],
            'once_per_object': defaults['once_per_object'],
            'is_active': True,
        },
    )
    return rule


@transaction.atomic
def add_xp(user, action, object_id=None, multiplier=1):

    if not user or not user.is_authenticated:
        return None

    rule = get_or_create_rule(action)
    profile, _ = Profile.objects.select_for_update().get_or_create(user=user)

    if not rule.is_active:
        return profile

    if rule.once_per_object and object_id is not None:
        already_added = XPEvent.objects.filter(
            user=user,
            action=action,
            object_id=object_id,
        ).exists()
        if already_added:
            return profile

    points = rule.points * max(multiplier, 1)

    XPEvent.objects.create(
        user=user,
        rule=rule,
        action=action,
        points=points,
        object_id=object_id,
    )

    Profile.objects.filter(pk=profile.pk).update(xp=F('xp') + points)
    profile.refresh_from_db()
    return profile