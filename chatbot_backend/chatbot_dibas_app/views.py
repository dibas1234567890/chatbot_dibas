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

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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
        print(f"Saving FAISS index to: {index_dir}")
        os.makedirs(index_dir, exist_ok=True)

        try:
            vector_store.save_local(index_dir)
        except Exception as save_exception:
            print(f"Error saving FAISS index: {str(save_exception)}")
            return False

        index_file_path = os.path.join(index_dir, "index.faiss")
        if os.path.exists(index_file_path):
            print(f"Index file '{index_file_path}' created successfully.")
            return True
        else:
            print(f"Failed to create the index file at '{index_file_path}'.")
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

class QuestionAnswerView(APIView):
    def post(self, request):
        user_question = request.data.get('question')
        if not user_question:
            return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            index_dir = "faiss_index"
            
            index_file_path = os.path.join(index_dir, "index.faiss")
            if not os.path.exists(index_file_path):
                print(f"FAISS index file not found at '{index_file_path}'.")
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
            print(f"Error during question answering: {str(e)}")
            return Response({'error': 'An error occurred while processing your request.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
