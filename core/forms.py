from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, CustomerRequest, Property


# ✅ ويدجت مخصص يدعم رفع ملفات متعددة
class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# 📷 نموذج طلب عميل (بدون الصور داخل الـ form)
from django import forms
from .models import CustomerRequest

class CustomerRequestForm(forms.ModelForm):
    class Meta:
        model = CustomerRequest
        fields = [
            'full_name',
            'phone',
            'city',
            'district',
            'area_required',
            'property_type',
            'request_type',
            'details',
            'max_price',
            'payment_method',
            'license_number',
        ]
        labels = {
            'full_name': 'الاسم الكامل',
            'phone': 'رقم الجوال',
            'city': 'المدينة',
            'district': 'الحي',
            'area_required': 'المساحة المطلوبة (م²)',
            'property_type': 'نوع العقار',
            'request_type': 'نوع الطلب',
            'details': 'تفاصيل إضافية',
            'max_price': 'الحد الأعلى للسعر (ريال)',
            'payment_method': 'طريقة الدفع',
            'license_number': 'رقم الرخصة (اختياري)',
        }
        widgets = {
            'details': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'مثلاً: قريب من المدارس والخدمات...'
            }),
            'area_required': forms.NumberInput(attrs={
                'placeholder': 'مثلاً: 250'
            }),
            'max_price': forms.NumberInput(attrs={
                'placeholder': 'مثلاً: 500000'
            }),
        }


# 🏠 نموذج إضافة عقار
class PropertyForm(forms.ModelForm):
    images = forms.FileField(
        widget=MultiFileInput(attrs={'multiple': True}),
        required=False,
        label='صور إضافية'
    )

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
            'area': forms.NumberInput(attrs={'class': 'form-control'}),
        }


# 👤 نموذج تسجيل مستخدم جديد
class CustomUserCreationForm(UserCreationForm):
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
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        user.is_staff = user_type == 'admin'
        user.is_superuser = user_type == 'admin'
        if commit:
            user.save()
        return user


# 👤 تعديل بيانات المستخدم
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
        if self.instance:
            self.fields['user_type'].initial = 'admin' if self.instance.is_superuser else 'agent'

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exclude(id=self.user_id).exists():
            raise forms.ValidationError("اسم المستخدم مستخدم من قبل.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data.get('user_type')
        user.is_staff = user_type == 'admin'
        user.is_superuser = user_type == 'admin'
        if commit:
            user.save()
        return user


# 🔐 نموذج تسجيل الدخول
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(label="اسم المستخدم")
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")
