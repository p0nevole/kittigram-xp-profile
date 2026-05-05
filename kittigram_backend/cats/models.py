from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


User = get_user_model()


class Achievement(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


class Cat(models.Model):
    name = models.CharField(max_length=16)
    color = models.CharField(max_length=16)
    birth_year = models.IntegerField()
    owner = models.ForeignKey(
        User, related_name='cats', 
        on_delete=models.CASCADE
        )
    achievements = models.ManyToManyField(Achievement, through='AchievementCat')
    image = models.ImageField(
        upload_to='cats/images/', 
        null=True,  
        default=None
        )

    def __str__(self):
        return self.name


class AchievementCat(models.Model):
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    cat = models.ForeignKey(Cat, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.achievement} {self.cat}'


class Profile(models.Model):

    user = models.OneToOneField(
        User,
        related_name='profile',
        on_delete=models.CASCADE,
    )
    xp = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('user__username',)
        verbose_name = 'Профиль XP'
        verbose_name_plural = 'Профили XP'

    @property
    def level(self):
        return self.xp // 100 + 1

    @property
    def current_level_xp(self):
        return self.xp % 100

    @property
    def xp_to_next_level(self):
        return 100 - self.current_level_xp

    @property
    def next_level_xp(self):
        return self.level * 100

    def __str__(self):
        return f'{self.user.username}: {self.xp} XP'


class XPActionRule(models.Model):

    CAT_CREATED = 'cat_created'
    CAT_UPDATED = 'cat_updated'
    ACHIEVEMENT_ADDED = 'achievement_added'
    IMAGE_UPLOADED = 'image_uploaded'

    ACTION_CHOICES = (
        (CAT_CREATED, 'Создание кота'),
        (CAT_UPDATED, 'Редактирование кота'),
        (ACHIEVEMENT_ADDED, 'Добавление достижения'),
        (IMAGE_UPLOADED, 'Добавление изображения'),
    )

    code = models.CharField(
        max_length=32,
        unique=True,
        choices=ACTION_CHOICES,
    )
    title = models.CharField(max_length=128)
    points = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(1), MaxValueValidator(500)),
    )
    is_active = models.BooleanField(default=True)
    once_per_object = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('code',)
        verbose_name = 'Правило начисления XP'
        verbose_name_plural = 'Правила начисления XP'

    def __str__(self):
        return f'{self.title}: +{self.points} XP'


class XPEvent(models.Model):

    user = models.ForeignKey(
        User,
        related_name='xp_events',
        on_delete=models.CASCADE,
    )
    rule = models.ForeignKey(
        XPActionRule,
        related_name='events',
        on_delete=models.PROTECT,
    )
    action = models.CharField(max_length=32)
    points = models.PositiveIntegerField()
    object_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)
        indexes = (
            models.Index(fields=('user', 'action')),
            models.Index(fields=('object_id',)),
        )
        verbose_name = 'Событие XP'
        verbose_name_plural = 'События XP'

    def __str__(self):
        return f'{self.user.username}: {self.action} +{self.points}'