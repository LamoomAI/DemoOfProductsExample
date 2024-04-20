import React, { useEffect, useState } from 'react';
import LogEntry from './LogEntry';
import Button from './Button';

const PromptLogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        // Replace with actual backend call
        const response = await fetch('/api/logs');
        const data = await response.json();
        setLogs(data);
        console.log('Logs fetched:', data);
      } catch (err) {
        console.error('Error fetching logs:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  const handleTestPrompt = (contextId, promptId, version) => {
    console.log(`Testing prompt with contextId: ${contextId}, promptId: ${promptId}, version: ${version}`);
    // Replace with actual backend call to test the prompt
  };

  if (loading) return <div>Loading logs...</div>;
  if (error) return <div>Error loading logs: {error.message}</div>;

  return (
    <div>
      {logs.map((log) => (
        <LogEntry key={log.id} log={log}>
          <Button onClick={() => handleTestPrompt(log.context_id, log.prompt_id, log.version)}>
            Test Prompt
          </Button>
        </LogEntry>
      ))}
    </div>
  );
};

export default PromptLogViewer;