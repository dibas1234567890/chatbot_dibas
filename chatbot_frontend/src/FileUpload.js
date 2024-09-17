import React, { useState } from 'react';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function FileUpload() {
  const [file, setFile] = useState(null);

  const getCookie = (name) => {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  };

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const onFileUpload = () => {
    if (!file) {
      console.error('No file selected for upload');
      return;
    }

    const formData = new FormData();
    formData.append('pdfs', file);

    axios.post('http://localhost:8000/api/upload_pdf/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-CSRFToken': getCookie('csrftoken'),
      },
    })
    .then(response => {
      console.log('File uploaded successfully', response.data);
      
      setFile(null);
     
      toast.success('PDF processed and embeddings saved successfully!', {
        position: "top-right",
        autoClose: 3000, 
        hideProgressBar: true,
      });
    })
    .catch(error => {
      console.error('Error uploading file', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
      }
      toast.error('Error uploading file. Please try again.', {
        position: "top-right",
        autoClose: 3000, 
        hideProgressBar: true,
      });
    });
  };

  return (
    <div className="card">
      <div className='card'>
        <div className='card-body'>
          <input type="file" onChange={onFileChange} />
          <div className='card-title'>Upload Multiple PDFs</div>
        </div>
      </div>
      <button className='btn btn-info text-white' onClick={onFileUpload}>
        Upload!
      </button>
      <ToastContainer />
    </div>
  );
}

export default FileUpload;
