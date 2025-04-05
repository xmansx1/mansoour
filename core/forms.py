from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, CustomerRequest, Property


# ✅ ويدجت يدعم رفع ملفات متعددة – مستخدم في فورم الطلب فقط
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# 📷 نموذج طلب عميل مع صور متعددة
class CustomerRequestForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        label='صور الطلب'
    )

    class Meta:
        model = CustomerRequest
        exclude = ['status', 'created_at']
        labels = {
            'full_name': 'الاسم الكامل',
            'phone': 'رقم الجوال',
            'city': 'المدينة',
            'district': 'الحي',
            'area_required': 'المساحة المطلوبة',
            'property_type': 'نوع العقار',
            'request_type': 'نوع الطلب',
            'details': 'تفاصيل إضافية',
            'max_price': 'الحد الأعلى للسعر',
            'payment_method': 'طريقة الدفع',
            'license_number': 'رقم الرخصة',
        }
        widgets = {
            'details': forms.Textarea(attrs={'rows': 4}),
             'area': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# 🏠 نموذج إضافة عقار (بدون الصور – الصور تُعالَج في views.py)
class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        exclude = ['owner', 'created_at']
        labels = {
            'property_type': 'نوع العقار',
            'offer_type': 'نوع العرض',
            'age': 'عمر العقار',
            'area': 'المساحة',
            'price': 'السعر',
            'city': 'المدينة',
            'district': 'الحي',
            'phone': 'رقم الجوال',
            'description': 'التفاصيل',
            'image': 'الصورة الرئيسية',
            'license_number': 'رقم الترخيص',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'area': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'أدخل المساحة بالمتر المربع'}),
        }



# 👤 نموذج تسجيل مستخدم جديد
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    # ✅ حقل جديد لتحديد نوع المستخدم
    USER_TYPES = [
        ('agent', 'وسيط'),
        ('admin', 'آدمن'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        label='نوع المستخدم',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'city', 'district', 'license_number', 'password1', 'password2']
        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الجوال',
            'city': 'المدينة',
            'district': 'الحي',
            'license_number': 'رقم الرخصة',
            'password1': 'كلمة المرور',
            'password2': 'تأكيد كلمة المرور',
        }

    def save(self, commit=True):
        # 🧠 أولًا ننشئ المستخدم بدون حفظه في قاعدة البيانات
        user = super().save(commit=False)

        # ✅ نقرأ نوع المستخدم اللي اختاره في الفورم
        user_type = self.cleaned_data.get('user_type')

        # ⚙️ نحدد الصلاحيات بناءً على نوعه
        if user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False

        # ✅ حفظ المستخدم النهائي
        if commit:
            user.save()

        return user

from django import forms
from .models import CustomUser

class CustomUserUpdateForm(forms.ModelForm):
    USER_TYPES = [
        ('agent', 'وسيط'),
        ('admin', 'آدمن'),
    ]

    user_type = forms.ChoiceField(
        choices=USER_TYPES,
        label='نوع المستخدم',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'phone', 'city', 'district', 'license_number']

        labels = {
            'username': 'اسم المستخدم',
            'email': 'البريد الإلكتروني',
            'phone': 'رقم الجوال',
            'city': 'المدينة',
            'district': 'الحي',
            'license_number': 'رقم الرخصة',
        }

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

        # ✅ تعبئة user_type من الصلاحيات الفعلية
        if self.instance:
            if self.instance.is_superuser:
                self.fields['user_type'].initial = 'admin'
            else:
                self.fields['user_type'].initial = 'agent'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(id=self.user_id).exists():
            raise forms.ValidationError("اسم المستخدم مستخدم من قبل.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')

        if user_type == 'admin':
            user.is_staff = True
            user.is_superuser = True
        else:
            user.is_staff = False
            user.is_superuser = False

        if commit:
            user.save()
        return user


# 🔐 نموذج تسجيل الدخول
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")
