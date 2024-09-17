import React from 'react';
import FileUpload from './FileUpload';
import ChatBox from './ChatBox';
import './App.css';
import 'bootstrap/dist/css/bootstrap.min.css';  

function App() {
  return (
    <div className="App container">
      <div className='card'>
        <div className='card-header h1'> 
        Welcome to Dibas' Chatbot
        </div>
        <main className="mt-4">
          <div className="row">
            <div className="col-md-4 my-5 mx-5">
              <div className='card'>
                <div className='card-header'> Upload Files </div>
                <FileUpload />
                
              </div>
            </div>
            <div className="col-md-4 my-5 mx-5">
            <div className='card'>
              <div className='card-header'>
                Try Asking Me Some Questions
              </div>
              <div className='card-body'>
              <ChatBox />
              </div>
            </div>
            </div>
          </div>
        </main>
      </div>

      
    </div>
  );
}

export default App;
