from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
import os
from django.core.files.storage import default_storage
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter 
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai 
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI 
from langchain.chains.question_answering import load_qa_chain 
from langchain.prompts import PromptTemplate 
from dotenv import load_dotenv

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def process_pdf(pdf_files):
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
    vector_store.save_local("faiss_index")

    return True

class UploadPDFView(APIView):
    def post(self, request):
        pdf_files = request.FILES.getlist('pdfs')
        if not pdf_files:
            return Response({'error': 'No PDF files provided'}, status=status.HTTP_400_BAD_REQUEST)

        success = process_pdf(pdf_files)
        if success:
            return Response({"message": "PDF processed and embeddings saved successfully."}, status=status.HTTP_200_OK)
        return Response({"error": "Failed to process PDF."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class QuestionAnswerView(APIView):
    def post(self, request):
        user_question = request.data.get('question')
        if not user_question:
            return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        vector_store = FAISS.load_local("faiss_index", embeddings)

        docs = vector_store.similarity_search(user_question)

        prompt_template = """
        Answer the question as detailed as possible from the provided context. If the answer is not in the provided context, say: "answer is not available in the context". 
        Context:\n{context}\n
        Question: \n{question}\n
        Answer: 
        """
        model = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.3)
        prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
        chain = load_qa_chain(model, chain_type="stuff")

        response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

        return Response({"answer": response["output_text"]}, status=status.HTTP_200_OK)
