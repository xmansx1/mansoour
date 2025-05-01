from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import admin_properties_list

urlpatterns = [
    # 🏠 صفحات عامة
    path('', views.home_view, name='home'),
    path('request/', views.request_form_view, name='customer_request'),
    path('request/success/', views.request_success_view, name='request_success'),
    path('requests/', views.customer_requests_list, name='customer_requests'),
    path('requests/<int:request_id>/', views.customer_request_detail_view, name='request_detail'),
    path('requests/<int:request_id>/execute/', views.execute_customer_request, name='execute_request'),
    path('customer-request/add/', views.add_customer_request_view, name='add-customer-request'),
    path('admin-panel/properties/', admin_properties_list, name='admin_properties_list'),

    # 🏘️ تفاصيل العقار
    path('property/<int:pk>/', views.property_detail_view, name='property_detail'),
    path('property/<int:pk>/reserve/', views.reserve_property_view, name='reserve_property'),
    path('property/<int:pk>/execute/', views.execute_property_view, name='execute_property'),
    path('property/<int:pk>/cancel-reservation/', views.cancel_property_reservation, name='cancel_property_reservation'),
    path('property/<int:pk>/cancel-execution/', views.cancel_property_execution, name='cancel_property_execution'),

    # 🔐 الدخول والتسجيل
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('accounts/password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),

    # 🧑‍💼 لوحة تحكم الوسيط/العميل
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/add-property/', views.add_property_view, name='add_property'),
    path('dashboard/my-properties/', views.my_properties_view, name='my_properties'),
    path('dashboard/my-properties/<int:pk>/edit/', views.edit_property_view, name='edit_property'),
    path('dashboard/my-properties/<int:pk>/delete/', views.delete_property_view, name='delete_property'),
    path('dashboard/my-requests/', views.my_executed_requests_view, name='my_executed_requests'),

    # 🛠️ لوحة تحكم الأدمن
    path('admin-panel/agents/', views.agents_list_view, name='admin_agents'),
    path('admin-panel/agents/add/', views.create_agent_view, name='admin_add_agent'),
    path('admin-panel/agents/<int:pk>/edit/', views.edit_agent, name='admin_edit_agent'),
    path('admin-panel/agents/<int:pk>/delete/', views.delete_agent_view, name='admin_delete_agent'),

    path('admin-panel/requests/', views.all_requests_admin_view, name='admin_all_requests'),
    path('admin-panel/requests/<int:request_id>/edit/', views.admin_edit_request_view, name='admin_edit_request'),
    path('admin-panel/requests/<int:request_id>/delete/', views.admin_delete_request_view, name='admin_delete_request'),

    path('admin-panel/properties/<int:property_id>/edit/', views.admin_edit_property, name='admin_edit_property'),
    path('admin-panel/properties/<int:property_id>/delete/', views.admin_delete_property, name='admin_delete_property'),
    path('admin-panel/site-settings/', views.site_settings_view, name='site_settings'),
    path('admin-panel/properties/<int:pk>/confirm-delete/', views.confirm_delete_property_view, name='confirm_delete_property'),

    # ✅ حجز/إلغاء طلب العملاء
    path('requests/<int:request_id>/reserve/', views.reserve_customer_request, name='reserve_request'),
    path('requests/<int:request_id>/cancel-reservation/', views.cancel_reservation, name='cancel_reservation'),

    # 🔐 تغيير كلمة المرور
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='core/change_password.html'), name='change_password'),
    path('change-password/done/', auth_views.PasswordChangeDoneView.as_view(template_name='core/change_password_done.html'), name='password_change_done'),
]

# تفعيل ملفات media و static عند التطوير
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
