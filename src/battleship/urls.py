from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^signup/$', views.signup, name='signup-view'),
    url(r'^login/$', views.login, name='login-view'),
    url(r'^logout/$', views.logout, name='logout-view'),
    url(r'^$', views.index, name='index-view'),
    url(r'^createroom/$', views.create_room, name='create_room-view'),
    url(r'^rooms/$', views.join_room, name='rooms-view'),
    url(r'^room-(?P<room>[0-9]+)/$', views.waiting_room,
        name='waiting-room-view'),
    url(r'^room-(?P<room>[0-9]+)/gameroom$', views.game_room,
        name='game-room-view'),
    url(r'^room-(?P<room>[0-9]+)/gameroom/attack$', views.attack,
        name='attack-view'),
    url(r'^room-(?P<room>[0-9]+)/gameroom/selectvictim$',
        views.select_victim, name='select-victim-view'),
    url(r'^room-(?P<room>[0-9]+)/startgame$', views.start_game,
        name='start-game-view'),
    url(r'^room-(?P<room>[0-9]+)/victim-table-(?P<victim>[0-9]+)$',
        views.victim_table, name='victim-table-view'),
    url(r'^room-(?P<room>[0-9]+)/newplayer$', views.create_player,
        name='create-player-view'),
    url(r'^room-(?P<room>[0-9]+)/table-(?P<table>[0-9]+)$', views.my_table,
        name='my-table-view'),
    url(r'^room-(?P<room>[0-9]+)/table-(?P<table>[0-9]+)/setboats$',
        views.set_boats, name='set-boats-view'),
]
