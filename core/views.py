from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Property, CustomUser, CustomerRequest, Execution, CustomerRequestImage
from .forms import CustomerRequestForm, PropertyForm, CustomUserCreationForm, CustomLoginForm
from .models import CustomerRequestImage 
from .models import PropertyImage

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

from urllib.parse import quote

def property_detail_view(request, pk):
    property = get_object_or_404(Property, pk=pk)
    images = PropertyImage.objects.filter(property=property)

    # نص الرسالة
    msg = (
        f"مرحبًا، اطلعت على إعلان العقار التالي:\n\n"
        f"نوع العقار: {property.get_property_type_display()}\n"
        f"الموقع: حي {property.district} - {property.city}\n"
        f"السعر: {int(property.price)} ريال\n\n"
        f"أرغب بمعرفة المزيد من التفاصيل، وهل العقار ما زال متاحًا؟\n"
        f"{request.build_absolute_uri()}\n\n"
        f"📩 تم إرسال هذا الطلب من منصة خطوة وسيط"
    )

    # ترميز الرسالة لربط واتساب
    encoded_msg = quote(msg)

    context = {
        "property": property,
        "images": images,
        "whatsapp_message": encoded_msg
    }
    return render(request, 'core/property_detail.html', context)


# ===================================================
# 🗓️ استقبال طلبات العملاء
# ===================================================


from .models import CustomerRequestImage

def request_form_view(request):
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST, request.FILES)
        if form.is_valid():
            customer_request = form.save()

            # حفظ الصور المتعددة
            for image in request.FILES.getlist('images'):
                CustomerRequestImage.objects.create(request=customer_request, image=image)

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

    context = {
        'requests': requests,
        'selected_city': city or '',
        'selected_district': district or '',
        'selected_type': request_type or '',
    }
    return render(request, 'core/customer_requests.html', context)

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
            user = form.get_user()
            login(request, user)
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
@login_required
def dashboard_view(request):
    if request.user.user_type == 'admin':
        return redirect('admin_dashboard')
    return render(request, 'core/dashboard.html', {'user': request.user})

@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()

            # ✅ الصور داخل البلوك الصحيح
            images = request.FILES.getlist('images')
            for image in images:
                PropertyImage.objects.create(property=property_obj, image=image)

            messages.success(request, '✅ تم إضافة العقار بنجاح.')
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'core/add_property.html', {'form': form})







@login_required
def my_properties_view(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'core/my_properties.html', {'properties': properties})

@login_required
def edit_property_view(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل العقار بنجاح.')
            return redirect('my_properties')
    else:
        form = PropertyForm(instance=property)
    return render(request, 'core/edit_property.html', {'form': form, 'property': property})

@login_required
def delete_property_view(request, pk):
    property = get_object_or_404(Property, pk=pk, owner=request.user)
    if request.method == 'POST':
        property.delete()
        messages.success(request, 'تم حذف العقار بنجاح.')
        return redirect('my_properties')
    return render(request, 'core/delete_property_confirm.html', {'property': property})

@login_required
def my_executed_requests_view(request):
    executions = request.user.execution_set.select_related('customer_request').order_by('-executed_at')
    return render(request, 'core/my_executed_requests.html', {'executions': executions})

# ===================================================
# ✅ تنفيذ طلبات العملاء
# ===================================================
def is_agent(user):
    return user.is_authenticated and user.user_type == 'agent'

@login_required
@user_passes_test(is_agent)
def execute_customer_request(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, pk=request_id)
    if customer_request.status == 'open':
        Execution.objects.create(customer_request=customer_request, agent=request.user)
        customer_request.status = 'executed'
        customer_request.save()
    return redirect('customer_requests')

# ===================================================
# 🛠️ لوحة تحكم الأدمن
# ===================================================
def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'

@login_required
@user_passes_test(is_admin)
def agents_list_view(request):
    agents = CustomUser.objects.filter(user_type='agent')
    return render(request, 'core/admin_agents_list.html', {'agents': agents})

@login_required
@user_passes_test(is_admin)
def all_requests_admin_view(request):
    requests = CustomerRequest.objects.all().order_by('-created_at')
    city = request.GET.get('city')
    status = request.GET.get('status')
    if city:
        requests = requests.filter(city__icontains=city)
    if status in ['open', 'executed']:
        requests = requests.filter(status=status)
    return render(request, 'core/admin_all_requests.html', {'requests': requests})

from .forms import CustomUserUpdateForm  # تأكد من الاستيراد
 

from django.contrib import messages

def edit_agent(request, pk):
    user = get_object_or_404(CustomUser, pk=pk)

    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=user, user_id=user.id)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم حفظ التعديلات بنجاح.")
            return redirect('admin_edit_agent', pk=user.id)

    else:
        form = CustomUserUpdateForm(instance=user, user_id=user.id)

    return render(request, 'core/admin_edit_agent.html', {'form': form})




@login_required
@user_passes_test(is_admin)
def delete_agent_view(request, pk):
    agent = get_object_or_404(CustomUser, pk=pk, user_type='agent')
    if request.method == 'POST':
        agent.delete()
        messages.success(request, 'تم حذف الوسيط.')
        return redirect('agents_list')  # ✅ هذا هو الاسم في urls.py
    return render(request, 'core/admin_delete_agent_confirm.html', {'agent': agent})

@login_required
@user_passes_test(is_admin)
def admin_dashboard_view(request):
    total_agents = CustomUser.objects.filter(user_type='agent').count()
    total_requests = CustomerRequest.objects.count()
    total_properties = Property.objects.count()
    highest_price = Property.objects.order_by('-price').first()

    context = {
        'total_agents': total_agents,
        'total_requests': total_requests,
        'total_properties': total_properties,
        'highest_price': highest_price,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def create_agent_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'تم إنشاء المستخدم بنجاح.')
            return redirect('admin_agents')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/admin_add_agent.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_edit_request_view(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST, request.FILES, instance=customer_request)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تعديل الطلب بنجاح.')
            return redirect('admin_all_requests')
    else:
        form = CustomerRequestForm(instance=customer_request)
    return render(request, 'core/admin_edit_request.html', {'form': form, 'request_obj': customer_request})

@login_required
@user_passes_test(is_admin)
def admin_delete_request_view(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, id=request_id)
    if request.method == 'POST':
        customer_request.delete()
        messages.success(request, 'تم حذف الطلب بنجاح.')
        return redirect('admin_all_requests')
    return render(request, 'core/admin_delete_request_confirm.html', {'request_obj': customer_request})
