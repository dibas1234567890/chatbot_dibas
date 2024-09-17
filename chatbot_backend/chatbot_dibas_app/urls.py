from django.urls import path

from chatbot_dibas_app import views

urlpatterns = [
    path('upload_pdf/', views.UploadPDFView.as_view(), name='upload_pdf'),
    path('question/', views.QuestionAnswerView.as_view(), name='question'),
]