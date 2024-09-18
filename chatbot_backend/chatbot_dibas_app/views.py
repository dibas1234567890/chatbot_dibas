import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import google.generativeai as genai
import os
from dotenv import load_dotenv
from .serializers import AppointmentSerializer

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

USER_SESSIONS = {}

def process_pdf(pdf_files):
    try:
        text = ""
        for pdf_file in pdf_files:
            file_path = default_storage.save(pdf_file.name, pdf_file)
            pdf_reader = PdfReader(file_path)
            for page in pdf_reader.pages:
                text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
        chunks = text_splitter.split_text(text)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.from_texts(chunks, embeddings)

        index_dir = os.path.abspath("faiss_index")
        os.makedirs(index_dir, exist_ok=True)

        try:
            vector_store.save_local(index_dir)
        except Exception as save_exception:
            print(f"Error saving FAISS index: {str(save_exception)}")
            return False

        index_file_path = os.path.join(index_dir, "index.faiss")
        if os.path.exists(index_file_path):
            return True
        else:
            return False

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return False

class UploadPDFView(APIView):
    def post(self, request):
        pdf_files = request.FILES.getlist('pdfs')
        if not pdf_files:
            return Response({'error': 'No PDF files provided'}, status=status.HTTP_400_BAD_REQUEST)

        success = process_pdf(pdf_files)
        if success:
            return Response({"message": "PDF processed and embeddings saved successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to process PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from datetime import datetime

class QuestionAnswerView(APIView):
    def post(self, request):
        session_id = request.data.get('session_id')
        user_question = request.data.get('question')

        if not session_id or not user_question:
            return Response({'error': 'Session ID and question are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if session_id not in USER_SESSIONS:
            USER_SESSIONS[session_id] = {'name': None, 'phone': None, 'email': None, 'date': None, 'step': None}

        session_data = USER_SESSIONS[session_id]
        appointment_keywords = ["appointment", "book", "schedule"]

        if any(keyword in user_question.lower() for keyword in appointment_keywords):
            if session_data['step'] is None:
                session_data['step'] = 'ask_name'
                return Response({'answer': "Please provide your full name."})

        if session_data['step'] == 'ask_name':
            if not session_data['name']:
                session_data['name'] = user_question
                session_data['step'] = 'ask_phone'
                return Response({'answer': "Please provide your phone number."})
            else:
                session_data['step'] = 'ask_phone'

        elif session_data['step'] == 'ask_phone':
            if not session_data['phone']:
                session_data['phone'] = user_question
                session_data['step'] = 'ask_email'
                return Response({'answer': "Please provide your email address."})
            else:
                session_data['step'] = 'ask_email'

        elif session_data['step'] == 'ask_email':
            if not session_data['email']:
                session_data['email'] = user_question
                session_data['step'] = 'ask_date'
                return Response({'answer': "Please provide a date for your appointment (e.g., YYYY-MM-DD)."})
            else:
                session_data['step'] = 'ask_date'

        elif session_data['step'] == 'ask_date':
            if not session_data['date']:
                try:
                    session_data['date'] = datetime.strptime(user_question, '%Y-%m-%d').date()
                    session_data['step'] = 'complete'
                    return Response({
                        'answer': f"Thank you, {session_data['name']}! Your appointment is set for {session_data['date']}. We'll contact you at {session_data['phone']}.",
                        'contact_info': session_data
                    })
                except ValueError:
                    return Response({'answer': "The date format is incorrect. Please use YYYY-MM-DD."})
            elif 'change date' in user_question.lower():
                session_data['date'] = None  
                session_data['step'] = 'ask_date'
                return Response({'answer': "Please provide the new date for your appointment (e.g., YYYY-MM-DD)."})

        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            index_dir = "faiss_index"
            
            index_file_path = os.path.join(index_dir, "index.faiss")
            if not os.path.exists(index_file_path):
                return Response({'error': 'FAISS index not found'}, status=status.HTTP_404_NOT_FOUND)

            vector_store = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
            docs = vector_store.similarity_search(user_question)

            prompt_template = """
            Answer the question as detailed as possible from the provided context. If the answer is not in the provided context, say: "answer is not available in the context". 
            Context:\n{context}\n
            Question: \n{question}\n
            Answer: 
            """
            model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.3)
            prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
            chain = load_qa_chain(model, chain_type="stuff")

            response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

            return Response({"answer": response["output_text"]}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#For this chatbot, the serializer is optional but it converts inputs to JSON which can be integrated to other tools 
class AppointmentView(APIView):
    def post(self, request):
        serializer = AppointmentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Appointment booked successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings
import os 

