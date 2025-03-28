import React, { useState, useRef, useEffect } from 'react';
import styled from 'styled-components';
import { FiSend, FiMic } from 'react-icons/fi';
import { motion } from 'framer-motion';

const InputContainer = styled.div`
  padding: 1.25rem;
  border-top: 1px solid var(--border-color);
  background-color: var(--surface-color);
  border-radius: 0 0 var(--border-radius) var(--border-radius);
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: 0;
    right: 0;
    height: 2px;
    background: linear-gradient(
      to right,
      transparent,
      var(--primary-light),
      transparent
    );
    opacity: 0.7;
  }
`;

const Form = styled.form`
  display: flex;
  gap: 0.8rem;
  position: relative;
`;

const TextareaWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const Textarea = styled.textarea`
  width: 100%;
  min-height: 55px;
  max-height: 150px;
  padding: 1rem 1.25rem;
  border-radius: 24px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  line-height: 1.5;
  resize: none;
  background-color: var(--background-color);
  color: var(--text-primary);
  transition: all 0.2s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
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

const ButtonsContainer = styled.div`
  display: flex;
  gap: 0.6rem;
  align-self: flex-end;
`;

const ActionButton = styled(motion.button)`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background-color: ${props => props.secondary ? 'var(--background-color)' : 'var(--primary-color)'};
  color: ${props => props.secondary ? 'var(--text-secondary)' : 'var(--text-on-primary)'};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: var(--shadow);
  
  &:hover {
    background-color: ${props => props.secondary ? 'var(--border-color)' : 'var(--primary-dark)'};
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
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

const CharCounter = styled.div`
  position: absolute;
  right: 12px;
  bottom: -22px;
  font-size: 0.75rem;
  color: var(--text-secondary);
  opacity: ${props => props.isVisible ? '1' : '0'};
  transition: opacity 0.2s ease;
`;

const buttonVariants = {
  tap: { scale: 0.95 }
};

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
          <CharCounter isVisible={message.length > 0}>
            {message.length} characters
          </CharCounter>
        </TextareaWrapper>
        <ButtonsContainer>
          <ActionButton
            type="button"
            secondary
            disabled={disabled}
            variants={buttonVariants}
            whileTap="tap"
            aria-label="Voice input"
          >
            <FiMic />
          </ActionButton>
          <ActionButton
            type="submit"
            disabled={!message.trim() || disabled}
            variants={buttonVariants}
            whileTap="tap"
            aria-label="Send message"
          >
            <FiSend />
          </ActionButton>
        </ButtonsContainer>
      </Form>
    </InputContainer>
  );
}

export default ChatInput; 