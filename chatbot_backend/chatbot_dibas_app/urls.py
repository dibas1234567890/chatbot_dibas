from django.urls import path

from chatbot_dibas_app.views import UploadPDFView,QuestionAnswerView, AppointmentView

urlpatterns = [
    path('upload_pdf/', UploadPDFView.as_view(), name='upload_pdf'),
    path('question/', QuestionAnswerView.as_view(), name='question'),
    path('api/appointment/', AppointmentView.as_view(), name='appointment'),

]