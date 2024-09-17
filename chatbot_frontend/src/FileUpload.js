import React, { useState } from 'react';
import axios from 'axios';

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
    })
    .catch(error => {
      console.error('Error uploading file', error);
      if (error.response) {
        console.error('Error response data:', error.response.data);
      }
    });
  };

  return (
    <div>
      <input type="file" onChange={onFileChange} />
      <button onClick={onFileUpload}>
        Upload!
      </button>
    </div>
  );
}

export default FileUpload;
