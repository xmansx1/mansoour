from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db import transaction
from urllib.parse import quote
from .models import Property, PropertyImage, CustomerRequest, CustomerRequestImage, CustomUser, Execution
from .forms import PropertyForm, CustomerRequestForm, CustomUserCreationForm, CustomLoginForm, CustomUserUpdateForm
from django import forms

# ===================================================
# 📍 الصفحات العامة
# ===================================================
def home_view(request):
    city = request.GET.get('city')
    property_type = request.GET.get('type')
    offer_type = request.GET.get('offer')

    for_sale = Property.objects.filter(offer_type='sale')
    for_rent = Property.objects.filter(offer_type='rent')

    if city:
        for_sale = for_sale.filter(city__icontains=city)
        for_rent = for_rent.filter(city__icontains=city)

    if property_type:
        for_sale = for_sale.filter(property_type=property_type)
        for_rent = for_rent.filter(property_type=property_type)

    if offer_type:
        for_sale = for_sale.filter(offer_type=offer_type)
        for_rent = for_rent.filter(offer_type=offer_type)

    context = {
        'for_sale': for_sale.order_by('-created_at'),
        'for_rent': for_rent.order_by('-created_at'),
    }
    return render(request, 'core/home.html', context)

def property_detail_view(request, pk):
    property = get_object_or_404(Property, pk=pk)
    images = PropertyImage.objects.filter(property=property)

    msg = (
        f"مرحبًا، اطلعت على إعلان العقار التالي:\n\n"
        f"نوع العقار: {property.get_property_type_display()}\n"
        f"الموقع: حي {property.district} - {property.city}\n"
        f"السعر: {int(property.price)} ريال\n\n"
        f"أرغب بمعرفة المزيد من التفاصيل، وهل العقار ما زال متاحًا؟\n"
        f"{request.build_absolute_uri()}\n\n"
        f"📩 تم إرسال هذا الطلب من منصة خطوة وسيط"
    )
    encoded_msg = quote(msg)
    return render(request, 'core/property_detail.html', {
        "property": property,
        "images": images,
        "whatsapp_message": encoded_msg
    })

# ===================================================
# 🗓️ استقبال طلبات العملاء
# ===================================================
def request_form_view(request):
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST, request.FILES)
        if form.is_valid():
            request_obj = form.save()
            for image in request.FILES.getlist('images'):
                CustomerRequestImage.objects.create(request=request_obj, image=image)
            messages.success(request, '✅ تم إرسال الطلب بنجاح.')
            return redirect('request_success')
    else:
        form = CustomerRequestForm()
    return render(request, 'core/request_form.html', {'form': form})

def request_success_view(request):
    return render(request, 'core/request_success.html')

@login_required
def customer_requests_list(request):
    requests = CustomerRequest.objects.all().order_by('-created_at')
    city = request.GET.get('city')
    district = request.GET.get('district')
    request_type = request.GET.get('request_type')

    if city:
        requests = requests.filter(city__icontains=city)
    if district:
        requests = requests.filter(district__icontains=district)
    if request_type in ['buy', 'sell', 'rent', 'rent_out']:
        requests = requests.filter(request_type=request_type)

    return render(request, 'core/customer_requests.html', {
        'requests': requests,
        'selected_city': city or '',
        'selected_district': district or '',
        'selected_type': request_type or '',
    })

@login_required
def customer_request_detail_view(request, request_id):
    request_obj = get_object_or_404(CustomerRequest, id=request_id)
    images = request_obj.images.all()
    return render(request, 'core/request_detail.html', {'request_obj': request_obj, 'images': images})

# ===================================================
# 👤 مصادقة المستخدم
# ===================================================
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'agent'
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = CustomLoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# ===================================================
# 📊 لوحة تحكم المستخدم
# ===================================================
from django.shortcuts import render
from .models import Property, CustomerRequest, CustomUser  # تأكد من صحة الاستيراد

from django.shortcuts import render
from core.models import Property, CustomerRequest, CustomUser

from django.shortcuts import render
from core.models import Property, CustomerRequest, CustomUser

from django.shortcuts import render
from core.models import Property, CustomerRequest, CustomUser

def dashboard_view(request):
    context = {}

    if request.user.is_authenticated:
        if request.user.user_type == 'admin':
            # إحصائيات عامة تشمل النظام بالكامل
            context.update({
                'total_agents': CustomUser.objects.filter(user_type='agent').count(),
                'total_requests': CustomerRequest.objects.count(),
                'total_properties': Property.objects.count(),

                'total_rent_properties': Property.objects.filter(offer_type='rent').count(),
                'total_sale_properties': Property.objects.filter(offer_type='sale').count(),

                'executed_requests': CustomerRequest.objects.filter(status__iexact='executed').count(),
                'reserved_requests': CustomerRequest.objects.filter(status__iexact='reserved').count(),
                'open_requests': CustomerRequest.objects.filter(status__iexact='open'),

                'highest_price': Property.objects.order_by('-price').first(),
            })
        else:
            # إحصائيات خاصة بالمستخدم الحالي (الوسيط/العميل)
            user_properties = Property.objects.filter(owner=request.user)
            context.update({
                'total_properties': user_properties.count(),
                'reserved_count': user_properties.filter(status='reserved').count(),
                'executed_count': user_properties.filter(status='executed').count(),
            })

    return render(request, 'core/dashboard.html', context)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import Property

@login_required
def admin_properties_list(request):
    if request.user.user_type != 'admin':
        return redirect('dashboard')

    properties = Property.objects.all().order_by('-created_at')
    return render(request, 'core/admin_properties_list.html', {'properties': properties})






@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            for image in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=obj, image=image)
            messages.success(request, '✅ تم إضافة العقار بنجاح.')
            return redirect('dashboard')
    else:
        form = PropertyForm()
        # إخفاء الحقول غير المرغوبة
        for field_name in ['status', 'reserved_by', 'reserved_at', 'executed_by', 'executed_at']:
            if field_name in form.fields:
                form.fields[field_name].widget = forms.HiddenInput()
    return render(request, 'core/add_property.html', {'form': form})


@login_required
def my_properties_view(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'core/my_properties.html', {'properties': properties})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, PropertyImage
from .forms import PropertyForm

@login_required
def edit_property_view(request, pk):
    # ✅ إذا كان المستخدم أدمن، يمكنه تعديل أي عقار
    if request.user.user_type == 'admin':
        property_obj = get_object_or_404(Property, pk=pk)
    else:
        # ✅ الوسيط لا يمكنه تعديل إلا عقاراته فقط
        property_obj = get_object_or_404(Property, pk=pk, owner=request.user)

    # ✅ إذا كانت عملية تعديل أو حذف صورة
    if request.method == 'POST':
        # حذف صورة واحدة
        if 'delete_image_id' in request.POST:
            PropertyImage.objects.filter(id=request.POST['delete_image_id'], property=property_obj).delete()
            return redirect('edit_property', pk=pk)

        # استبدال صورة واحدة
        if 'replace_image_id' in request.POST and 'replace_image_file' in request.FILES:
            image_obj = PropertyImage.objects.filter(id=request.POST['replace_image_id'], property=property_obj).first()
            if image_obj:
                image_obj.image = request.FILES['replace_image_file']
                image_obj.save()
            return redirect('edit_property', pk=pk)

        # تحديث بيانات النموذج
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()

            # إضافة صور جديدة إن وُجدت
            for image in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=property_obj, image=image)

            messages.success(request, '✅ تم تعديل العقار بنجاح.')
            # إعادة التوجيه حسب نوع المستخدم
            if request.user.user_type == 'admin':
                return redirect('admin_properties_list')
            else:
                return redirect('my_properties')

    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'core/edit_property.html', {
        'form': form,
        'property': property_obj,
        'images': PropertyImage.objects.filter(property=property_obj)
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .models import Property

from django.shortcuts import render

@login_required
def delete_property_view(request, pk):
    if request.user.user_type == 'admin':
        property_obj = get_object_or_404(Property, pk=pk)
    else:
        property_obj = get_object_or_404(Property, pk=pk, owner=request.user)

    if request.method == 'POST':
        property_obj.delete()
        if request.user.user_type == 'admin':
            return redirect('admin_properties_list')
        else:
            return redirect('my_properties')

    return render(request, 'core/confirm_delete_property.html', {'property': property_obj})



@login_required
def my_executed_requests_view(request):
    executions = Execution.objects.filter(agent=request.user).order_by('-executed_at')
    return render(request, 'core/my_executed_requests.html', {'executions': executions})

# ===================================================
# 🛠️ تنفيذ / حجز / إلغاء العقارات
# ===================================================
@login_required
def reserve_property_view(request, pk):
    with transaction.atomic():
        property = Property.objects.select_for_update().get(pk=pk)
        if property.status == 'available':
            property.status = 'reserved'
            property.reserved_by = request.user
            property.reserved_at = timezone.now()
            property.executed_by = None
            property.executed_at = None
            property.save()
            messages.success(request, '✅ تم حجز العقار.')
        else:
            messages.warning(request, '⚠️ لا يمكن حجز العقار.')
    return redirect('property_detail', pk=pk)

@login_required
def execute_property_view(request, pk):
    with transaction.atomic():
        property = Property.objects.select_for_update().get(pk=pk)
        if property.status == 'reserved':
            if property.reserved_by != request.user:
                messages.error(request, '⚠️ لا يمكنك تنفيذ هذا العقار لأنه محجوز من قبل وسيط آخر.')
                return redirect('property_detail', pk=pk)

            property.status = 'executed'
            property.executed_by = request.user
            property.executed_at = timezone.now()
            property.save()
            messages.success(request, '🏁 تم تنفيذ العقار.')
        else:
            messages.warning(request, '⚠️ لا يمكن تنفيذ العقار.')
    return redirect('property_detail', pk=pk)


@login_required
def cancel_property_reservation(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if request.user != property.reserved_by and request.user.user_type != 'admin':
        messages.warning(request, "⚠️ لا يمكنك إلغاء الحجز. هذا الحجز ليس من طرفك.")
        return redirect('my_properties')

    property.status = 'available'
    property.reserved_by = None
    property.reserved_at = None
    property.save()

    messages.success(request, "✅ تم إلغاء الحجز بنجاح.")
    return redirect('property_detail', pk=pk)



@login_required
def cancel_property_execution(request, pk):
    property = get_object_or_404(Property, pk=pk)

    if request.user != property.executed_by and request.user.user_type != 'admin':
        messages.warning(request, "⚠️ لا يمكنك إلغاء التنفيذ. هذا التنفيذ ليس من طرفك.")
        return redirect('my_properties')

    property.status = 'available'
    property.executed_by = None
    property.executed_at = None
    property.save()

    messages.success(request, "✅ تم إلغاء التنفيذ بنجاح.")
    return redirect('property_detail', pk=pk)



from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CustomerRequest, Execution

@login_required
@user_passes_test(lambda u: u.user_type in ['agent', 'admin'])
def execute_customer_request(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    if customer_request.status == 'reserved':
        customer_request.status = 'executed'
        customer_request.save()
        Execution.objects.create(customer_request=customer_request, agent=request.user)
        messages.success(request, '✅ تم تنفيذ الطلب بنجاح.')
    else:
        messages.warning(request, '⚠️ لا يمكن تنفيذ الطلب. ربما لم يتم حجزه بعد.')
    return redirect('customer_requests')

from .forms import CustomerRequestForm
from .models import CustomerRequestImage

def add_customer_request_view(request):
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST, request.FILES)
        if form.is_valid():
            customer_request = form.save()
            for image in request.FILES.getlist('images'):
                CustomerRequestImage.objects.create(request=customer_request, image=image)
            messages.success(request, '✅ تم إرسال الطلب بنجاح.')
            return redirect('request_success')
    else:
        form = CustomerRequestForm()
    return render(request, 'core/request_form.html', {'form': form})
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from .models import CustomUser, Property, CustomerRequest


@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def agents_list_view(request):
    agents = CustomUser.objects.filter(user_type='agent')
    return render(request, 'core/admin_agents_list.html', {'agents': agents})
@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def create_agent_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = 'agent'
            user.save()
            messages.success(request, '✅ تم إنشاء الوسيط بنجاح.')
            return redirect('agents_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/admin_add_agent.html', {'form': form})
@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def edit_agent(request, pk):
    agent = get_object_or_404(CustomUser, pk=pk, user_type='agent')
    
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=agent, user_id=agent.id)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم تعديل بيانات الوسيط بنجاح.")
            return redirect('agents_list')
    else:
        form = CustomUserUpdateForm(instance=agent, user_id=agent.id)
    
    return render(request, 'core/admin_edit_agent.html', {'form': form, 'agent': agent})
@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def delete_agent_view(request, pk):
    agent = get_object_or_404(CustomUser, pk=pk, user_type='agent')
    
    if request.method == 'POST':
        agent.delete()
        messages.success(request, '✅ تم حذف الوسيط بنجاح.')
        return redirect('agents_list')
    
    return render(request, 'core/admin_delete_agent_confirm.html', {'agent': agent})
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def all_requests_admin_view(request):
    requests = CustomerRequest.objects.all().order_by('-created_at')
    city = request.GET.get('city')
    status = request.GET.get('status')

    if city:
        requests = requests.filter(city__icontains=city)
    if status in ['open', 'executed', 'reserved']:
        requests = requests.filter(status=status)

    return render(request, 'core/admin_all_requests.html', {
        'requests': requests,
        'selected_city': city or '',
        'selected_status': status or '',
    })
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomerRequest
from .forms import CustomerRequestForm

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def admin_edit_request_view(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST, request.FILES, instance=customer_request)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم تعديل الطلب بنجاح.')
            return redirect('admin_all_requests')
    else:
        form = CustomerRequestForm(instance=customer_request)

    return render(request, 'core/admin_edit_request.html', {
        'form': form,
        'request_obj': customer_request
    })
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from .models import CustomerRequest
from django.contrib import messages

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def admin_delete_request_view(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)

    if request.method == 'POST':
        customer_request.delete()
        messages.success(request, '✅ تم حذف الطلب بنجاح.')
        return redirect('admin_all_requests')

    return render(request, 'core/admin_delete_request_confirm.html', {'request_obj': customer_request})
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Property
from .forms import PropertyForm

# تحقق أن المستخدم هو أدمن
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect('admin_properties_list')
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'core/admin_edit_property.html', {'form': form, 'property': property_obj})

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from .models import Property

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def admin_delete_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    property_obj.delete()
    return redirect('admin_properties_list')


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CustomerRequest

@login_required
@user_passes_test(lambda u: u.user_type in ['agent', 'admin'])
def reserve_customer_request(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    if customer_request.status == 'open':
        customer_request.status = 'reserved'
        customer_request.save()
        messages.success(request, '✅ تم حجز الطلب بنجاح.')
    else:
        messages.warning(request, '⚠️ لا يمكن حجز الطلب. تحقق من حالته الحالية.')
    return redirect('customer_requests')
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import CustomerRequest

@login_required
@user_passes_test(lambda u: u.user_type in ['agent', 'admin'])
def cancel_reservation(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    if customer_request.status == 'reserved':
        customer_request.status = 'open'
        customer_request.save()
        messages.success(request, '✅ تم إلغاء الحجز وإعادة الطلب إلى الحالة المفتوحة.')
    else:
        messages.warning(request, '⚠️ لا يمكن إلغاء الحجز، لأن الطلب ليس في حالة محجوز.')
    return redirect('customer_requests')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import SiteSettingsForm
from .models import SiteSettings

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def site_settings_view(request):
    settings, created = SiteSettings.objects.get_or_create(pk=1)

    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('site_settings')
    else:
        form = SiteSettingsForm(instance=settings)

    return render(request, 'core/site_settings.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def confirm_delete_property_view(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        property_obj.delete()
        messages.success(request, "✅ تم حذف العقار بنجاح.")
        return redirect('admin_properties_list')
    
    return render(request, 'core/confirm_delete_property.html', {'property': property_obj})
