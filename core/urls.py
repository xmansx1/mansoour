from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

urlpatterns = [
    # 🏠 صفحات عامة
    path('', views.home_view, name='home'),
    path('request/', views.request_form_view, name='customer_request'),
    path('request/success/', views.request_success_view, name='request_success'),
    path('requests/', views.customer_requests_list, name='customer_requests'),
    path('requests/<int:request_id>/', views.customer_request_detail_view, name='request_detail'),
    path('requests/<int:request_id>/execute/', views.execute_customer_request, name='execute_request'),
    path('property/<int:pk>/', views.property_detail_view, name='property_detail'),
    path('customer-request/add/', views.add_customer_request_view, name='add-customer-request'),
    # 🔐 تسجيل الدخول والخروج والتسجيل
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # 🧑‍💼 لوحة تحكم الوسيط
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/add-property/', views.add_property_view, name='add_property'),
    path('dashboard/my-properties/', views.my_properties_view, name='my_properties'),
    path('dashboard/my-properties/<int:pk>/edit/', views.edit_property_view, name='edit_property'),
    path('dashboard/my-properties/<int:pk>/delete/', views.delete_property_view, name='delete_property'),
    path('dashboard/my-requests/', views.my_executed_requests_view, name='my_executed_requests'),

    # 🛠️ لوحة تحكم الأدمن
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/agents/', views.agents_list_view, name='agents_list'),
    path('admin-panel/agents/add/', views.create_agent_view, name='admin_add_agent'),
    path('admin-panel/agents/<int:pk>/edit/', views.edit_agent, name='admin_edit_agent'),
    path('admin-panel/agents/<int:pk>/delete/', views.delete_agent_view, name='admin_delete_agent'),
    path('admin-panel/requests/', views.all_requests_admin_view, name='admin_all_requests'),
    path('admin-panel/requests/<int:request_id>/edit/', views.admin_edit_request_view, name='admin_edit_request'),
    path('admin-panel/requests/<int:request_id>/delete/', views.admin_delete_request_view, name='admin_delete_request'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


#mansour