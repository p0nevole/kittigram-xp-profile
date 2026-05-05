from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions, routers
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from cats.views import (
    AchievementViewSet,
    CatViewSet,
    ProfileViewSet,
    XPActionRuleViewSet,
)


schema_view = get_schema_view(
    openapi.Info(
        title='Kittygram XP API',
        default_version='v1',
        description='API проекта Kittygram с пользовательским сценарием уровней профиля и XP за действия.',
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

router = routers.DefaultRouter()
router.register(r'cats', CatViewSet, basename='cats')
router.register(r'achievements', AchievementViewSet, basename='achievements')
router.register(r'profiles', ProfileViewSet, basename='profiles')
router.register(r'xp-rules', XPActionRuleViewSet, basename='xp-rules')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/', include(router.urls)),
    path('api/', include('djoser.urls')),
    path('api/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)