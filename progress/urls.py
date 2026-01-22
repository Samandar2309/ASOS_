from django.urls import path

from .views import (
    MyProgressView,
    MyXPTransactionsView,
    GlobalLeaderboardView,
    CenterLeaderboardView,
    GroupLeaderboardView,
    AdminXPGrantView,
)
urlpatterns = [
    # My progress
    path(
        'me/',
        MyProgressView.as_view(),
        name='my-progress'
    ),
    path(
        'me/xp-history/',
        MyXPTransactionsView.as_view(),
        name='my-xp-history'
    ),

    # Leaderboards
    path(
        'leaderboard/global/',
        GlobalLeaderboardView.as_view(),
        name='leaderboard-global'
    ),
    path(
        'leaderboard/center/<int:center_id>/',
        CenterLeaderboardView.as_view(),
        name='leaderboard-center'
    ),
    path(
        'leaderboard/group/<uuid:group_id>/',
        GroupLeaderboardView.as_view(),
        name='leaderboard-group'
    ),

    # Admin actions
    path(
        'admin/xp-grant/',
        AdminXPGrantView.as_view(),
        name='admin-xp-grant'
    ),
]
