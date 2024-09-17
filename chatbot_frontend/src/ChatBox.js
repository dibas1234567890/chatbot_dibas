import React, { useState } from 'react';
import axios from 'axios';

function ChatBox() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();

    axios.post('http://localhost:8000/api/question/', { question })
      .then(response => {
        setAnswer(response.data.answer);
      })
      .catch(error => {
        console.error('Error fetching answer', error);
      });
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question"
        />
        <button type="submit">Submit</button>
      </form>
      <p>Answer: {answer}</p>
    </div>
  );
}

export default ChatBox;
