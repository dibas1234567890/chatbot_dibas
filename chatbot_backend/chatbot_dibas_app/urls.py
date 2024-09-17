from django.urls import path

from chatbot_dibas_app.views import UploadPDFView,QuestionAnswerView

urlpatterns = [
    path('upload_pdf/', UploadPDFView.as_view(), name='upload_pdf'),
    path('question/', QuestionAnswerView.as_view(), name='question'),
]