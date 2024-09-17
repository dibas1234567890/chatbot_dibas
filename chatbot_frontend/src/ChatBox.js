import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './ChatBox.css';

function ChatBox() {
  const [step, setStep] = useState('form');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleFormSubmit = (e) => {
    e.preventDefault();
    if (name && phone && email) {
      const introMessage = `User Information:\nName: ${name}\nPhone: ${phone}\nEmail: ${email}\n`;
      setMessages([{ type: 'system', text: introMessage }]);
      setStep('chat');
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const newMessage = { type: 'user', text: question };
    setMessages([...messages, newMessage]);

    axios.post('http://localhost:8000/api/question/', { question })
      .then(response => {
        const botMessage = { type: 'bot', text: response.data.answer };
        setMessages([...messages, newMessage, botMessage]);
        setQuestion('');
      })
      .catch(error => {
        console.error('Error fetching answer', error);
      });
  };

  const handleDownload = () => {
    const userInfo = `User Information:\nName: ${name}\nPhone: ${phone}\nEmail: ${email}\n\n`;
    const blob = new Blob([userInfo + messages.map(msg => `${msg.type === 'user' ? 'You' : 'Bot'}: ${msg.text}`).join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'conversation.txt';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="chat-box">
      {step === 'form' ? (
        <form onSubmit={handleFormSubmit} className="form-container">
          <h2>Enter your details</h2>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Name"
            className="form-control"
            required
          />
          <input
            type="text"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            placeholder="Phone"
            className="form-control"
            required
          />
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Email"
            className="form-control"
            required
          />
          <button type="submit" className="btn btn-primary">Start Chat</button>
        </form>
      ) : (
        <>
          <div className="chat-container" ref={chatContainerRef}>
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <span>{msg.text}</span>
              </div>
            ))}
          </div>
          
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
        </>
      )}
    </div>
  );
}

export default ChatBox;
