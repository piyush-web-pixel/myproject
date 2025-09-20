from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    
    path("landing/",views.landing, name='landing'),
#   
    path("workers/", views.worker_list, name="worker_list"),
    path("add-worker/", views.add_worker, name="add_worker"),
    path("worker/<int:pk>/", views.worker_detail, name="worker_detail"),
    path("worker/<int:worker_id>/add-record/", views.add_health_record, name="add_health_record"),
    path("worker/<int:pk>/delete/", views.delete_worker, name="delete_worker"),

    # path("summarize_notes/", views.summarize_notes, name="summarize_notes"),
    path("summarize_notes/<int:record_id>/", views.summarize_notes, name="summarize_notes"),
    # path("summarize/", views.summarize, name="worker_list"),
    # path("summarize/<int:record_id>/", views.summarize_notes, name="summarize_notes"),
    # path("summarize-document/", views.summarize_document, name="summarize_document"),
    path("lab-analyzer/", views.lab_report_analyzer, name="lab_report_analyzer"),

    path("upload-lab-report/", views.upload_lab_report, name="upload_lab_report"),
    
    path("lab-report/<int:report_id>/", views.view_lab_report, name="view_lab_report"),
    path("lab-reports/", views.lab_report_list, name="lab_report_list"),


    # path("nearby-doctors/", views.search_nearby_doctors, name="search_nearby_doctors"),

    path("nearby-doctors/", views.nearby_doctors, name="nearby_doctors"),

    path("nearby-healthcare/", views.nearby_healthcare, name="nearby_healthcare"),

    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("accounts/login/", views.login_view),
    # path('profile/', views.profile, name='profile'),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.update_profile, name="update_profile"),
    path("book_appointment/",views.book_appointment, name='book_appointment'),
    # path("landing_copy/",views.landing_copy, name='landing_copy'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('disease_alerts/',views.disease_alerts,name="disease_alerts"),
    # path("doctor_dashboard/", views.doctor_dashboard, name="doctor_dashboard"),
    # path("doctor/worker/<int:worker_id>/edit/", views.edit_health_record, name="edit_health_record"),
    path("doctor-panel/", views.doctor_panel_dashboard, name="doctor_panel_dashboard"),
    path("doctor-panel/worker/<int:worker_id>/edit/", views.doctor_edit_worker, name="doctor_edit_worker"),
    path("doctor_register/", views.doctor_register, name="doctor_register"),
    path("doctor/home/", views.doctor_home, name="doctor_home"),  # doctor dashboard
    path("doctor/login/", views.doctor_login, name="doctor_login"),
    path("booking/book/", views.book_booking, name="book_booking"),
    path("doctor/bookings/", views.doctor_bookings, name="doctor_bookings"),
    path("booking/<int:booking_id>/<str:status>/", views.update_booking_status, name="update_booking_status"),
    # path('predict/', views.predict_disease, name='predict_disease'),
    path("search-abha/", views.search_abha, name="search_abha"),
    path("chatbot/", views.chatbot_page, name="chatbot_page"),   # Page UI
    path("chatbot/api/", views.chatbot_api, name="chatbot_api"), # AJAX API


]
