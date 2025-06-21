from django.urls import path # type: ignore
from .import views


urlpatterns = [
    path('', views.home,name='home'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('chatquery/',views.chatquery,name='chatquery'),
    path("get_user_room/",views.get_user_room, name="get_user_room"), 
    path('sales/', views.sales_summariser, name='sales'),
    path('sales/download_pdf/', views.download_pdf, name='download_pdf'),  
    path('predictions/', views.run_churn_prediction, name='predictions'),


]


# Enhanced URL patterns
from django.urls import path
from . import views

urlpatterns = [
    # Existing URLs
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('chatquery/', views.chatquery, name='chatquery'),
    path('get_user_room/', views.get_user_room, name='get_user_room'),
    path('sales_summariser/', views.sales_summariser, name='sales_summariser'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),
    path('run_churn_prediction/', views.run_churn_prediction, name='run_churn_prediction'),
    
    # New enhanced features URLs
    path('segments/', views.customer_segments, name='customer_segments'),
    path('segments/create/', views.create_segment, name='create_segment'),
    path('tasks/', views.tasks_dashboard, name='tasks_dashboard'),
    path('tasks/create/', views.create_task, name='create_task'),
    path('tasks/<int:task_id>/update_status/', views.update_task_status, name='update_task_status'),
    path('campaigns/', views.marketing_campaigns, name='marketing_campaigns'),
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/<int:campaign_id>/send/', views.send_campaign, name='send_campaign'),
    path('analytics/', views.enhanced_analytics, name='enhanced_analytics'),
]

