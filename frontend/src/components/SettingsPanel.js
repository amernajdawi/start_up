import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiX, FiTrash2, FiSave, FiSettings } from 'react-icons/fi';

const Backdrop = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;

const Panel = styled(motion.div)`
  background: var(--surface-color);
  border-radius: var(--border-radius);
  padding: 1.75rem;
  width: 90%;
  max-width: 540px;
  box-shadow: var(--shadow-lg);
  overflow: hidden;
  border: 1px solid var(--border-color);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.75rem;
  
  h2 {
    font-size: 1.5rem;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    
    svg {
      color: var(--primary-color);
    }
  }
`;

const CloseButton = styled.button`
  background: var(--background-color);
  border: none;
  color: var(--text-secondary);
  width: 36px;
  height: 36px;
  font-size: 1.2rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  transition: var(--transition);
  
  &:hover {
    background: var(--border-color);
    color: var(--text-primary);
    transform: translateY(-2px);
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  
  label {
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--text-primary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
`;

const Input = styled.input`
  padding: 0.9rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  background-color: var(--background-color);
  color: var(--text-primary);
  transition: var(--transition);
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
  }
`;

const SliderContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const SliderRow = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  
  span {
    min-width: 40px;
    text-align: center;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
    background: var(--background-color);
    padding: 0.3rem 0.5rem;
    border-radius: 6px;
    border: 1px solid var(--border-color);
  }
`;

const Slider = styled.input`
  flex: 1;
  height: 6px;
  -webkit-appearance: none;
  border-radius: 3px;
  background: linear-gradient(
    to right,
    var(--primary-color) 0%,
    var(--primary-color) ${props => props.percentage}%,
    var(--border-color) ${props => props.percentage}%,
    var(--border-color) 100%
  );
  outline: none;
  
  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: var(--primary-color);
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    transition: var(--transition);
  }
  
  &::-webkit-slider-thumb:hover {
    box-shadow: 0 0 0 6px rgba(99, 102, 241, 0.2);
    transform: scale(1.1);
  }
`;

const Description = styled.div`
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: 0.25rem;
  line-height: 1.4;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
`;

const Button = styled(motion.button)`
  padding: 0.9rem 1.5rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: var(--shadow);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const PrimaryButton = styled(Button)`
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark));
  color: var(--text-on-primary);
  border: none;
  flex: 1;
  justify-content: center;
`;

const SecondaryButton = styled(Button)`
  background-color: var(--background-color);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
`;

const DangerButton = styled(Button)`
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid var(--error-color);
  
  &:hover {
    background-color: rgba(239, 68, 68, 0.15);
  }
`;

const buttonVariants = {
  tap: { scale: 0.98 }
};

function SettingsPanel({ settings, onSave, onCancel, onClearMessages }) {
  const [formData, setFormData] = useState({
    temperature: settings.temperature,
    apiEndpoint: settings.apiEndpoint,
    modelName: settings.modelName
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave(formData);
  };

  // Calculate percentage for slider gradient
  const temperaturePercentage = (formData.temperature / 2) * 100;

  return (
    <Backdrop
      onClick={onCancel}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
    >
      <Panel
        onClick={e => e.stopPropagation()}
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 30 }}
        transition={{
          type: "spring",
          damping: 25,
          stiffness: 300
        }}
      >
        <Header>
          <h2>
            <FiSettings />
            Settings
          </h2>
          <CloseButton onClick={onCancel} aria-label="Close settings">
            <FiX />
          </CloseButton>
        </Header>

        <Form onSubmit={handleSubmit}>
          <FormGroup>
            <label htmlFor="modelName">Model Name</label>
            <Input
              type="text"
              id="modelName"
              name="modelName"
              value={formData.modelName}
              onChange={handleChange}
              placeholder="e.g. gpt-4o-mini"
            />
            <Description>
              The AI model to use for generating responses.
            </Description>
          </FormGroup>

          <FormGroup>
            <label htmlFor="temperature">Temperature</label>
            <SliderContainer>
              <SliderRow>
                <Slider
                  type="range"
                  id="temperature"
                  name="temperature"
                  min="0"
                  max="2"
                  step="0.1"
                  value={formData.temperature}
                  onChange={handleChange}
                  percentage={temperaturePercentage}
                />
                <span>{formData.temperature}</span>
              </SliderRow>
            </SliderContainer>
            <Description>
              Controls randomness: Lower values produce more focused and deterministic responses,
              while higher values produce more diverse and creative responses.
            </Description>
          </FormGroup>

          <FormGroup>
            <label htmlFor="apiEndpoint">API Endpoint</label>
            <Input
              type="text"
              id="apiEndpoint"
              name="apiEndpoint"
              value={formData.apiEndpoint}
              onChange={handleChange}
              placeholder="e.g. /api/chat"
            />
            <Description>
              The endpoint URL used to send API requests.
            </Description>
          </FormGroup>

          <ButtonGroup>
            <PrimaryButton
              type="submit"
              variants={buttonVariants}
              whileTap="tap"
            >
              <FiSave /> Save Settings
            </PrimaryButton>
            <DangerButton
              type="button"
              onClick={onClearMessages}
              variants={buttonVariants}
              whileTap="tap"
            >
              <FiTrash2 /> Clear Chat
            </DangerButton>
          </ButtonGroup>
        </Form>
      </Panel>
    </Backdrop>
  );
}

export default SettingsPanel; 