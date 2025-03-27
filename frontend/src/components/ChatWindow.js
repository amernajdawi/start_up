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
`;

const MessageContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  max-width: 88%;
  
  ${props => props.role === 'user' ? `
    align-self: flex-end;
  ` : `
    align-self: flex-start;
  `}
`;

const MessageBubble = styled.div`
  padding: 1rem;
  border-radius: 18px;
  font-size: 1rem;
  line-height: 1.5;
  box-shadow: var(--shadow);
  
  ${props => props.role === 'user' ? `
    background-color: var(--chat-user-bg);
    border-bottom-right-radius: 4px;
  ` : `
    background-color: var(--chat-assistant-bg);
    border-bottom-left-radius: 4px;
  `}
  
  p {
    margin-bottom: 1rem;
  }
  
  p:last-child {
    margin-bottom: 0;
  }
  
  pre {
    background: rgba(0, 0, 0, 0.05);
    padding: 0.8rem;
    border-radius: 8px;
    overflow-x: auto;
    margin: 1rem 0;
  }
  
  code {
    font-family: 'Courier New', monospace;
  }
  
  ul, ol {
    padding-left: 1.5rem;
    margin: 0.5rem 0;
  }
`;

const MessageRole = styled.div`
  font-size: 0.85rem;
  color: var(--text-secondary);
  ${props => props.role === 'user' ? `
    text-align: right;
    padding-right: 0.5rem;
  ` : `
    padding-left: 0.5rem;
  `}
`;

const LoadingIndicator = styled.div`
  align-self: flex-start;
  padding: 1rem;
  background-color: var(--chat-assistant-bg);
  border-radius: 18px;
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  color: var(--text-secondary);
  
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
  
  h3 {
    margin-bottom: 1rem;
    font-weight: 500;
  }
  
  p {
    text-align: center;
    max-width: 400px;
    line-height: 1.6;
  }
`;

const messageVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.3 } }
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
                <h3>Welcome to AI Chat Assistant</h3>
                <p>Send a message to start a conversation with the AI model.</p>
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