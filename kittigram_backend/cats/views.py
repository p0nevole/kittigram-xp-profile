from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .models import Achievement, Cat, Profile, XPActionRule
from .permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly
from .serializers import (
    AchievementSerializer,
    CatSerializer,
    ManualXPGrantSerializer,
    ProfileSerializer,
    XPActionRuleSerializer,
    XPEventSerializer,
)
from .services import add_xp


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.select_related('owner').prefetch_related('achievements')
    serializer_class = CatSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAuthenticated, IsOwnerOrReadOnly)

    def perform_create(self, serializer):
        cat = serializer.save(owner=self.request.user)

        add_xp(
            user=self.request.user,
            action=XPActionRule.CAT_CREATED,
            object_id=cat.id,
        )

        if cat.image:
            add_xp(
                user=self.request.user,
                action=XPActionRule.IMAGE_UPLOADED,
                object_id=cat.id,
            )

        achievements_count = cat.achievements.count()
        if achievements_count:
            add_xp(
                user=self.request.user,
                action=XPActionRule.ACHIEVEMENT_ADDED,
                object_id=cat.id,
                multiplier=achievements_count,
            )

    def perform_update(self, serializer):
        cat_before = self.get_object()
        old_achievement_ids = set(
            cat_before.achievements.values_list('id', flat=True)
        )
        had_image = bool(cat_before.image)

        cat = serializer.save()

        add_xp(
            user=self.request.user,
            action=XPActionRule.CAT_UPDATED,
            object_id=cat.id,
        )

        new_achievement_ids = set(
            cat.achievements.values_list('id', flat=True)
        )
        added_achievements_count = len(
            new_achievement_ids - old_achievement_ids
        )

        if added_achievements_count:
            add_xp(
                user=self.request.user,
                action=XPActionRule.ACHIEVEMENT_ADDED,
                object_id=cat.id,
                multiplier=added_achievements_count,
            )

        if not had_image and cat.image:
            add_xp(
                user=self.request.user,
                action=XPActionRule.IMAGE_UPLOADED,
                object_id=cat.id,
            )


class AchievementViewSet(viewsets.ModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=('get',), url_path='me')
    def me(self, request):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=('get',), url_path='me/events')
    def events(self, request):
        events = request.user.xp_events.select_related('rule').all()
        action = request.query_params.get('action')

        if action:
            events = events.filter(action=action)

        page = self.paginate_queryset(events)
        if page is not None:
            serializer = XPEventSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = XPEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=('get',), url_path='leaderboard')
    def leaderboard(self, request):
        profiles = Profile.objects.select_related('user').order_by(
            '-xp',
            'user__username',
        )

        page = self.paginate_queryset(profiles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(profiles, many=True)
        return Response(serializer.data)

class XPActionRuleViewSet(viewsets.ModelViewSet):
    queryset = XPActionRule.objects.all()
    serializer_class = XPActionRuleSerializer
    pagination_class = None
    permission_classes = (IsAuthenticated, IsAdminOrReadOnly)

    @action(
        detail=True,
        methods=('post',),
        url_path='grant',
        permission_classes=(IsAdminUser,),
    )
    def grant(self, request, pk=None):
        rule = self.get_object()
        serializer = ManualXPGrantSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        profile = add_xp(
            user=serializer.validated_data['user_id'],
            action=rule.code,
            object_id=serializer.validated_data.get('object_id'),
            multiplier=serializer.validated_data.get('multiplier', 1),
        )

        response_serializer = ProfileSerializer(profile)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)