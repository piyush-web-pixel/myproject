from django.db import models

class MigrantWorker(models.Model):
    name = models.CharField(max_length=100)
    aadhaar_id = models.CharField(max_length=12, unique=True)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    state_of_origin = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    qr_code = models.ImageField(upload_to="qrcodes/", blank=True, null=True)
    added_by = models.ForeignKey(
        "DoctorPanel", on_delete=models.SET_NULL, null=True, blank=True, related_name="workers"
    )

    def __str__(self):
        return f"{self.name} ({self.aadhaar_id})"

class HealthRecord(models.Model):
    worker = models.ForeignKey(MigrantWorker, on_delete=models.CASCADE, related_name="health_records")
    date = models.DateField()
    illness = models.CharField(max_length=200)
    treatment = models.TextField()
    doctor_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.worker.name} - {self.date}"




class LabReport(models.Model):
    worker = models.ForeignKey(MigrantWorker, on_delete=models.CASCADE, related_name="lab_reports")
    report_file = models.FileField(upload_to="lab_reports/")
    original_text = models.TextField(blank=True, null=True)
    summary_en = models.TextField(blank=True, null=True)
    summary_hi = models.TextField(blank=True, null=True)
    summary_ml = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lab Report - {self.worker.name} ({self.uploaded_at.date()})"





from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
















# Create your models here.


class Doctor(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)  # Specialist field
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.department})"
    
    

class Appointment(models.Model):
    patient_name = models.CharField(max_length=100)
    patient_phone = models.CharField(max_length=15)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    cost = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        # Automatically set cost from doctor's consultation fee
        self.cost = self.doctor.consultation_fee
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient_name} with {self.doctor.name} on {self.date}"
    



class Booking(models.Model):
    worker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")  
    doctor = models.ForeignKey("DoctorPanel", on_delete=models.CASCADE, related_name="bookings")
    date = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")],
        default="Pending"
    )
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking: {self.worker.username} with Dr. {self.doctor.user.username} - {self.status}"














from django.shortcuts import render
from .models import Doctor  # सही import

def home(request):
    doctors = Doctor.objects.all()
    return render(request, 'home.html', {'doctors': doctors})





from django.db import models
from django.utils import timezone

class DiseaseAlert(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    date_issued = models.DateTimeField(default=timezone.now)
    severity = models.CharField(max_length=50, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    




# in models.py
from django.db import models
from django.contrib.auth.models import User

class DoctorPanel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # link with login user
    specialization = models.CharField(max_length=100, blank=True, null=True)
    hospital = models.CharField(max_length=150, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"Dr. {self.user.username} ({self.specialization})"
