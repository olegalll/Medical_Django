from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Consultation
from .serializers import ConsultationSerializer
from .permissions import CanWorkWithConsultation


class ConsultationViewSet(viewsets.ModelViewSet):
    """CRUD для консультаций"""
    serializer_class = ConsultationSerializer
    permission_classes = [CanWorkWithConsultation]

    def get_queryset(self):
        queryset = Consultation.objects.select_related('doctor', 'patient', 'clinic')
        if self.request.user.role == 'patient':
            queryset = queryset.filter(patient__user=self.request.user)
        if self.request.user.role == 'doctor':
            queryset = queryset.filter(doctor__user=self.request.user)

        status_filter = self.request.query_params.get('status')
        doctor_name = self.request.query_params.get('doctor_name')
        patient_name = self.request.query_params.get('patient_name')
        order_by = self.request.query_params.get('ordering', '-created_at')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if doctor_name:
            queryset = queryset.filter(doctor__full_name__icontains=doctor_name)

        if patient_name:
            queryset = queryset.filter(patient__full_name__icontains=patient_name)
        queryset = queryset.order_by(order_by)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        for obj in queryset:
            self.check_object_permissions(request, obj)
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        try:
            consultation = Consultation.objects.get(pk=pk)
        except Consultation.DoesNotExist:
            return Response({"error": "Консультация не найдена"}, status=status.HTTP_404_NOT_FOUND)
        self.check_object_permissions(request, consultation)

        new_status = request.data.get('status')
        if new_status not in dict(Consultation.STATUS_CHOICES).keys():
            return Response({"error": "Неверный статус"}, status=status.HTTP_400_BAD_REQUEST)

        consultation.status = new_status
        consultation.save()
        return Response({"info": "Статус успешно обновлен"})
