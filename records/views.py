from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.db.models import Count
from .models import MigrantWorker, HealthRecord
from .forms import WorkerForm, HealthRecordForm
import qrcode, os
from django.http import FileResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Doctor, Appointment,DoctorPanel,Booking
from .forms import DoctorRegisterForm,BookingForm
from .models import LabReport
from transformers import pipeline
from django.shortcuts import render, get_object_or_404
from .models import HealthRecord
import pickle
import numpy as np
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
import PyPDF2
from transformers import pipeline
from .models import LabReport, MigrantWorker
from .forms import LabReportForm


def home(request):
    # workers = MigrantWorker.objects.count()
    # records = HealthRecord.objects.count()
    # recent = HealthRecord.objects.order_by("-date")[:5]
    # doctors = Doctor.objects.all().order_by('department')
    # departments = set(doctors.values_list('department', flat=True))
    
    return render(request, "home.html")
@login_required
def worker_list(request):
    workers = MigrantWorker.objects.all()
    return render(request, "worker_list.html", {"workers": workers})

@login_required
def dashboard(request):
    workers = MigrantWorker.objects.count()
    records = HealthRecord.objects.count()
    recent = HealthRecord.objects.order_by("-date")[:5]
    doctors = Doctor.objects.all().order_by('department')
    departments = set(doctors.values_list('department', flat=True))
    
    return render(request, "dashboard.html", {
        "workers": workers, "records": records, "recent": recent,'doctors': doctors, 'departments': departments
    })





def landing(request):
    return render(request,"landing.html")




@login_required
def add_worker(request):
    if request.method == "POST":
        form = WorkerForm(request.POST)
        if form.is_valid():
            worker = form.save()
            # Generate QR Code
            qr_img = qrcode.make(f"https://2cxm7jdq-8000.inc1.devtunnels.ms/worker/{worker.id}/")

            qr_path = os.path.join(settings.MEDIA_ROOT, f"qrcodes/worker_{worker.id}.png")
            os.makedirs(os.path.dirname(qr_path), exist_ok=True)
            qr_img.save(qr_path)
            worker.qr_code = f"qrcodes/worker_{worker.id}.png"
            worker.save()
            return redirect("worker_list")
    else:
        form = WorkerForm()
    return render(request, "add_worker.html", {"form": form})

def worker_detail(request, pk):
    worker = get_object_or_404(MigrantWorker, pk=pk)
    records = worker.health_records.all()
    return render(request, "worker_detail.html", {
        "worker": worker, "records": records
    })






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import MigrantWorker

def delete_worker(request, pk):
    worker = get_object_or_404(MigrantWorker, pk=pk)

    if request.method == "POST":
        worker.delete()
        messages.success(request, "Worker deleted successfully!")
        return redirect("worker_list")   # back to list after delete

    return render(request, "delete_worker.html", {"worker": worker})

















def add_health_record(request, worker_id):
    worker = get_object_or_404(MigrantWorker, pk=worker_id)
    if request.method == "POST":
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.worker = worker
            record.save()
            return redirect("worker_detail", pk=worker.id)
    else:
        form = HealthRecordForm()
    return render(request, "add_health_record.html", {
        "form": form, "worker": worker
    })




summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_notes(request, record_id):
    record = get_object_or_404(HealthRecord, id=record_id)
    summary = summarizer(
        record.doctor_notes,
        max_length=50,
        min_length=10,
        do_sample=False
    )[0]['summary_text']

    return render(request, "summarize_notes.html", {
        "record": record,
        "summary": summary   # ✅ use "summary" instead of "summarize_notes"
    })



 


from django.shortcuts import render
from django.core.files.storage import default_storage
import PyPDF2
from transformers import pipeline

# Summarizer (English base)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# Translation pipelines
translator_hi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")   # English → Hindi
translator_ml = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ml")   # English → Malayalam

def lab_report_analyzer(request):
    summary_en = None
    summary_hi = None
    summary_ml = None
    original_text = None

    if request.method == "POST" and request.FILES.get("report"):
        uploaded_file = request.FILES["report"]
        file_path = default_storage.save(uploaded_file.name, uploaded_file)

        # Extract text from PDF or txt
        if uploaded_file.name.endswith(".pdf"):
            with open(file_path, "rb") as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                original_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        else:  # text file
            with open(file_path, "r", encoding="utf-8") as f:
                original_text = f.read()

        if original_text.strip():
            try:
                # Step 1: Summarize in English
                summary_en = summarizer(original_text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]

                # Step 2: Translate to Hindi
                summary_hi = translator_hi(summary_en)[0]["translation_text"]

                # Step 3: Translate to Malayalam (Kerala language)
                summary_ml = translator_ml(summary_en)[0]["translation_text"]

            except Exception as e:
                summary_en = f"Error analyzing report: {e}"

    return render(request, "lab_report_analyzer.html", {
        "original_text": original_text,
        "summary_en": summary_en,
        "summary_hi": summary_hi,
        "summary_ml": summary_ml,
    })






# Load AI models
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
translator_hi = pipeline("translation", model="Helsinki-NLP/opus-mt-en-hi")
translator_ml = pipeline("translation", model="Helsinki-NLP/opus-mt-en-ml")


def upload_lab_report(request):
    if request.method == "POST":
        form = LabReportForm(request.POST, request.FILES)
        if form.is_valid():
            lab_report = form.save(commit=False)
            uploaded_file = lab_report.report_file

            file_path = default_storage.save(uploaded_file.name, uploaded_file)

            # Extract text
            if uploaded_file.name.endswith(".pdf"):
                with open(file_path, "rb") as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()

            lab_report.original_text = text

            # Summarize
            if text.strip():
                try:
                    summary_en = summarizer(text, max_length=100, min_length=20, do_sample=False)[0]["summary_text"]
                    lab_report.summary_en = summary_en
                    lab_report.summary_hi = translator_hi(summary_en)[0]["translation_text"]
                    lab_report.summary_ml = translator_ml(summary_en)[0]["translation_text"]
                except Exception as e:
                    lab_report.summary_en = f"Error: {e}"

            lab_report.save()

            # ✅ Redirect to the list page instead of a single report
            return redirect("lab_report_list")

    else:
        form = LabReportForm()

    return render(request, "upload_lab_report.html", {"form": form})


def view_lab_report(request, report_id):
    report = get_object_or_404(LabReport, id=report_id)

    # Agar query param ?download=true hai to file download karao
    if request.GET.get("download") == "true":
        file_path = report.report_file.path
        if os.path.exists(file_path):
            return FileResponse(open(file_path, "rb"), as_attachment=True, filename=os.path.basename(file_path))

    return render(request, "view_lab_report.html", {"report": report})




def lab_report_list(request):
    reports = LabReport.objects.all().select_related("worker").order_by("-uploaded_at")
    return render(request, "lab_report_list.html", {"reports": reports})





def nearby_doctors(request):
    doctors = []
    if request.method == "POST":
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        api_key = settings.GOOGLE_MAPS_API_KEY

        url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "radius": 5000,  # 5km range
            "type": "doctor",
            "key": api_key,
        }

        response = requests.get(url, params=params).json()

        for place in response.get("results", []):
            doctors.append({
                "name": place.get("name"),
                "address": place.get("vicinity"),
                "rating": place.get("rating"),
            })

    return render(request, "nearby_doctors.html", {"doctors": doctors})








def nearby_healthcare(request):
    results = []
    error_message = None

    if request.method == "POST":
        lat = request.POST.get("lat")
        lng = request.POST.get("lng")
        api_key = getattr(settings, "GOOGLE_MAPS_API_KEY", None)

        if not api_key:
            error_message = "Google Maps API key is missing in settings.py"
        elif lat and lng:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

            # Search for both doctors and hospitals
            for place_type in ["doctor", "hospital"]:
                params = {
                    "location": f"{lat},{lng}",
                    "radius": 5000,  # 5km range
                    "type": place_type,
                    "key": api_key,
                }

                response = requests.get(url, params=params).json()

                # Debugging: check raw API response
                print(f"{place_type} API Response:", response)

                if response.get("status") == "OK":
                    for place in response.get("results", []):
                        results.append({
                            "type": place_type.capitalize(),
                            "name": place.get("name"),
                            "address": place.get("vicinity"),
                            "rating": place.get("rating"),
                        })
                else:
                    error_message = f"Google API Error ({place_type}): {response.get('status')}"

    return render(request, "nearby_healthcare.html", {
        "results": results,
        "error": error_message
    })






from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")  # after register go to login
    else:
        form = RegisterForm()
    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")  # after login go to home
    else:
        form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")





# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render, redirect
# from .forms import UserUpdateForm, ProfileUpdateForm

# @login_required
# def profile(request):
#     if request.method == "POST":
#         u_form = UserUpdateForm(request.POST, instance=request.user)
#         p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)

#         if u_form.is_valid() and p_form.is_valid():
#             u_form.save()
#             p_form.save()
#             return redirect('profile')
#     else:
#         u_form = UserUpdateForm(instance=request.user)
#         p_form = ProfileUpdateForm(instance=request.user.profile)

#     context = {
#         'u_form': u_form,
#         'p_form': p_form,
#     }
#     return render(request, 'profile.html', context)







from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import UserUpdateForm, ProfileUpdateForm

@login_required
def profile(request):
    """Show profile details only"""
    return render(request, "profile.html", {"user": request.user, "profile": request.user.profile})

@login_required
def update_profile(request):
    """Update profile + user details"""
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {"u_form": u_form, "p_form": p_form}
    return render(request, "update_profile.html", context)






from django.shortcuts import render, get_object_or_404
from .models import LabReport

def lab_report_list(request):
    reports = LabReport.objects.order_by("-uploaded_at")
    return render(request, "lab_report_list.html", {"reports": reports})

def view_lab_report(request, report_id):
    report = get_object_or_404(LabReport, id=report_id)
    return render(request, "view_lab_report.html", {"report": report})





def book_appointment(request):
    doctors = Doctor.objects.all().order_by('department')
    if request.method == 'POST':
        patient_name = request.POST['name']
        patient_phone = request.POST['phone']
        doctor_id = request.POST['doctor']
        date = request.POST['date']
        time = request.POST['time']
        description = request.POST['description']

        doctor = Doctor.objects.get(id=doctor_id)
        Appointment.objects.create(
            patient_name=patient_name,
            patient_phone=patient_phone,
            doctor=doctor,
            date=date,
            time=time,
            description=description
        )
        messages.success(request, f'Appointment booked! Consultation fee is ₹{doctor.consultation_fee}')
        return redirect('home')

    return render(request, 'book_appointment.html', {'doctors': doctors})



import requests
from .models import DiseaseAlert

def fetch_disease_alerts():
    url = "https://example-ngo.org/api/disease-alerts"
    response = requests.get(url).json()

    for item in response["alerts"]:
        DiseaseAlert.objects.update_or_create(
            title=item["title"],
            defaults={
                "description": item["description"],
                "location": item["location"],
                "source": "NGO API",
                "severity": item.get("severity", "medium"),
            }
        )



import requests
import feedparser
from django.shortcuts import render

def disease_alerts(request):
    feed_url = "https://www.who.int/feeds/entity/csr/don/en/rss.xml"
    
    headers = {"User-Agent": "Mozilla/5.0"}  # WHO blocks requests without UA
    response = requests.get(feed_url, headers=headers, timeout=10)
    
    data = feedparser.parse(response.text)
    alerts = []

    for entry in data.entries[:5]:  # get top 5 alerts
        alerts.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", "No date"),
            "summary": entry.get("summary", "")
        })

    return render(request, "disease_alerts.html", {"alerts": alerts})







# # @login_required
# def doctor_dashboard(request):
#     # Ensure only doctors can access
#     doctor = get_object_or_404(Doctor, user=request.user)
#     workers = MigrantWorker.objects.all()
#     return render(request, "doctor_dashboard.html", {"workers": workers, "doctor": doctor})

# # @login_required
# def edit_health_record(request, worker_id):
#     doctor = get_object_or_404(Doctor, user=request.user)
#     worker = get_object_or_404(MigrantWorker, id=worker_id)

#     if request.method == "POST":
#         form = HealthRecordForm(request.POST)
#         if form.is_valid():
#             record = form.save(commit=False)
#             record.worker = worker
#             record.doctor = doctor
#             record.save()
#             return redirect("doctor_dashboard")
#     else:
#         form = HealthRecordForm()

#     return render(request, "edit_health_record.html", {"form": form, "worker": worker})



# @login_required
def doctor_panel_dashboard(request):
    try:
        doctor = DoctorPanel.objects.get(user=request.user)
    except DoctorPanel.DoesNotExist:
        messages.error(request, "You do not have access to the Doctor Panel.")
        return redirect("home")

    workers = doctor.workers.all()

    return render(request, "doctor_panel_dashboard.html", {
        "doctor": doctor,
        "workers": workers
    })








# @login_required
def doctor_edit_worker(request, worker_id):
    worker = get_object_or_404(MigrantWorker, id=worker_id)

    # Ensure doctor can only edit their own workers
    doctor = DoctorPanel.objects.get(user=request.user)
    if worker.added_by != doctor:
        messages.error(request, "You are not authorized to edit this worker.")
        return redirect("doctor_panel_dashboard")

    if request.method == "POST":
        form = HealthRecordForm(request.POST, instance=worker)
        if form.is_valid():
            form.save()
            messages.success(request, "Worker updated successfully!")
            return redirect("doctor_panel_dashboard")
    else:
        form = HealthRecordForm(instance=worker)

    return render(request, "doctor_edit_worker.html", {"form": form, "worker": worker})






# views.py


def doctor_register(request):
    if request.method == "POST":
        form = DoctorRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Doctor account created successfully! You can now log in.")
            return redirect("doctor_login")  # redirect to normal login
    else:
        form = DoctorRegisterForm()
    return render(request, "doctor_register.html", {"form": form})




# Doctor Login View
def doctor_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            try:
                doctor = DoctorPanel.objects.get(user=user)  # ensure this user is a doctor
                login(request, user)
                return redirect("doctor_home")  # redirect to doctor dashboard
            except DoctorPanel.DoesNotExist:
                messages.error(request, "You are not registered as a Doctor.")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "doctor_login.html")


# Doctor Home/Dashboard
@login_required
def doctor_home(request):
    doctor = DoctorPanel.objects.get(user=request.user)
    return render(request, "doctor_home.html", {"doctor": doctor})









# Worker books booking

@login_required
def book_booking(request):
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.worker = request.user
            booking.save()

            # ✅ Add success message
            messages.success(request, "Appointment booked successfully ✅")

            # Stay on the same page (no redirect to profile)
            return render(request, "book_booking.html", {"form": BookingForm()})
    else:
        form = BookingForm()

    return render(request, "book_booking.html", {"form": form})

# Doctor sees all bookings
@login_required
def doctor_bookings(request):
    doctor = get_object_or_404(DoctorPanel, user=request.user)
    bookings = doctor.bookings.all()
    return render(request, "doctor_bookings.html", {"bookings": bookings})

# Doctor updates status
@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id, doctor__user=request.user)
    booking.status = status
    booking.save()
    return redirect("doctor_bookings")






import requests
from django.conf import settings
from django.shortcuts import render,HttpResponse

def search_abha(request):
    profile = None
    error = None

    if request.method == "POST":
        abha_id = request.POST.get("abha_id").strip()

        # Sandbox API endpoint (ABHA search)
        url = f"{settings.ABDM_BASE_URL}/patients/searchByHealthId"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "client_id": settings.ABDM_CLIENT_ID,
            "client_secret": settings.ABDM_CLIENT_SECRET
        }

        payload = {
            "healthId": abha_id
        }

        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=20)
            if resp.status_code == 200:
                profile = resp.json()
            else:
                error = f"Failed! Status {resp.status_code}: {resp.text}"
        except Exception as e:
            error = str(e)

    return render(request, "search_abha.html", {"profile": profile, "error": error})




import requests
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Renders chatbot page
def chatbot_page(request):
    return render(request, "chatbot.html")

import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_msg = data.get("message", "")

        try:
            response = requests.post(
                "https://vortexislive92.app.n8n.cloud/webhook/hack",
                json={"message": user_msg},
                timeout=10
            )

            if response.status_code == 200:
                try:
                    data = response.json()
                    print("🔹 Raw n8n response:", data)  # 👈 check in Django console

                    if isinstance(data, list) and len(data) > 0:
                        item = data[0]
                        n8n_reply = item.get("reply") or item.get("message") or str(item)
                    if isinstance(data, dict):
                        n8n_reply = data.get("reply") or data.get("message") or data.get("myField") or str(data)

                    else:
                        n8n_reply = str(data)

                except Exception:
                    n8n_reply = response.text
            else:
                n8n_reply = f"Error {response.status_code} from n8n"

        except Exception as e:
            n8n_reply = f"❌ Connection error: {str(e)}"

        return JsonResponse({"reply": n8n_reply})

