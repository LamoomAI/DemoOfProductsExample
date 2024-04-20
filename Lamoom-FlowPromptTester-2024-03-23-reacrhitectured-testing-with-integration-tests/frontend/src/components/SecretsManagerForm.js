import React, { useState } from 'react';
import { Button, Input } from './components'; // Assuming these are imported from a UI library

const SecretsManagerForm = () => {
  const [azureOpenAiKeys, setAzureOpenAiKeys] = useState('');
  const [openAiOrg, setOpenAiOrg] = useState('');
  const [openAiApiKey, setOpenAiApiKey] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAzureOpenAiKeysChange = (event) => {
    setAzureOpenAiKeys(event.target.value);
    console.log('Azure OpenAI Keys changed:', event.target.value);
  };

  const handleOpenAiOrgChange = (event) => {
    setOpenAiOrg(event.target.value);
    console.log('OpenAI Org changed:', event.target.value);
  };

  const handleOpenAiApiKeyChange = (event) => {
    setOpenAiApiKey(event.target.value);
    console.log('OpenAI API Key changed:', event.target.value);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setIsSubmitting(true);
    console.log('Submitting secrets to backend...');

    // Replace with actual backend call
    try {
      // const response = await saveSecretsToBackend({ azureOpenAiKeys, openAiOrg, openAiApiKey });
      // console.log('Backend response:', response);
      console.log('Secrets saved successfully');
    } catch (error) {
      console.error('Error saving secrets:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <Input
        label="Azure OpenAI Keys"
        value={azureOpenAiKeys}
        onChange={handleAzureOpenAiKeysChange}
        disabled={isSubmitting}
      />
      <Input
        label="OpenAI Org"
        value={openAiOrg}
        onChange={handleOpenAiOrgChange}
        disabled={isSubmitting}
      />
      <Input
        label="OpenAI API Key"
        value={openAiApiKey}
        onChange={handleOpenAiApiKeyChange}
        disabled={isSubmitting}
      />
      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Secrets'}
      </Button>
    </form>
  );
};

export default SecretsManagerForm;