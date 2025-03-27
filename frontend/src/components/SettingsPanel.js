import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { FiX, FiTrash2 } from 'react-icons/fi';

const Backdrop = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
`;

const Panel = styled(motion.div)`
  background: var(--surface-color);
  border-radius: 12px;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  
  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--primary-color);
  }
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 50%;
  transition: all 0.2s ease;
  
  &:hover {
    background: var(--background-color);
    color: var(--text-primary);
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  
  label {
    font-weight: 500;
    font-size: 0.9rem;
    color: var(--text-secondary);
  }
`;

const Input = styled.input`
  padding: 0.8rem 1rem;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  font-size: 1rem;
  background-color: var(--background-color);
  color: var(--text-primary);
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(126, 87, 194, 0.1);
  }
`;

const SliderContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
`;

const SliderRow = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  
  span {
    min-width: 40px;
    text-align: center;
    font-weight: 500;
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
    transition: all 0.2s ease;
  }
  
  &::-webkit-slider-thumb:hover {
    box-shadow: 0 0 0 6px rgba(126, 87, 194, 0.2);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  margin-top: 1.2rem;
  flex-wrap: wrap;
`;

const Button = styled.button`
  padding: 0.8rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  
  &:hover {
    transform: translateY(-2px);
  }
  
  &:active {
    transform: translateY(0);
  }
`;

const PrimaryButton = styled(Button)`
  background-color: var(--primary-color);
  color: var(--text-on-primary);
  border: none;
  flex: 1;
  justify-content: center;
  
  &:hover {
    background-color: var(--primary-dark);
  }
`;

const SecondaryButton = styled(Button)`
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  
  &:hover {
    background-color: var(--background-color);
  }
`;

const DangerButton = styled(Button)`
  background-color: transparent;
  color: var(--error-color);
  border: 1px solid var(--error-color);
  
  &:hover {
    background-color: rgba(176, 0, 32, 0.1);
  }
`;

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
        <Backdrop onClick={onCancel}>
            <Panel
                onClick={e => e.stopPropagation()}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{ duration: 0.3 }}
            >
                <Header>
                    <h2>Settings</h2>
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
                    </FormGroup>

                    <FormGroup>
                        <label htmlFor="apiEndpoint">API Endpoint</label>
                        <Input
                            type="text"
                            id="apiEndpoint"
                            name="apiEndpoint"
                            value={formData.apiEndpoint}
                            onChange={handleChange}
                            placeholder="e.g. /chat"
                        />
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
                            <small>
                                Lower values make responses more deterministic, higher values make them more creative.
                            </small>
                        </SliderContainer>
                    </FormGroup>

                    <ButtonGroup>
                        <PrimaryButton type="submit">Save Settings</PrimaryButton>
                        <SecondaryButton type="button" onClick={onCancel}>Cancel</SecondaryButton>
                        <DangerButton type="button" onClick={onClearMessages}>
                            <FiTrash2 />
                            Clear Chat
                        </DangerButton>
                    </ButtonGroup>
                </Form>
            </Panel>
        </Backdrop>
    );
}

export default SettingsPanel; 