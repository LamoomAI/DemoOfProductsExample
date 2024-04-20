import React, { useState, useEffect } from 'react';
import { Button, Input, Dropdown } from 'your-component-library';

const BehaviorCRUDForm = () => {
  const [behaviors, setBehaviors] = useState([]);
  const [selectedBehavior, setSelectedBehavior] = useState(null);
  const [behaviorName, setBehaviorName] = useState('');
  const [attempts, setAttempts] = useState([]);
  const [aiModel, setAiModel] = useState('');
  const [weight, setWeight] = useState(100);

  useEffect(() => {
    // Fetch behaviors and populate dropdown
    console.log('Fetching behaviors...');
    // Replace with actual backend call
    fetch('/api/behaviors')
      .then(response => response.json())
      .then(data => {
        setBehaviors(data);
        console.log('Behaviors fetched:', data);
      })
      .catch(error => console.error('Error fetching behaviors:', error));
  }, []);

  const handleBehaviorChange = (event) => {
    const { value } = event.target;
    setSelectedBehavior(value);
    // Fetch and populate form with selected behavior data
    console.log(`Behavior selected: ${value}`);
    // Replace with actual backend call
    fetch(`/api/behaviors/${value}`)
      .then(response => response.json())
      .then(data => {
        setBehaviorName(data.name);
        setAttempts(data.attempts);
        setAiModel(data.aiModel);
        setWeight(data.weight);
        console.log('Behavior data populated for editing:', data);
      })
      .catch(error => console.error('Error fetching behavior data:', error));
  };

  const handleNameChange = (event) => {
    setBehaviorName(event.target.value);
  };

  const handleWeightChange = (event) => {
    setWeight(event.target.value);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    const behaviorData = {
      name: behaviorName,
      attempts,
      aiModel,
      weight,
    };
    console.log('Submitting behavior:', behaviorData);
    // Replace with actual backend call
    const method = selectedBehavior ? 'PUT' : 'POST';
    const endpoint = selectedBehavior ? `/api/behaviors/${selectedBehavior}` : '/api/behaviors';
    fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(behaviorData),
    })
    .then(response => {
      if (response.ok) {
        console.log('Behavior submitted successfully:', behaviorData);
        // Reset form or provide further user feedback
      } else {
        console.error('Error submitting behavior:', response.statusText);
      }
    })
    .catch(error => console.error('Error submitting behavior:', error));
  };

  const handleDelete = () => {
    if (!selectedBehavior) {
      console.error('No behavior selected to delete');
      return;
    }
    console.log(`Deleting behavior: ${selectedBehavior}`);
    // Replace with actual backend call
    fetch(`/api/behaviors/${selectedBehavior}`, {
      method: 'DELETE',
    })
    .then(response => {
      if (response.ok) {
        console.log('Behavior deleted successfully');
        // Update state or provide further user feedback
      } else {
        console.error('Error deleting behavior:', response.statusText);
      }
    })
    .catch(error => console.error('Error deleting behavior:', error));
  };

  return (
    <form onSubmit={handleSubmit}>
      <Dropdown
        label="Select Behavior"
        options={behaviors.map(behavior => ({ label: behavior.name, value: behavior.id }))}
        onChange={handleBehaviorChange}
        value={selectedBehavior}
      />
      <Input label="Behavior Name" value={behaviorName} onChange={handleNameChange} />
      {/* Additional form fields for attempts and aiModel */}
      <Input label="Weight" type="number" value={weight} onChange={handleWeightChange} />
      <Button type="submit">Save Behavior</Button>
      <Button onClick={handleDelete} disabled={!selectedBehavior}>Delete Behavior</Button>
    </form>
  );
};

export default BehaviorCRUDForm;