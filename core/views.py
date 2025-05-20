from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from urllib.parse import quote
from django.db.models import Count
from .models import (
    Property, CustomUser, CustomerRequest, Execution,
    CustomerRequestImage, PropertyImage
)
from .forms import (
    CustomerRequestForm, PropertyForm,
    CustomUserCreationForm, CustomLoginForm, CustomUserUpdateForm
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from core.models import Property  # تأكد من وجود هذا السطر
from core.models import CustomerRequest, Execution
from django.views.decorators.csrf import csrf_exempt

import cloudinary.uploader

# ===================================================
# 📍 الصفحات العامة
# ===================================================
def home_view(request):
    city = request.GET.get('city')
    property_type = request.GET.get('type')
    offer_type = request.GET.get('offer')

    for_sale = Property.objects.filter(offer_type='sale', executed_by__isnull=True)
    for_rent = Property.objects.filter(offer_type='rent', executed_by__isnull=True)


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
    context = {
        "property": property,
        "images": images,
        "whatsapp_message": encoded_msg
    }
    return render(request, 'core/property_detail.html', context)

# ===================================================
# 🗓️ استقبال طلبات العملاء
# ===================================================
def request_form_view(request):
    if request.method == 'POST':
        form = CustomerRequestForm(request.POST)
        if form.is_valid():
            customer_request = form.save()
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

    my_property_count = Property.objects.filter(owner=request.user).count()

    # عدد الطلبات المنفذة
    executed_count = Execution.objects.filter(agent=request.user).count()

    # عدد الطلبات المحجوزة
    reserved_count = CustomerRequest.objects.filter(status='reserved', reserved_by=request.user).count()

    context = {
        'user': request.user,
        'my_property_count': my_property_count,
        'executed_count': executed_count,
        'reserved_count': reserved_count,
    }

    return render(request, 'core/dashboard.html', context)



@login_required
def add_property_view(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.owner = request.user
            property_obj.save()

            # حفظ الصور المتعددة
            for image in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=property_obj, image=image)

            messages.success(request, '✅ تم إضافة العقار بنجاح.')

            # التوجيه حسب نوع المستخدم
            if request.user.user_type == 'admin':
                return redirect('admin_dashboard')
            return redirect('dashboard')
    else:
        form = PropertyForm()

    return render(request, 'core/add_property.html', {'form': form})



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


@login_required
def my_properties_view(request):
    properties = Property.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'core/my_properties.html', {'properties': properties})

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from .models import Property, PropertyImage
from .forms import PropertyForm

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()

            # ✅ حفظ الصور الجديدة المرفوعة
            for img in request.FILES.getlist('images'):
                PropertyImage.objects.create(property=property_obj, image=img)

            # ✅ عرض رسالة نجاح
            messages.success(request, "✅ تم حفظ التعديلات بنجاح.")

            # ✅ توجيه الجميع (المستخدم أو الآدمن) لنفس صفحة التعديل
            return redirect('edit_property', property_id=property_id)
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'core/edit_property.html', {
        'form': form,
        'property': property_obj,
    })






from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Property

# إنشاء مجموعة جديدة
agents_group, created = Group.objects.get_or_create(name="الوكلاء")

# إضافة صلاحية معينة
content_type = ContentType.objects.get_for_model(Property)
permission = Permission.objects.get(
    codename='change_property',
    content_type=content_type,
)
agents_group.permissions.add(permission)


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
    return user.is_authenticated and user.user_type in ['agent', 'admin']

@login_required
@user_passes_test(is_agent)
def reserve_customer_request(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, pk=request_id)
    if customer_request.status == 'open':
        customer_request.status = 'reserved'
        customer_request.reserved_by = request.user
        customer_request.save()
        messages.success(request, f'✅ تم حجز الطلب بواسطة {request.user.username}')
    else:
        messages.warning(request, '⚠️ لا يمكن حجز هذا الطلب')
    return redirect('customer_requests')



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
        return redirect('agents_list')
    return render(request, 'core/admin_delete_agent_confirm.html', {'agent': agent})

@login_required
@user_passes_test(is_admin)

def admin_dashboard_view(request):
    total_agents = CustomUser.objects.filter(user_type='agent').count()
    total_requests = CustomerRequest.objects.count()
    total_properties = Property.objects.count()
    all_properties = Property.objects.all().order_by('-created_at')
    open_requests = CustomerRequest.objects.filter(status='open').order_by('-created_at')

    # ✅ إحصائيات نوع العرض
    rent_count = Property.objects.filter(offer_type='rent').count()
    sell_count = Property.objects.filter(offer_type='sale').count()

    context = {
        'total_agents': total_agents,
        'total_requests': total_requests,
        'total_properties': total_properties,
        'open_requests': open_requests,
        'all_properties': all_properties,
        'rent_count': rent_count,
        'sell_count': sell_count,
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


@login_required
@user_passes_test(is_agent)
def cancel_reservation(request, request_id):
    customer_request = get_object_or_404(CustomerRequest, pk=request_id)
    
    if customer_request.status == 'reserved' and customer_request.reserved_by == request.user:
        customer_request.status = 'open'
        customer_request.reserved_by = None
        customer_request.save()
        messages.success(request, '✅ تم إلغاء الحجز بنجاح.')
    else:
        messages.error(request, '❌ لا يمكنك إلغاء هذا الحجز.')
    
    return redirect('customer_requests')

@login_required
@user_passes_test(is_admin)
def admin_edit_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property)
        if form.is_valid():
            form.save()
            messages.success(request, '✅ تم تعديل العقار بنجاح')
            return redirect('admin_dashboard')
    else:
        form = PropertyForm(instance=property)

    return render(request, 'core/admin_edit_property.html', {'form': form, 'property': property})
@login_required
@user_passes_test(is_admin)
def admin_delete_property(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    property.delete()
    messages.success(request, '🗑️ تم حذف العقار بنجاح')
    return redirect('admin_dashboard')
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .forms import PropertyForm

def is_admin(user):
    return user.is_authenticated and user.user_type == 'admin'


from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Property

@login_required
def reserve_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.reserved_by:
        messages.warning(request, "العقار محجوز بالفعل.")
    else:
        property.reserved_by = request.user
        property.save()
        messages.success(request, "تم حجز العقار بنجاح.")
    return redirect('property_detail', pk=pk)

@login_required
def cancel_property_reservation(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.reserved_by == request.user:
        property.reserved_by = None
        property.save()
        messages.success(request, "تم إلغاء الحجز.")
    else:
        messages.warning(request, "لا يمكنك إلغاء هذا الحجز.")
    return redirect('property_detail', pk=pk)

@login_required
def execute_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.executed_by:
        messages.warning(request, "العقار تم تنفيذه بالفعل.")
    else:
        property.executed_by = request.user
        property.save()
        messages.success(request, "تم تنفيذ العقار.")
    return redirect('property_detail', pk=pk)

@login_required
def cancel_property_execution(request, pk):
    property = get_object_or_404(Property, pk=pk)
    if property.executed_by == request.user:
        property.executed_by = None
        property.save()
        messages.success(request, "تم إلغاء التنفيذ.")
    else:
        messages.warning(request, "لا يمكنك إلغاء هذا التنفيذ.")
    return redirect('property_detail', pk=pk)

# views.py
from cloudinary.uploader import destroy  # ✅ استيراد الحذف الصحيح من Cloudinary

@login_required
@csrf_exempt
def delete_property_image(request, image_id):
    if request.method == 'POST':
        try:
            image = PropertyImage.objects.get(id=image_id)

            if image.property.owner == request.user or request.user.is_staff:
                # ✅ حذف الصورة من Cloudinary باستخدام public_id
                if image.image:
                    public_id = image.image.public_id
                    destroy(public_id)

                # حذف من قاعدة البيانات فقط
                image.delete()
                return JsonResponse({'success': True})

            return JsonResponse({'error': 'غير مصرح لك بالحذف'}, status=403)
        except PropertyImage.DoesNotExist:
            return JsonResponse({'error': 'الصورة غير موجودة'}, status=404)

    return JsonResponse({'error': 'طلب غير صالح'}, status=400)


import cloudinary.uploader  # تأكد من وجود هذا السطر

@csrf_exempt
def delete_property_image_ajax(request, image_id):
    if request.method == "POST":
        try:
            image = PropertyImage.objects.get(id=image_id)

            # حذف الصورة من Cloudinary
            public_id = image.image.public_id
            cloudinary.uploader.destroy(public_id)

            # حذف من قاعدة البيانات
            image.delete()

            return JsonResponse({"success": True})
        except PropertyImage.DoesNotExist:
            return JsonResponse({"error": "الصورة غير موجودة"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "الطريقة غير مدعومة"}, status=405)




from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Property, PropertyImage

@csrf_exempt
@login_required
def upload_property_image(request, property_id):
    if request.method == 'POST' and request.FILES.get('image'):
        property_obj = Property.objects.get(id=property_id, owner=request.user)
        image = request.FILES['image']
        PropertyImage.objects.create(property=property_obj, image=image)
        return JsonResponse({'message': 'تم رفع الصورة بنجاح'})
    return JsonResponse({'error': 'طلب غير صالح'}, status=400)
