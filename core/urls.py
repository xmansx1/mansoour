from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from .views import delete_property_image_ajax
from .views import upload_property_image


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
    path('property/<int:pk>/reserve/', views.reserve_property, name='reserve_property'),
    path('property/<int:pk>/cancel-reservation/', views.cancel_property_reservation, name='cancel_property_reservation'),
    path('property/<int:pk>/execute/', views.execute_property, name='execute_property'),
    path('property/<int:pk>/cancel-execution/', views.cancel_property_execution, name='cancel_property_execution'),
    path('delete-image/<int:image_id>/', delete_property_image_ajax, name='delete_property_image_ajax'),

    # 🔐 تسجيل الدخول والخروج والتسجيل
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('delete-image/<int:image_id>/', views.delete_property_image, name='delete_property_image'),
    path('upload-image/<int:property_id>/', upload_property_image, name='upload_property_image'),

    # 🧑‍💼 لوحة تحكم الوسيط
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/add-property/', views.add_property_view, name='add_property'),
    path('dashboard/my-properties/', views.my_properties_view, name='my_properties'),
    path('dashboard/my-properties/<int:property_id>/edit/', views.edit_property, name='edit_property'),

    path('dashboard/my-properties/<int:pk>/delete/', views.delete_property_view, name='delete_property'),
    path('dashboard/my-requests/', views.my_executed_requests_view, name='my_executed_requests'),
    path('requests/<int:request_id>/reserve/', views.reserve_customer_request, name='reserve_request'),
    path('requests/<int:request_id>/cancel-reservation/', views.cancel_reservation, name='cancel_reservation'),
    path('admin-panel/properties/<int:property_id>/edit/', views.admin_edit_property, name='admin_edit_property'),
    path('admin-panel/properties/<int:property_id>/delete/', views.admin_delete_property, name='admin_delete_property'),
 
    # 🛠️ لوحة تحكم الأدمن
    path('admin-panel/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin-panel/agents/', views.agents_list_view, name='agents_list'),
    path('admin-panel/agents/add/', views.create_agent_view, name='admin_add_agent'),
    path('admin-panel/agents/<int:pk>/edit/', views.edit_agent, name='admin_edit_agent'),
    path('admin-panel/agents/<int:pk>/delete/', views.delete_agent_view, name='admin_delete_agent'),
    path('admin-panel/requests/', views.all_requests_admin_view, name='admin_all_requests'),
    path('admin-panel/requests/<int:request_id>/edit/', views.admin_edit_request_view, name='admin_edit_request'),
    path('admin-panel/requests/<int:request_id>/delete/', views.admin_delete_request_view, name='admin_delete_request'),
    path('properties/add/', views.add_property_view, name='add_property'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 


#mansour