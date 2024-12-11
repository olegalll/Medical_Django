from rest_framework.permissions import BasePermission
from consults.models import Consultation


class BaseRole(BasePermission):

    def __init__(self, role):
        self.role = role

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role == self.role


class IsAdmin(BaseRole):
    def __init__(self):
        super().__init__('admin')


class IsDoctor(BaseRole):
    def __init__(self):
        super().__init__('doctor')


class IsPatient(BaseRole):
    def __init__(self):
        super().__init__('patient')


class CanWorkWithConsultation(BasePermission):
    """Проверка прав доступа на создание, обновление и удаление консультаций
    - Администратор может изменять любые консультации
    - Врачи могут изменять только свои консультации
    Проверка прав доступа на просмотр консультаций
    - Администратор может просматривать все
    - Врачи и пациенты могут просматривать только свои консультации
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.user.role == 'admin':
            return True

        if view.action == 'change_status':
            if request.user.role == 'doctor':
                return True
            return False
        elif view.action == 'create':
            if request.user.role == 'doctor':
                doctor_id = request.data.get('doctor_id')
                return doctor_id and str(doctor_id) == str(request.user.doctor.id)
        elif view.action in ['update', 'destroy', 'partial_update']:
            try:
                consultation_id = view.kwargs.get('pk')
                if not consultation_id:
                    return False
                consultation = Consultation.objects.get(pk=consultation_id)
                return request.user.role == 'doctor' and consultation.doctor.user == request.user
            except Consultation.DoesNotExist:
                return False
        elif view.action in ['list', 'retrieve']:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        """
        Проверяем, может ли пользователь получить доступ к определенному объекту.
        - Админ имеет доступ ко всем консультациям.
        - Врач и пациент имеют доступ только к своим консультациям.
        """
        if request.user.role == "admin":
            return True
        if view.action in ['create', 'update', 'destroy', 'partial_update', 'change_status']:
            if request.user.role == 'doctor' and obj.doctor.user == request.user:
                return True
        else:
            if request.user.role == "doctor":
                return obj.doctor.user == request.user
            if request.user.role == "patient":
                return obj.patient.user == request.user
        return False
