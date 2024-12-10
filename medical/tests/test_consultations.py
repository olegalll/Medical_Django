import pytest
from rest_framework import status
from rest_framework.test import APIClient
from consults.models import Patient, Doctor, Consultation, Clinic, User


# Фикстуры для тестов
@pytest.fixture
def create_user(db):
    """Создание пользователя для тестов с ролью и телефоном."""
    user = User.objects.create_user(
        username="admin_user",
        email="admin_user@example.com",
        password="password",
        role='admin'
    )
    return user


@pytest.fixture
def create_doctor(db):
    """Создание тестового доктора."""
    user = User.objects.create_user(
        username="doctor_user",
        email="doctor_user@example.com",
        first_name="Doctor",
        last_name="Smith",
        password="password",
        role='doctor',
        specialization='Терапевт'
    )
    doctor = Doctor.objects.get(user=user)
    return doctor


@pytest.fixture
def create_patient(db):
    """Создание тестового пациента."""
    user = User.objects.create_user(
        username="patient_user",
        email="patient_user@example.com",
        first_name="Patient",
        last_name="Johnson",
        password="password",
        phone="+123456787",
        role='patient',
    )
    patient = Patient.objects.get(user=user)
    return patient


@pytest.fixture
def create_clinic(db):
    """Создание тестовой клиники."""
    clinic = Clinic.objects.create(name="Test Clinic", address='Test address', physical_address="Test physical address")
    return clinic


@pytest.fixture
def api_client():
    """Создание тестового клиента API."""
    return APIClient()


@pytest.fixture
def create_consultation(db, create_patient, create_doctor, create_clinic):
    """Создание тестовой консультации с корректными ссылками."""
    consultation = Consultation.objects.create(
        start_time="2023-12-11T10:00:00",
        end_time="2023-12-11T11:00:00",
        status="pending",
        patient=create_patient,
        doctor=create_doctor,
        clinic=create_clinic,
    )
    return consultation


# Тесты
def test_admin_can_see_all_consultations(api_client, create_user, create_consultation):
    """Администратор может видеть все консультации."""
    url = "/api/consultations/"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


def test_doctor_can_see_own_consultations(api_client, create_doctor, create_consultation):
    """Доктор видит только свои консультации."""
    url = "/api/consultations/"
    api_client.force_authenticate(user=create_doctor.user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    for consultation in response.data:
        assert consultation["doctor"]["id"] == create_doctor.id


def test_patient_can_see_own_consultations(api_client, create_patient, create_consultation):
    """Пациент видит только свои консультации."""
    url = "/api/consultations/"
    api_client.force_authenticate(user=create_patient.user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    for consultation in response.data:
        assert consultation["patient"]["id"] == create_patient.id


def test_filter_consultations_by_status(api_client, create_user, create_consultation):
    """Фильтрация консультаций по статусу."""
    url = "/api/consultations/?status=pending"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    for consultation in response.data:
        assert consultation["status"] == "pending"


def test_filter_consultations_by_doctor_name(api_client, create_user, create_consultation):
    """Фильтрация консультаций по имени доктора."""
    url = "/api/consultations/?doctor_name=Doctor"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    for consultation in response.data:
        assert "Doctor" in consultation["doctor"]["full_name"]


def test_filter_consultations_by_patient_name(api_client, create_user, create_consultation):
    """Фильтрация консультаций по имени пациента."""
    url = "/api/consultations/?patient_name=Patient"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    for consultation in response.data:
        assert "Patient" in consultation["patient"]["first_name"]


def test_sort_consultations_by_created_at(api_client, create_user, create_consultation):
    """Сортировка консультаций по времени создания."""
    url = "/api/consultations/?ordering=-created_at"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) > 0


def test_change_consultation_status(api_client, create_consultation):
    """Доктор может изменить статус своей консультации."""
    url = f"/api/consultations/{create_consultation.id}/change_status/"
    api_client.force_authenticate(user=create_consultation.doctor.user)

    data = {"status": "completed"}
    response = api_client.patch(url, data=data)

    assert response.status_code == status.HTTP_200_OK
    assert response.data["info"] == "Статус успешно обновлен"

    create_consultation.refresh_from_db()
    assert create_consultation.status == "completed"


def test_patient_cannot_change_consultation_status(api_client, create_consultation, create_patient):
    """Пациент не может изменить статус консультации."""
    url = f"/api/consultations/{create_consultation.id}/change_status/"
    api_client.force_authenticate(user=create_patient.user)

    data = {"status": "completed"}
    response = api_client.patch(url, data=data)

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_create_consultation(api_client, create_user, create_patient, create_doctor, create_clinic):
    """Администратор может создать новую консультацию."""
    url = "/api/consultations/"
    api_client.force_authenticate(user=create_user)

    data = {
        "start_time": "2023-12-15T10:00:00",
        "end_time": "2023-12-15T11:00:00",
        "status": "pending",
        "patient_id": create_patient.id,
        "doctor_id": create_doctor.id,
        "clinic_id": create_clinic.id,
    }
    response = api_client.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["status"] == "pending"


def test_admin_delete_consultation(api_client, create_user, create_consultation):
    """Администратор может удалить консультацию."""
    url = f"/api/consultations/{create_consultation.id}/"
    api_client.force_authenticate(user=create_user)

    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Consultation.objects.filter(id=create_consultation.id).exists()


# Проверяем ошибки
def test_update_consultation_with_invalid_data(api_client, create_consultation):
    """Ошибка при обновлении некорректными данными"""
    url = f"/api/consultations/{create_consultation.id}/"
    api_client.force_authenticate(user=create_consultation.doctor.user)

    # Некорректный статус
    data = {"status": "invalid_status"}
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid_choice" in str(response.data)


def test_unauthorized_user_cannot_update(api_client, create_consultation, create_patient):
    """Ошибка: пользователь без прав пытается обновить консультацию"""
    url = f"/api/consultations/{create_consultation.id}/"
    api_client.force_authenticate(user=create_patient.user)  # Пациент без прав на обновление

    response = api_client.patch(url, {"status": "completed"})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_consultation_not_found(api_client, create_user):
    """Ошибка при попытке доступа к несуществующей консультации"""
    url = "/api/consultations/99999/"
    api_client.force_authenticate(user=create_user)

    response = api_client.get(url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_admin_can_update_consultation(api_client, create_user, create_consultation):
    """Администратор может успешно обновить консультацию"""
    url = f"/api/consultations/{create_consultation.id}/"
    api_client.force_authenticate(user=create_user)

    data = {"status": "completed"}
    response = api_client.patch(url, data)

    assert response.status_code == status.HTTP_200_OK
    create_consultation.refresh_from_db()
    assert create_consultation.status == "completed"


def test_doctor_cannot_access_other_consultations(api_client, create_consultation):
    """Доктор не может обновлять чужие консультации."""
    user = User.objects.create_user(
        username="doctor_user2",
        email="doctor_user2@example.com",
        first_name="Doctor2",
        last_name="Smith2",
        password="password",
        role='doctor',
        specialization='Терапевт'
    )
    doctor = Doctor.objects.get(user=user)
    api_client.force_authenticate(user=doctor.user)

    url = f"/api/consultations/{create_consultation.id}/"
    response = api_client.patch(url, {"status": "completed"})

    assert response.status_code == status.HTTP_403_FORBIDDEN
