from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from cloudinary.models import CloudinaryField

# ========== المستخدم المخصص ==========
class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('agent', 'وسيط'),
        ('admin', 'أدمن'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='agent')
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.username


# ========== العقارات ==========
class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'شقة'),
        ('villa', 'فيلا'),
        ('land', 'أرض'),
        ('building', 'عمارة'),
        ('townhouse', 'تاون هاوس'),
        ('floor', 'دور'),
        ('palace', 'قصر'),
        ('chalet', 'استراحة'),
        ('farm', 'مزرعة'),
    ]

    OFFER_TYPE_CHOICES = [
        ('sale', 'بيع'),
        ('rent', 'إيجار'),
    ]

    PROPERTY_STATUS_CHOICES = [
        ('available', 'متاح'),
        ('reserved', 'محجوز'),
        ('executed', 'تم التنفيذ'),
    ]

    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    offer_type = models.CharField(max_length=10, choices=OFFER_TYPE_CHOICES)
    age = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, verbose_name="رقم الجوال", null=True, blank=True)
    description = models.TextField()
    image = CloudinaryField('image', blank=True, null=True)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    area = models.FloatField(null=True, blank=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=10,
        choices=PROPERTY_STATUS_CHOICES,
        default='available'
    )

    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reserved_properties',
        verbose_name="تم الحجز بواسطة"
    )
    reserved_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت الحجز")

    executed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='executed_properties',
        verbose_name="تم التنفيذ بواسطة"
    )
    executed_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت التنفيذ")

    def __str__(self):
        return f"{self.get_property_type_display()} - {self.city} - {self.price}"


# ✅ صور متعددة للعقار
class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return f"صورة لـ {self.property}"


# ========== الطلبات ==========
class CustomerRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('buy', 'شراء'),
        ('sell', 'بيع'),
        ('rent_out', 'تأجير'),
        ('rent', 'استئجار'),
    ]
    PROPERTY_TYPE_CHOICES = Property.PROPERTY_TYPE_CHOICES
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'كاش'),
        ('finance', 'تمويل'),
    ]
    STATUS_CHOICES = [
        ('open', 'مفتوح'),
        ('reserved', 'محجوز'),
        ('executed', 'تم التنفيذ'),
    ]

    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    area_required = models.CharField(max_length=50)
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)
    details = models.TextField()
    max_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    license_number = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    reserved_by = models.ForeignKey(
        CustomUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='reserved_requests'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    area = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_request_type_display()}"


# ✅ صور متعددة لطلبات العملاء
class CustomerRequestImage(models.Model):
    request = models.ForeignKey(CustomerRequest, related_name='images', on_delete=models.CASCADE)
    image = CloudinaryField('image', blank=True, null=True)


# تنفيذ الطلبات
class Execution(models.Model):
    customer_request = models.OneToOneField(CustomerRequest, on_delete=models.CASCADE, related_name='execution')
    agent = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'user_type': 'agent'})
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"تم التنفيذ بواسطة {self.agent.username} لطلب {self.customer_request.id}"


class SiteSettings(models.Model):
    site_name = models.CharField(max_length=100, default='مكتب خطوة وسيط')
    twitter_url = models.URLField(blank=True, null=True)
    snapchat_url = models.URLField(blank=True, null=True)
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return "إعدادات الموقع"

    class Meta:
        verbose_name = "إعدادات الموقع"
        verbose_name_plural = "إعدادات الموقع"
