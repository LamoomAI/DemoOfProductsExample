import React, { useState, useEffect } from 'react';
import { Button, Input, Textarea } from './FormComponents';

const PromptTestForm = () => {
  const [promptText, setPromptText] = useState('');
  const [selectedBehavior, setSelectedBehavior] = useState('');
  const [response, setResponse] = useState('');
  const [behaviors, setBehaviors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Fetch behaviors from backend and update state
    // Placeholder for backend call
    const fetchBehaviors = async () => {
      try {
        setIsLoading(true);
        // Replace with actual backend call
        const behaviorsData = await getBehaviors();
        setBehaviors(behaviorsData);
        setIsLoading(false);
      } catch (error) {
        console.error('Error fetching behaviors:', error);
        setIsLoading(false);
      }
    };

    fetchBehaviors();
  }, []);

  const handlePromptSubmit = async (event) => {
    event.preventDefault();
    setIsLoading(true);
    try {
      // Replace with actual backend call
      const result = await testPrompt(promptText, selectedBehavior);
      setResponse(result);
      console.log('AI Model Response:', result);
    } catch (error) {
      console.error('Error testing prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handlePromptSubmit}>
      <Textarea
        label="Prompt"
        value={promptText}
        onChange={(e) => setPromptText(e.target.value)}
        placeholder="Enter your prompt here..."
      />
      <select
        value={selectedBehavior}
        onChange={(e) => setSelectedBehavior(e.target.value)}
      >
        {behaviors.map((behavior) => (
          <option key={behavior.id} value={behavior.id}>
            {behavior.name}
          </option>
        ))}
      </select>
      <Button type="submit" disabled={isLoading}>
        Test Prompt
      </Button>
      {isLoading && <p>Testing prompt...</p>}
      {response && <div>Response: {response}</div>}
    </form>
  );
};

// Placeholder functions for backend calls
const getBehaviors = async () => {
  // Implement backend call to fetch behaviors
  return [{ id: 'behavior1', name: 'Default Behavior' }]; // Example data
};

const testPrompt = async (promptText, behaviorId) => {
  // Implement backend call to test prompt with selected behavior
  return 'AI Model Response'; // Example response
};

export default PromptTestForm;