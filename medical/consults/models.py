from django.db import models
from django.db import transaction
from django.contrib.auth.models import AbstractUser, BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, role='patient', **extra_fields):
        if not email:
            raise ValueError('Пользователь должен иметь email')
        email = self.normalize_email(email)
        if role != "admin":
            if role == "patient" and not extra_fields.get('phone'):
                raise ValueError('Телефон обязателен и должен быть указан')
            if not (extra_fields.get('first_name') and extra_fields.get('last_name')):
                raise ValueError('Имя и фамилия должны быть указаны')
        if User.objects.filter(username=username).exists():
            raise ValueError('Имя пользователя должно быть уникальным')
        if User.objects.filter(username=email).exists():
            raise ValueError('Email должен быть уникальным')

        with transaction.atomic():
            user_fields = {key: extra_fields[key] for key in ['first_name', 'last_name'] if key in extra_fields}
            user = User.objects.create(
                username=username,
                email=email,
                role=role,
                **user_fields
            )
            user.set_password(password)
            user.save(using=self._db)

            first_name = extra_fields.get('first_name', '')
            last_name = extra_fields.get('last_name', '')
            surname = extra_fields.get('surname', '')

            if role == 'doctor':
                Doctor.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    surname=surname,
                    specialization=extra_fields.get('specialization', "Без специализации")
                )

            if role == 'patient':
                if Patient.objects.filter(user=user).exists():
                    raise ValueError('Пациент уже существует')
                Patient.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    surname=surname,
                    phone=extra_fields.get('phone')
                )

            return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        user = self.create_user(username, email, password, role='admin', **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """Пользователь с ролевой моделью"""
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('doctor', 'Доктор'),
        ('patient', 'Пациент'),
    ]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    objects = CustomUserManager()

    class Meta:
        db_table = "consults_user"

    def is_admin(self):
        return self.role == 'admin'

    def is_doctor(self):
        return self.role == 'doctor'

    def is_patient(self):
        return self.role == 'patient'


class BasePerson(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=125)
    last_name = models.CharField(max_length=125)
    surname = models.CharField(max_length=125, null=True, blank=True)
    full_name = models.CharField(max_length=255, editable=False)

    def save(self, *args, **kwargs):
        self.full_name = f"{self.first_name} {self.last_name} {self.surname or ''}".strip()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Doctor(BasePerson):
    specialization = models.CharField(max_length=255)
    clinics = models.ManyToManyField('Clinic')

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
        ]


class Patient(BasePerson):
    phone = PhoneNumberField(unique=True)

    def clean(self):
        """Проверяем, что телефон корректный и обязателен"""
        if not self.phone:
            raise ValidationError({'phone': 'Телефон обязателен и должен быть указан'})

    class Meta:
        indexes = [
            models.Index(fields=["full_name"]),
        ]


class Clinic(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    physical_address = models.TextField()


class Consultation(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Подтверждена'),
        ('pending', 'Ожидает'),
        ('started', 'Начата'),
        ('completed', 'Завершена'),
        ('paid', 'Оплачена'),
    ]
    created_at = models.DateTimeField(auto_now_add=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE)

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['start_time']),
        ]

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('Время начала должно быть меньше времени окончания')
