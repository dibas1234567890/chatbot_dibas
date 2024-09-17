import React from 'react';
import FileUpload from './FileUpload';
import ChatBox from './ChatBox';
import './App.css';
import logo from './logo.svg';

function App() {
  return (
    <div className="App">
      
      <main>
        <FileUpload />
        <ChatBox />
      </main>
    </div>
  );
}

export default App;
