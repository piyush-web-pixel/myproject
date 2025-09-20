from django.contrib import admin
from .models import Doctor,Appointment

# Register your models here.


# Doctor model ko admin mein register karna
admin.site.register(Doctor)

# Appointment model ko admin mein register karna
admin.site.register(Appointment)