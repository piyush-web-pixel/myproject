from django import forms
from .models import MigrantWorker, HealthRecord,LabReport,Profile,DoctorPanel,Booking
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm




class WorkerForm(forms.ModelForm):
    class Meta:
        model = MigrantWorker
        fields = "__all__"

class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = "__all__"




class DocumentForm(forms.Form):
    document = forms.FileField()





class LabReportForm(forms.ModelForm):
    class Meta:
        model = LabReport
        fields = ["worker", "report_file"]



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'date_of_birth']






# class DoctorRegisterForm(forms.ModelForm):
#     username = forms.CharField(max_length=150)
#     email = forms.EmailField()
#     password = forms.CharField(widget=forms.PasswordInput)

#     class Meta:
#         model = DoctorPanel
#         fields = ["specialization", "hospital", "phone"]

#     def save(self, commit=True):
#         user = User.objects.create_user(
#             username=self.cleaned_data["username"],
#             email=self.cleaned_data["email"],
#             password=self.cleaned_data["password"]
#         )
#         doctor = DoctorPanel(
#             user=user,
#             specialization=self.cleaned_data["specialization"],
#             hospital=self.cleaned_data["hospital"],
#             phone=self.cleaned_data["phone"],
#         )
#         if commit:
#             doctor.save()
#         return doctor


class DoctorRegisterForm(forms.ModelForm):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            "placeholder": "Enter Username",
            "class": "form-control"
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "Enter Email Address",
            "class": "form-control"
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Enter Password",
            "class": "form-control"
        })
    )

    class Meta:
        model = DoctorPanel
        fields = ["specialization", "hospital", "phone"]
        widgets = {
            "specialization": forms.TextInput(attrs={
                "placeholder": "Enter Specialization",
                "class": "form-control"
            }),
            "hospital": forms.TextInput(attrs={
                "placeholder": "Enter Hospital Name",
                "class": "form-control"
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Enter Phone Number",
                "class": "form-control"
            }),
        }

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"]
        )
        doctor = DoctorPanel(
            user=user,
            specialization=self.cleaned_data["specialization"],
            hospital=self.cleaned_data["hospital"],
            phone=self.cleaned_data["phone"],
        )
        if commit:
            doctor.save()
        return doctor





class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ["doctor", "date", "reason"]
        widgets = {
            "date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
