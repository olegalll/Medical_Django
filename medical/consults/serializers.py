from rest_framework import serializers
from .models import Consultation, Doctor, Patient, Clinic


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = '__all__'


class ConsultationSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    clinic = ClinicSerializer(read_only=True)

    doctor_id = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all(), write_only=True, source='doctor')
    patient_id = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), write_only=True, source='patient')
    clinic_id = serializers.PrimaryKeyRelatedField(queryset=Clinic.objects.all(), write_only=True, source='clinic')

    class Meta:
        model = Consultation
        fields = [
            'id',
            'created_at',
            'start_time',
            'end_time',
            'status',
            'doctor',
            'patient',
            'clinic',
            'doctor_id',
            'patient_id',
            'clinic_id',
        ]
        read_only_fields = ['id', 'created_at', 'doctor', 'patient', 'clinic']
