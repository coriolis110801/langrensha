from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add-player/', views.add_player, name='add_player'),
    path('add-all-players/', views.add_all_players, name='add_all_players'),
    path('set-police-identity/', views.set_police_identity, name='set_police_identity'),
    path('add-night-check/', views.add_night_check, name='add_night_check'),
    path('add-death-event/', views.add_death_event, name='add_death_event'),
    path('add-judgment/', views.add_judgment, name='add_judgment'),
    path('add-werewolf-probability/', views.add_werewolf_probability, name='add_werewolf_probability'),
    path('edit-werewolf-probability/<int:adjustment_id>/', views.edit_werewolf_probability, name='edit_werewolf_probability'),
    path('delete-werewolf-probability/<int:adjustment_id>/', views.delete_werewolf_probability, name='delete_werewolf_probability'),
    path('add-opposition-group/', views.add_opposition_group, name='add_opposition_group'),
    path('edit-opposition-group/<int:opposition_id>/', views.edit_opposition_group, name='edit_opposition_group'),
    path('delete-opposition-group/<int:opposition_id>/', views.delete_opposition_group, name='delete_opposition_group'),
    path('ajax-inference/', views.ajax_inference, name='ajax_inference'),
    path('initialize-and-clear-data/', views.initialize_and_clear_data, name='initialize_and_clear_data'),
] 