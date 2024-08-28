import React, { useState, useEffect } from 'react';
import './App.css';

// Constants
const SERVER_IP = import.meta.env.VITE_server_ip;
const BACK_PORT = import.meta.env.VITE_back_port;

// Initial states
const initialSimConfig = {
  template: '',
  new: '',
  sim_code: '',
  sim_mode: null,
  start_date: "",
  curr_time: "",
  maze_name: "the_villie",
  step: 0,
  llm_config: 'inherit',
  api_base: '',
  api_key: '',
  engine: '',
  temperature: 1.0,
  max_tokens: 512,
  top_p: 0.7,
  frequency_penalty: 0.0,
  presence_penalty: 0.0,
  stream: false
};

// Utility functions
const resizeTextAreas = () => {
  document.querySelectorAll('.dynamic-textarea').forEach((textarea) => {
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
  });
};

function StartApp() {
  // State declarations
  const [activeTab, setActiveTab] = useState('basic');
  const [agents, setAgents] = useState([]);
  const [events, setEvents] = useState([]);
  const [selectedEventId, setSelectedEventId] = useState(null);
  const [nextEventId, setNextEventId] = useState(1);
  const [selectedAgentId, setSelectedAgentId] = useState(null);
  const [nextAgentId, setNextAgentId] = useState(1);
  const [templates, setTemplates] = useState([]);
  const [simConfig, setSimConfig] = useState(initialSimConfig);

  // API calls
  const getEnvs = async () => {
    try {
      const response = await fetch(`http://${SERVER_IP}:${BACK_PORT}/list_envs/`, { method: 'GET' });
      const data = await response.json();
      return data.envs;
    } catch (error) {
      console.error("Error fetching environments:", error);
      return [];
    }
  };

  const fetchEnvInfo = async (template) => {
    try {
      const params = new URLSearchParams({ env_name: template });
      const response = await fetch(`http://${SERVER_IP}:${BACK_PORT}/env_info/?${params}`, { method: 'GET' });
      const data = await response.json();

      setSimConfig(prev => ({
        ...prev,
        start_date: data.meta.start_date,
        curr_time: data.meta.curr_time,
        maze_name: data.meta.maze_name,
        step: data.meta.step,
        sim_mode: data.meta.sim_mode,
      }));

      setEvents(data.events.map((event, index) => ({
        id: index + 1,
        name: `Event ${index + 1}`,
        access_list: event.access_list.join(","),
        websearch: event.websearch,
        policy: event.policy,
        description: event.description,
      })));

      setAgents(Object.values(data.personas).map((persona, index) => ({
        id: index,
        name: persona.name,
        daily_plan_req: persona.daily_plan_req,
        first_name: persona.first_name,
        last_name: persona.last_name,
        age: persona.age,
        innate: persona.innate,
        learned: persona.learned,
        currently: persona.currently,
        lifestyle: persona.lifestyle,
        living_area: persona.living_area,
        bibliography: persona.bibliography,
      })));

      setNextAgentId(Object.values(data.personas).length);
    } catch (error) {
      console.error("Error fetching environment info:", error);
    }
  };

  const startSim = async (e) => {
    e.preventDefault();
    const newConfig = {
      sim_code: simConfig.sim_code,
      start_date: simConfig.start_date,
      curr_time: simConfig.curr_time,
      maze_name: simConfig.maze_name,
      step: parseInt(simConfig.step),
      sim_mode: simConfig.sim_mode,
      personas: agents,
      events: events,
      llm_config: simConfig.llm_config === 'custom' ? {
        api_base: simConfig.api_base,
        api_key: simConfig.api_key,
        engine: simConfig.engine,
        temperature: parseFloat(simConfig.temperature),
        max_tokens: parseInt(simConfig.max_tokens),
        top_p: parseFloat(simConfig.top_p),
        frequency_penalty: parseFloat(simConfig.frequency_penalty),
        presence_penalty: parseFloat(simConfig.presence_penalty),
        stream: simConfig.stream
      } : null
    };

    Object.keys(newConfig).forEach(key =>
      (newConfig[key] === null || newConfig[key] === "") && delete newConfig[key]
    );

    const requestBody = {
      template: simConfig.template,
      config: newConfig
    };

    try {
      const response = await fetch(`http://${SERVER_IP}:${BACK_PORT}/start/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      if (response.ok) {
        window.location.href = `/act`;
      } else {
        console.error("Failed to start simulation");
      }
    } catch (error) {
      console.error("Error starting simulation:", error);
    }
  };

  // Event handlers
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSimConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const addNewAgent = () => {
    const newAgent = {
      id: nextAgentId,
      name: `Agent ${nextAgentId}`,
      daily_plan_req: "",
      first_name: "",
      last_name: "",
      age: 0,
      innate: "",
      learned: "",
      currently: "",
      lifestyle: "",
      living_area: "",
      bibliography: ""
    };
    setAgents([...agents, newAgent]);
    setSelectedAgentId(newAgent.id);
    setNextAgentId(nextAgentId + 1);
  };

  const addNewEvent = () => {
    const newEvent = {
      id: nextEventId,
      name: `Event ${nextEventId}`,
      access_list: "",
      websearch: "",
      policy: "",
      description: ""
    };
    setEvents([...events, newEvent]);
    setSelectedEventId(newEvent.id);
    setNextEventId(nextEventId + 1);
  };

  const updateAgent = (field, value) => {
    setAgents(agents.map(agent =>
      agent.id === selectedAgentId ? { ...agent, [field]: value } : agent
    ));
  };

  const updateEvent = (field, value) => {
    setEvents(events.map(event =>
      event.id === selectedEventId ? { ...event, [field]: value } : event
    ));
  };

  // Effects
  useEffect(() => {
    const fetchTemplates = async () => {
      const envs = await getEnvs();
      setTemplates(envs);
      fetchEnvInfo(envs[0]);
      setSimConfig(prev => ({ ...prev, template: envs[0] }));
    };
    fetchTemplates();
  }, []);

  useEffect(() => {
    resizeTextAreas();
  }, [selectedAgentId, selectedEventId, activeTab]);

  // Render helpers
  const renderBasicConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="template">Template:</label>
        <select
          id="template"
          name="template"
          value={simConfig.template}
          onChange={(e) => {
            handleInputChange(e);
            fetchEnvInfo(e.target.value);
          }}
          className="w-full p-2 border rounded"
          required
        >
          {templates.map((env) => (
            <option key={env} value={env}>{env}</option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="sim_code">Simulation Name:</label>
        <input
          type="text"
          id="sim_code"
          name="sim_code"
          value={simConfig.sim_code}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="sim_mode">Simulation Mode:</label>
        <select
          id="sim_mode"
          name="sim_mode"
          value={simConfig.sim_mode || ''}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
        >
          <option value="">Inherit from template</option>
          <option value="offline">Offline</option>
          <option value="online">Online</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="maze_name">Maze Name:</label>
        <input
          type="text"
          id="maze_name"
          name="maze_name"
          value={simConfig.maze_name}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
          placeholder="e.g., the_ville"
        />
      </div>
    </div>
  );

  const renderAgentConfig = () => (
    <div className="flex h-[500px]">
      <div className="w-1/3 pr-4 border-r flex flex-col">
        <ul className="flex-grow overflow-auto">
          {agents.map((agent) => (
            <li
              key={agent.id}
              className={`flex justify-between items-center p-2 ${selectedAgentId === agent.id ? 'bg-blue-100' : ''}`}
            >
              <span
                className="cursor-pointer flex-grow"
                onClick={() => setSelectedAgentId(agent.id)}
              >
                {agent.name}
              </span>
              <button
                className="ml-2 text-red-600 hover:text-red-800"
                onClick={(e) => {
                  e.stopPropagation();
                  const newAgents = agents.filter(a => a.id !== agent.id);
                  setAgents(newAgents);
                  if (selectedAgentId === agent.id) {
                    setSelectedAgentId(newAgents[0]?.id || null);
                  }
                }}
              >
                ×
              </button>
            </li>
          ))}
          <li
            className="cursor-pointer p-2 text-blue-600"
            onClick={addNewAgent}
          >
            + Add New Agent
          </li>
        </ul>
      </div>

      <div className="w-2/3 pl-4 overflow-auto">
        {selectedAgentId ? (
          <div className="space-y-4">
            <div className="grid grid-cols-4 gap-4">
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="name">Name:</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={agents.find(a => a.id === selectedAgentId)?.name || ""}
                  onChange={(e) => updateAgent('name', e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="first_name">First Name:</label>
                <input
                  type="text"
                  id="first_name"
                  name="first_name"
                  value={agents.find(a => a.id === selectedAgentId)?.first_name || ""}
                  onChange={(e) => updateAgent('first_name', e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="last_name">Last Name:</label>
                <input
                  type="text"
                  id="last_name"
                  name="last_name"
                  value={agents.find(a => a.id === selectedAgentId)?.last_name || ""}
                  onChange={(e) => updateAgent('last_name', e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="age">Age:</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={agents.find(a => a.id === selectedAgentId)?.age || ""}
                  onChange={(e) => updateAgent('age', e.target.value)}
                  className="w-full p-2 border rounded"
                />
              </div>
            </div>
            {['daily_plan_req', 'innate', 'learned', 'currently', 'lifestyle', 'living_area', 'bibliography'].map((field) => (
              <div key={field} className="flex flex-col mb-4">
                <label className="block text-sm font-medium mb-1" htmlFor={field}>
                  {field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ')}:
                </label>
                <textarea
                  id={field}
                  name={field}
                  value={agents.find(a => a.id === selectedAgentId)?.[field] || ""}
                  onChange={(e) => updateAgent(field, e.target.value)}
                  className="p-2 border rounded w-full resize-none dynamic-textarea"
                  rows={1}
                  style={{ overflow: 'hidden', height: 'auto' }}
                  onInput={(e) => {
                    e.target.style.height = '';
                    e.target.style.height = `${e.target.scrollHeight}px`;
                  }}
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-lg font-medium mb-2">
            Click on an agent to view or edit their details, or add a new agent.
          </div>
        )}
      </div>
    </div>
  );

  // ... (previous code remains the same)

  const renderEventConfig = () => (
    <div className="flex h-[500px]">
      <div className="w-1/3 pr-4 border-r flex flex-col">
        <ul className="flex-grow overflow-auto">
          {events.map((event) => (
            <li
              key={event.id}
              className={`flex justify-between items-center p-2 ${selectedEventId === event.id ? 'bg-blue-100' : ''}`}
            >
              <span
                className="cursor-pointer flex-grow"
                onClick={() => setSelectedEventId(event.id)}
              >
                {event.name}
              </span>
              <button
                className="ml-2 text-red-600 hover:text-red-800"
                onClick={(e) => {
                  e.stopPropagation();
                  const newEvents = events.filter(e => e.id !== event.id);
                  setEvents(newEvents);
                  if (selectedEventId === event.id) {
                    setSelectedEventId(newEvents[0]?.id || null);
                  }
                }}
              >
                ×
              </button>
            </li>
          ))}
          <li
            className="cursor-pointer p-2 text-blue-600"
            onClick={addNewEvent}
          >
            + Add New Event
          </li>
        </ul>
      </div>

      <div className="w-2/3 pl-4 overflow-auto">
        {selectedEventId ? (
          <div className="space-y-4">
            <h3 className="text-lg font-medium mb-2">Event Configuration</h3>
            {['name', 'access_list', 'websearch', 'policy', 'description'].map((field) => (
              <div key={field}>
                <label className="block text-sm font-medium mb-1" htmlFor={field}>
                  {field.charAt(0).toUpperCase() + field.slice(1).replace('_', ' ')}:
                </label>
                <textarea
                  id={field}
                  name={field}
                  rows={1}
                  style={{ overflow: 'hidden', height: 'auto' }}
                  value={events.find(e => e.id === selectedEventId)?.[field] || ""}
                  onChange={(e) => updateEvent(field, e.target.value)}
                  className="p-2 border rounded w-full resize-none dynamic-textarea"
                />
              </div>
            ))}
          </div>
        ) : (
          <div className="text-lg font-medium mb-2">
            Click on an event to view or edit its details, or add a new event.
          </div>
        )}
      </div>
    </div>
  );

  const renderLLMConfig = () => (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1" htmlFor="llm_config">Configuration Type:</label>
        <select
          id="llm_config"
          name="llm_config"
          value={simConfig.llm_config}
          onChange={handleInputChange}
          className="w-full p-2 border rounded"
        >
          <option value="default">Default</option>
          <option value="custom">Custom</option>
        </select>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="api_base">API Base:</label>
          <input
            disabled={simConfig.llm_config === 'default'}
            type="text"
            id="api_base"
            name="api_base"
            value={simConfig.api_base}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            placeholder="https://api.openai.com/v1"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="api_key">API Key:</label>
          <input
            type="password"
            id="api_key"
            name="api_key"
            value={simConfig.api_key}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            placeholder="Your API key"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="engine">Engine:</label>
          <input
            type="text"
            id="engine"
            name="engine"
            value={simConfig.engine}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            placeholder="e.g., gpt-3.5-turbo"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="temperature">Temperature:</label>
          <input
            type="number"
            id="temperature"
            name="temperature"
            value={simConfig.temperature}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            min="0"
            max="2"
            step="0.1"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="max_tokens">Max Tokens:</label>
          <input
            type="number"
            id="max_tokens"
            name="max_tokens"
            value={simConfig.max_tokens}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            min="1"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="top_p">Top P:</label>
          <input
            type="number"
            id="top_p"
            name="top_p"
            value={simConfig.top_p}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            min="0"
            max="1"
            step="0.01"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="frequency_penalty">Frequency Penalty:</label>
          <input
            type="number"
            id="frequency_penalty"
            name="frequency_penalty"
            value={simConfig.frequency_penalty}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            min="-2"
            max="2"
            step="0.1"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="presence_penalty">Presence Penalty:</label>
          <input
            type="number"
            id="presence_penalty"
            name="presence_penalty"
            value={simConfig.presence_penalty}
            onChange={handleInputChange}
            className="w-full p-2 border rounded"
            min="-2"
            max="2"
            step="0.1"
            disabled={simConfig.llm_config === 'default'}
          />
        </div>
      </div>
      <div className="flex items-center mt-4">
        <input
          type="checkbox"
          id="stream"
          name="stream"
          checked={simConfig.stream}
          onChange={handleInputChange}
          disabled={simConfig.llm_config === 'default'}
          className="mr-2"
        />
        <label className="text-sm font-medium" htmlFor="stream">Stream</label>
      </div>
    </div>
  );

  const tabContent = {
    basic: renderBasicConfig(),
    agent: renderAgentConfig(),
    event: renderEventConfig(),
    llm: renderLLMConfig()
  };

  // Main render
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-200 to-red-200 p-4">
      <div className="w-full max-w-4xl bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Start Simulation</h2>

        <div className="flex mb-4 border-b">
          {['basic', 'agent', 'event', 'llm'].map((tab) => (
            <button
              key={tab}
              className={`px-4 py-2 ${activeTab === tab ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-500'}`}
              onClick={() => setActiveTab(tab)}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)} Configuration
            </button>
          ))}
        </div>

        <div className="mt-4 mb-6 h-[500px]" style={{ "padding": "15px" }}>
          {tabContent[activeTab]}
        </div>

        <button
          type="button"
          className="w-full px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700"
          onClick={startSim}
        >
          Start Simulation
        </button>
      </div>

      <div className="mt-8 text-center">
        <h2 className="text-2xl font-bold">Social Simulation Agent</h2>
        <p className="mt-2 text-gray-600">
          Developed by DAI Lab, Zhejiang University.
        </p>
      </div>
    </div>
  );
}

export default StartApp;