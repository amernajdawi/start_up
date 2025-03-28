import React, { useRef, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

const ChatContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  scroll-behavior: smooth;
  
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
`;

const MessageContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-width: 90%;
  
  ${props => props.role === 'user' ? `
    align-self: flex-end;
  ` : `
    align-self: flex-start;
  `}
  
  @media (min-width: 768px) {
    max-width: 75%;
  }
`;

const MessageBubble = styled.div`
  padding: 1rem 1.25rem;
  border-radius: 18px;
  font-size: 1rem;
  line-height: 1.6;
  box-shadow: var(--shadow);
  
  ${props => props.role === 'user' ? `
    background: linear-gradient(to bottom right, var(--primary-color), var(--primary-dark));
    color: var(--text-on-primary);
    border-bottom-right-radius: 4px;
  ` : `
    background-color: var(--chat-assistant-bg);
    border: 1px solid var(--border-color);
    border-bottom-left-radius: 4px;
  `}
  
  p {
    margin-bottom: 1rem;
  }
  
  p:last-child {
    margin-bottom: 0;
  }
  
  pre {
    background: ${props => props.role === 'user'
    ? 'rgba(0, 0, 0, 0.2)'
    : 'rgba(0, 0, 0, 0.05)'};
    padding: 1rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
    font-size: 0.9rem;
  }
  
  code {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    padding: 0.2rem 0.4rem;
    background: ${props => props.role === 'user'
    ? 'rgba(0, 0, 0, 0.2)'
    : 'rgba(0, 0, 0, 0.05)'};
    border-radius: 4px;
  }
  
  ul, ol {
    padding-left: 1.5rem;
    margin: 0.75rem 0;
  }
  
  a {
    color: ${props => props.role === 'user'
    ? 'var(--text-on-primary)'
    : 'var(--primary-color)'};
    text-decoration: underline;
    text-underline-offset: 2px;
  }
  
  h1, h2, h3, h4, h5, h6 {
    margin: 1.5rem 0 0.75rem;
    font-weight: 600;
  }
  
  h1:first-child, h2:first-child, h3:first-child {
    margin-top: 0;
  }
  
  blockquote {
    border-left: 3px solid ${props => props.role === 'user'
    ? 'rgba(255, 255, 255, 0.5)'
    : 'var(--primary-light)'};
    padding-left: 1rem;
    margin: 1rem 0;
    font-style: italic;
    color: ${props => props.role === 'user'
    ? 'rgba(255, 255, 255, 0.9)'
    : 'var(--text-secondary)'};
  }
`;

const MessageRole = styled.div`
  font-size: 0.85rem;
  color: var(--text-secondary);
  font-weight: 500;
  display: flex;
  align-items: center;
  
  ${props => props.role === 'user' ? `
    justify-content: flex-end;
    padding-right: 0.5rem;
  ` : `
    padding-left: 0.5rem;
  `}
  
  &::before {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 6px;
    background-color: ${props => props.role === 'user'
    ? 'var(--primary-color)'
    : 'var(--secondary-color)'};
  }
  
  ${props => props.role === 'user' ? `
    &::before {
      order: 2;
      margin-right: 0;
      margin-left: 6px;
    }
  ` : ''}
`;

const LoadingIndicator = styled.div`
  align-self: flex-start;
  padding: 1rem 1.5rem;
  background-color: var(--chat-assistant-bg);
  border-radius: 18px;
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  
  .dot {
    width: 8px;
    height: 8px;
    background: var(--primary-color);
    border-radius: 50%;
    opacity: 0.6;
    animation: bounce 1.4s infinite ease-in-out;
  }
  
  .dot:nth-child(1) {
    animation-delay: 0s;
  }
  
  .dot:nth-child(2) {
    animation-delay: 0.2s;
  }
  
  .dot:nth-child(3) {
    animation-delay: 0.4s;
  }
  
  @keyframes bounce {
    0%, 80%, 100% {
      transform: translateY(0);
    }
    40% {
      transform: translateY(-8px);
    }
  }
`;

const EmptyState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--text-secondary);
  padding: 2rem;
  text-align: center;
  
  h3 {
    margin-bottom: 1rem;
    font-weight: 600;
    color: var(--primary-color);
    font-size: 1.6rem;
  }
  
  p {
    text-align: center;
    max-width: 450px;
    line-height: 1.6;
    margin-bottom: 1.5rem;
  }
  
  .welcome-icon {
    font-size: 3rem;
    margin-bottom: 1.5rem;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  
  .example-queries {
    display: flex;
    flex-direction: column;
    gap: 0.8rem;
    width: 100%;
    max-width: 450px;
    margin-top: 1rem;
  }
  
  .example-query {
    padding: 0.75rem 1rem;
    background-color: var(--background-color);
    border-radius: 8px;
    cursor: pointer;
    transition: var(--transition);
    border: 1px solid var(--border-color);
    text-align: left;
    
    &:hover {
      transform: translateY(-2px);
      background-color: var(--primary-light);
      color: var(--text-on-primary);
    }
  }
`;

const messageVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: [0.25, 0.1, 0.25, 1.0]
    }
  }
};

function ChatWindow({ messages, loading }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0 && !loading) {
    return (
      <EmptyState>
        <div className="welcome-icon">💬</div>
        <h3>Welcome to AI Chat</h3>
        <p>
          Ask me anything - I'm here to assist with information, creative ideas,
          code help, and more.
        </p>
        <div className="example-queries">
          <button className="example-query">Explain quantum computing in simple terms</button>
          <button className="example-query">Write a poem about technology and nature</button>
          <button className="example-query">What's the best way to learn JavaScript?</button>
        </div>
      </EmptyState>
    );
  }

  return (
    <ChatContainer>
      {messages.map((message, index) => (
        <MessageContainer
          key={index}
          role={message.role}
          initial="hidden"
          animate="visible"
          variants={messageVariants}
          custom={index}
        >
          <MessageRole role={message.role}>
            {message.role === 'user' ? 'You' : 'AI Assistant'}
          </MessageRole>
          <MessageBubble role={message.role}>
            <ReactMarkdown>
              {message.content}
            </ReactMarkdown>
          </MessageBubble>
        </MessageContainer>
      ))}

      {loading && (
        <LoadingIndicator>
          <div className="dot"></div>
          <div className="dot"></div>
          <div className="dot"></div>
        </LoadingIndicator>
      )}

      <div ref={messagesEndRef} />
    </ChatContainer>
  );
}

export default ChatWindow; 