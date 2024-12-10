from django.contrib import admin
from .models import User, Patient, Doctor, Clinic, Consultation

admin.site.register(User)
admin.site.register(Patient)
admin.site.register(Doctor)
admin.site.register(Clinic)
admin.site.register(Consultation)
