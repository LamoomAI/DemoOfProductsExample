import React, { useState, useEffect } from 'react';
import { Select } from 'your-component-library';

const EnvironmentSelector = () => {
  const [selectedEnvironment, setSelectedEnvironment] = useState(null);
  const [environmentsList, setEnvironmentsList] = useState([]);

  useEffect(() => {
    const fetchEnvironments = async () => {
      try {
        // Replace with your actual backend call
        const response = await fetch('/api/environments');
        const data = await response.json();
        setEnvironmentsList(data);
      } catch (error) {
        console.error('Error fetching environments:', error);
      }
    };

    fetchEnvironments();
  }, []);

  const handleSelectEnvironment = (event) => {
    const newEnvironment = event.target.value;
    setSelectedEnvironment(newEnvironment);
    console.log('Selected environment:', newEnvironment);
  };

  return (
    <Select value={selectedEnvironment} onChange={handleSelectEnvironment}>
      {environmentsList.map((env) => (
        <option key={env.id} value={env.id}>
          {env.name}
        </option>
      ))}
    </Select>
  );
};

export default EnvironmentSelector;