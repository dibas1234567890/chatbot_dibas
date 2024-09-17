import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatBox.css';

function ChatBox() {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [userInfo, setUserInfo] = useState({ name: '', phone: '', email: '' });
  const [formStep, setFormStep] = useState(null);
  const chatContainerRef = useRef(null);
  const sessionId = useRef(`session_${Math.random()}`);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    setMessages([{ type: 'bot', text: 'Hello! Ask me general questions or about uploaded PDFs. Remember, you can upload multiple PDFs!' }]);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    const newMessage = { type: 'user', text: question };
    setMessages([...messages, newMessage]);

    axios.post('http://localhost:8000/api/question/', { session_id: sessionId.current, question })
      .then(response => {
        const botMessage = { type: 'bot', text: response.data.answer };
        setMessages([...messages, newMessage, botMessage]);

        if (response.data.contact_info) {
          setUserInfo(response.data.contact_info);
        }

        setQuestion('');
      })
      .catch(error => {
        console.error('Error fetching answer', error);
      });
  };

  const handleDownload = () => {
    const blob = new Blob([messages.map(msg => `${msg.type === 'user' ? 'You' : 'Bot'}: ${msg.text}`).join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'conversation.txt';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const renderForm = () => {
    if (formStep === 'ask_name') {
      return (
        <div>
          <input
            type="text"
            value={userInfo.name}
            onChange={(e) => setUserInfo({ ...userInfo, name: e.target.value })}
            placeholder="Enter your name"
            className="form-control"
          />
          <button onClick={() => setFormStep('ask_phone')} className="btn btn-primary mt-2">Next</button>
        </div>
      );
    }

    if (formStep === 'ask_phone') {
      return (
        <div>
          <input
            type="text"
            value={userInfo.phone}
            onChange={(e) => setUserInfo({ ...userInfo, phone: e.target.value })}
            placeholder="Enter your phone number"
            className="form-control"
          />
          <button onClick={() => setFormStep('ask_email')} className="btn btn-primary mt-2">Next</button>
        </div>
      );
    }

    if (formStep === 'ask_email') {
      return (
        <div>
          <input
            type="email"
            value={userInfo.email}
            onChange={(e) => setUserInfo({ ...userInfo, email: e.target.value })}
            placeholder="Enter your email"
            className="form-control"
          />
          <button onClick={handleSubmit} className="btn btn-primary mt-2">Submit</button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="chat-box">
      <div className="chat-container" ref={chatContainerRef}>
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.type}`}>
            <span>{msg.text}</span>
          </div>
        ))}
      </div>

      {formStep && renderForm()}

      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type a message..."
          className="form-control"
        />
        <button type="submit" className="btn btn-primary">Send</button>
      </form>

      <button onClick={handleDownload} className="btn btn-secondary mt-2">Download Conversation</button>
    </div>
  );
}

export default ChatBox;
