import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FiSend } from 'react-icons/fi';

const InputContainer = styled.div`
  padding: 1rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--surface-color);
  border-radius: 0 0 12px 12px;
`;

const Form = styled.form`
  display: flex;
  gap: 0.8rem;
`;

const TextareaWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const Textarea = styled.textarea`
  width: 100%;
  min-height: 50px;
  max-height: 150px;
  padding: 0.8rem 1rem;
  border-radius: 24px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
  background-color: var(--background-color);
  color: var(--text-primary);
  transition: border-color 0.3s ease;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(126, 87, 194, 0.1);
  }
  
  &::placeholder {
    color: var(--text-secondary);
    opacity: 0.7;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
`;

const SendButton = styled.button`
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: none;
  background-color: var(--primary-color);
  color: var(--text-on-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  align-self: flex-end;
  box-shadow: var(--shadow);
  
  &:hover {
    background-color: var(--primary-dark);
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
  
  svg {
    font-size: 1.2rem;
  }
`;

function ChatInput({ onSendMessage, disabled }) {
    const [message, setMessage] = useState('');
    const textareaRef = useRef(null);

    // Auto-resize textarea based on content
    useEffect(() => {
        const textarea = textareaRef.current;
        if (!textarea) return;

        textarea.style.height = 'auto';
        textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
    }, [message]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!message.trim() || disabled) return;

        onSendMessage(message);
        setMessage('');
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <InputContainer>
            <Form onSubmit={handleSubmit}>
                <TextareaWrapper>
                    <Textarea
                        ref={textareaRef}
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={handleKeyDown}
                        placeholder="Type your message here..."
                        disabled={disabled}
                        rows={1}
                    />
                </TextareaWrapper>
                <SendButton type="submit" disabled={!message.trim() || disabled}>
                    <FiSend />
                </SendButton>
            </Form>
        </InputContainer>
    );
}

export default ChatInput; 