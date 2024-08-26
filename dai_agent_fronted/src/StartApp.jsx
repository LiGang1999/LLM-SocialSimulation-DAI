import React, { useState, useEffect } from 'react';
import './App.css';

function StartApp() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;

  const [templates, setTemplates] = useState([]);
  const [showLLMConfig, setShowLLMConfig] = useState(false);
  const [simConfig, setSimConfig] = useState({
    template: '',
    new: '',
    sim_code: '',
    sim_mode: null,
    start_date: "",
    curr_time: "",
    maze_name: "the_villie",
    step: 0,
    persona_names: "",
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
  });

  useEffect(() => {
    const fetchTemplates = async () => {
      const envs = await get_envs();
      setTemplates(envs);
      setSimConfig(prev => ({
        ...prev,
        template: envs[0]
      }));
    };
    fetchTemplates();
  }, []);

  const get_envs = async () => {
    var url = `http://${server_ip}:${back_port}/list_envs/`;
    try {
      const response = await fetch(url, { method: 'GET' });
      const data = await response.json();
      return data.envs;
    } catch (error) {
      console.error("Error fetching environments:", error);
      return [];
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSimConfig(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const start_sim = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('template', simConfig.template);

    const newConfig = {
      sim_code: simConfig.sim_code,
      start_date: simConfig.start_date,
      curr_time: simConfig.curr_time,
      maze_name: simConfig.maze_name,
      step: parseInt(simConfig.step),
      persona_names: simConfig.persona_names.split(',').map(name => name.trim()).filter(name => name !== ''),
      sim_mode: simConfig.sim_mode,
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

    // Remove null values
    Object.keys(newConfig).forEach(key =>
      (newConfig[key] === null || newConfig[key] === "") && delete newConfig[key]
    );

    const requestBody = {
      template: simConfig.template,
      config: newConfig
    };

    var url = `http://${server_ip}:${back_port}/start/`;
    console.log("Request the url to start simulation: ", url);
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
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

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-200 to-red-200 p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-lg p-8">
        <h2 className="text-2xl font-bold mb-6">Start Simulation</h2>
        <form onSubmit={start_sim} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="template">Template:</label>
            <select
              id="template"
              name="template"
              value={simConfig.template}
              onChange={handleInputChange}
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



          {/* <div>
            <label className="block text-sm font-medium mb-1" htmlFor="start_date">Start Date:</label>
            <input
              type="date"
              id="start_date"
              name="start_date"
              value={simConfig.start_date}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="curr_time">Current Time:</label>
            <input
              type="datetime-local"
              id="curr_time"
              name="curr_time"
              value={simConfig.curr_time}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
            />
          </div> */}

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


          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="persona_names">Persona Names:</label>
            <input
              type="text"
              id="persona_names"
              name="persona_names"
              value={simConfig.persona_names}
              onChange={handleInputChange}
              className="w-full p-2 border rounded"
              placeholder="Enter comma-separated names"
            />
          </div>

          <div>
            <label className="block text-sm font-medium mb-1" htmlFor="llm_config">LLM Configuration:</label>
            <select
              id="llm_config"
              name="llm_config"
              value={simConfig.llm_config}
              onChange={(e) => {
                handleInputChange(e);
                setShowLLMConfig(e.target.value === 'custom');
              }}
              className="w-full p-2 border rounded"
            >
              <option value="default">Default Configuration</option>
              <option value="custom">Custom Configuration</option>
            </select>
          </div>

          {showLLMConfig && (
            <div className="space-y-4 mt-4 p-4 border rounded-md bg-gray-50">
              <h3 className="text-lg font-medium">Custom LLM Configuration</h3>
              <div>
                <label className="block text-sm font-medium mb-1" htmlFor="api_base">API Base:</label>
                <input
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
                />
              </div>
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="stream"
                  name="stream"
                  checked={simConfig.stream}
                  onChange={handleInputChange}
                  className="mr-2"
                />
                <label className="text-sm font-medium" htmlFor="stream">Stream</label>
              </div>
            </div>
          )}

          <button
            type="submit"
            className="w-full px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700"
          >
            Start Simulation
          </button>
        </form>
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