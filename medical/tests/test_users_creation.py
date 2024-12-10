# import pytest
# from django.core.exceptions import ValidationError
# from django.contrib.auth import get_user_model
# from consults.models import Patient, Doctor, Consultation, Clinic
# from django.db import connection, transaction
#
# User = get_user_model()
#
# @pytest.fixture(autouse=True)
# def clear_db():
#     User.objects.all().delete()
#     Patient.objects.all().delete()
#     Doctor.objects.all().delete()
#
# @pytest.mark.django_db
# def test_create_patient_user():
#     """Тест на создание пользователя типа 'patient'."""
#     user_data = {
#         "username": "ivan_patient",
#         "email": "ivan.patient@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Иван",
#         "last_name": "Иванов",
#         "phone": "+1234567893",
#     }
#
#     # Создаем пользователя
#     user = User.objects.create_user(**user_data)
#     assert user.username == "ivan_patient"
#     assert user.email == "ivan.patient@example.com"
#     assert user.role == "patient"
#
#     # Проверяем, был ли создан профиль пациента
#     patient = Patient.objects.get(user=user)
#     assert patient.phone == "+1234567893"
#
#
# @pytest.mark.django_db
# def test_create_doctor_user():
#     """Тест на создание пользователя типа 'doctor'."""
#     user_data = {
#         "username": "doctor_john",
#         "email": "doctor.john@example.com",
#         "password": "securepassword",
#         "role": "doctor",
#         "first_name": "Джон",
#         "last_name": "Смит",
#         "specialization": "Кардиолог",
#     }
#
#     # Создаем пользователя
#     user = User.objects.create_user(**user_data)
#     assert user.username == "doctor_john"
#     assert user.role == "doctor"
#
#     # Проверяем, был ли создан профиль доктора
#     doctor = Doctor.objects.get(user=user)
#     assert doctor.specialization == "Кардиолог"
#
#
# @pytest.mark.django_db
# def test_create_superuser():
#     """Тест на создание суперпользователя."""
#     user_data = {
#         "username": "admin_user",
#         "email": "admin@example.com",
#         "password": "securepassword",
#     }
#
#     # Создаем суперпользователя
#     user = User.objects.create_superuser(**user_data)
#     assert user.is_staff is True
#     assert user.is_superuser is True
#     assert user.role == "admin"
#
#
# @pytest.mark.django_db
# def test_unique_phone_for_patient():
#     """Тест на проверку уникальности номера телефона при создании пациента."""
#     # Создаем первого пациента
#     user_data_1 = {
#         "username": "ivan_patient_1",
#         "email": "ivan1@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Иван",
#         "last_name": "Иванов",
#         "phone": "+1234567890",
#     }
#
#     user_1 = User.objects.create_user(**user_data_1)
#
#     # Пытаемся создать второго пациента с тем же номером
#     user_data_2 = {
#         "username": "ivan_patient_2",
#         "email": "ivan2@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Иван",
#         "last_name": "Петров",
#         "phone": "+1234567890",
#     }
#
#     with pytest.raises(Exception):
#         user_2 = User.objects.create_user(**user_data_2)
#
# @pytest.mark.django_db
# def test_missing_email():
#     """Тест на создание пользователя без email (должен выдать ошибку)."""
#     user_data = {
#         "username": "ivan_patient_no_email",
#         "email": "",  # Email отсутствует
#         "password": "securepassword",
#         "role": "patient",
#     }
#
#     with pytest.raises(ValueError) as err:
#         User.objects.create_user(**user_data)
#
#     assert "Пользователь должен иметь email" in str(err.value)
#
#
# @pytest.mark.django_db
# def test_missing_phone_for_patient():
#     """Тест на создание пациента без обязательного номера телефона."""
#     user_data = {
#         "username": "ivan_patient_no_phone",
#         "email": "ivan_no_phone@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Иван",
#         "last_name": "Иванов",
#         # phone отсутствует
#     }
#
#     with pytest.raises(ValueError) as err:
#         user = User.objects.create_user(**user_data)
#         patient = Patient.objects.create(user=user)
#
#         # Проверяем метод clean, который выбросит ошибку
#         patient.full_clean()
#
#     assert 'Телефон обязателен и должен быть указан' in str(err.value)
#
#
# @pytest.mark.django_db
# def test_missing_specialization_for_doctor():
#     """Тест на создание доктора без обязательного поля 'specialization'."""
#     user_data = {
#         "username": "doctor_missing_spec",
#         "email": "doctor_spec_missing@example.com",
#         "password": "securepassword",
#         "role": "doctor",
#         "first_name": "Доктор",
#         "last_name": "Без специальности",
#         # specialization отсутствует
#     }
#
#     # Создаем пользователя
#     user = User.objects.create_user(**user_data)
#
#     # Проверяем, что профиль доктора создается с дефолтным значением "Без специализации"
#     doctor = Doctor.objects.get(user=user)
#     assert doctor.specialization == "Без специализации"
#
#
# @pytest.mark.django_db
# def test_missing_required_fields_for_doctor():
#     """Тест на отсутствие нескольких обязательных полей при создании доктора."""
#     user_data = {
#         "username": "doctor_no_required_fields",
#         "email": "doctor_no_required@example.com",
#         "password": "securepassword",
#         "role": "doctor",
#     }
#
#     # Проверяем создание доктора, но без полного имени и специальности
#     with pytest.raises(ValueError):
#         user = User.objects.create_user(**user_data)
#
#
# @pytest.mark.django_db
# def test_missing_first_and_last_name():
#     """Тест на создание пользователя без имени и фамилии."""
#     user_data = {
#         "username": "ivan_no_names1",
#         "email": "ivan_noname@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "phone": "+1234567894",
#     }
#
#     with pytest.raises(ValueError) as err:
#         user = User.objects.create_user(**user_data)
#
#     assert "Имя и фамилия должны быть указаны" in str(err.value)
#
#
# @pytest.mark.django_db
# def test_unique_username():
#     """Тест на проверку уникальности имени пользователя."""
#     user_data_1 = {
#         "username": "unique_user",
#         "email": "user1@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Иван",
#         "last_name": "Иванов",
#         "phone": "+1234567890",
#     }
#
#     user_data_2 = {
#         "username": "unique_user",  # Повтор имени пользователя
#         "email": "user2@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Петр",
#         "last_name": "Петров",
#         "phone": "+1234567891",
#     }
#
#     User.objects.create_user(**user_data_1)
#
#     with pytest.raises(ValueError) as excinfo:
#         User.objects.create_user(**user_data_2)
#
#     assert "Имя пользователя должно быть уникальным" in str(excinfo.value)
#
#
# @pytest.mark.django_db
# def test_transaction_atomic_rollback():
#     """Тест на откат транзакции при ошибке."""
#     user_data = {
#         "username": "user_for_rollback",
#         "email": "rollback@example.com",
#         "password": "securepassword",
#         "role": "patient",
#         "first_name": "Ошибка",
#         "last_name": "Транзакция",
#         "phone": "+9999999999",
#     }
#
#     with pytest.raises(ValueError):
#         with transaction.atomic():
#             User.objects.create_user(**user_data)
#             # Искусственно вызываем ошибку
#             raise ValueError("Ошибка, инициирующая откат")
#
#     # Проверяем, не был создан пользователь
#     assert not User.objects.filter(email="rollback@example.com").exists()
#
#
# @pytest.mark.django_db
# def test_consultation_time_validation():
#     """Тест на валидацию времени начала и окончания консультации."""
#     doctor_user = User.objects.create_user(
#         username="doctor_consult_test",
#         email="doctor@example.com",
#         password="securepassword",
#         role="doctor",
#         first_name="Доктор",
#         last_name="Тест",
#         specialization="Терапевт",
#     )
#
#     doctor = Doctor.objects.get(user=doctor_user)
#
#     patient_user = User.objects.create_user(
#         username="patient_consult_test",
#         email="patient@example.com",
#         password="securepassword",
#         role="patient",
#         first_name="Пациент",
#         last_name="Тест",
#         phone="+1111111111",
#     )
#
#     patient = Patient.objects.get(user=patient_user)
#
#     invalid_consultation = Consultation(
#         doctor=doctor,
#         patient=patient,
#         clinic=Clinic.objects.create(name="Клиника тест", address="Test address", physical_address="Test address"),
#         start_time="2024-01-10 14:00:00",
#         end_time="2024-01-10 13:00:00",  # Некорректное время
#     )
#
#     with pytest.raises(ValidationError):
#         invalid_consultation.full_clean()
#
#
# @pytest.mark.django_db
# def test_many_to_many_clinic_assignment():
#     """Тест на привязку клиник к доктору."""
#     doctor_user = User.objects.create_user(
#         username="doctor_clinic_test",
#         email="clinicdoctor@example.com",
#         password="securepassword",
#         role="doctor",
#         first_name="Доктор",
#         last_name="Тест",
#         specialization="Терапевт",
#     )
#     doctor = Doctor.objects.get(user=doctor_user)
#
#     clinic1 = Clinic.objects.create(name="Клиника 1", address="Address 1", physical_address="Physical Address 1")
#     clinic2 = Clinic.objects.create(name="Клиника 2", address="Address 2", physical_address="Physical Address 2")
#
#     doctor.clinics.add(clinic1, clinic2)
#
#     assert clinic1 in doctor.clinics.all()
#     assert clinic2 in doctor.clinics.all()
