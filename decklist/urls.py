from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('decklist/', views.post_decklist, name='post_decklist'),
    path('decklist/<int:pk>/', views.decklist_detail, name='decklist_detail'),
    path('decklist/new/', views.decklist_new, name='decklist_new'),
    path('decklist/new/sample', views.decklist_sample, name='decklist_sample'),
    path('decklist/<int:pk>/edit', views.decklist_edit, name='decklist_edit'),
    path('decklist/simulator/<int:pk>/', views.decklist_simulator_run, name='decklist_simulator_run'),
    path('decklist/simulator/<int:pk>/result/', views.decklist_simulator_results, name='decklist_simulator_result'),
    path('decklist/<int:pk>/card_edit', views.card_edit, name='card_edit'),
    path('decklist/<int:pk>/card_new', views.card_new, name='card_new'),
    path('decklist/<int:pk>/combo_edit', views.combo_edit, name='combo_edit'),
    path('decklist/<int:pk>/combo', views.combo_detail, name='combo_detail'),
    path('decklist/<int:pk>/combo_new', views.combo_new, name='combo_new'),
    path('decklist/<int:pk>/delete', views.delete_deck, name='delete_deck'),
    path('decklist/<int:pk>/card_edit/delete', views.delete_card, name='delete_card'),
    path('decklist/<int:pk>/combo/delete', views.delete_combo, name='delete_combo'),
    path('register_user', views.register_page, name='register_page'),
    path('login_user', auth_views.LoginView.as_view(template_name='decklist/login.html'), name='login_page'),
    path('logout_user', views.logout_user, name='logout_page'),
    # path('logout_user', auth_views.LogoutView.as_view(template_name='decklist/logout.html'), name='logout_page'),
]