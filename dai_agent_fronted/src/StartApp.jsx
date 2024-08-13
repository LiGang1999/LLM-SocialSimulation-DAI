import logo from './logo.svg';
import './App.css';
import fs from 'fs'
import yaml from 'js-yaml'

/**
 * v0 by Vercel.
 * @see https://v0.dev/t/vWHQ7AzR8lD
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */
function StartApp() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;
  const front_port2 = config_data.VITE_front_port2;
  const start_sim = async () => {

    var fork_name = document.getElementById("fork_sim").value;
    var new_name = document.getElementById("new_sim").value;
    const params = new URLSearchParams();
    params.append('fork', fork_name);
    params.append('new', new_name);
    var url = `http://${server_ip}:${back_port}/start/?${params.toString()}`;
    console.log("Request the url to start simulation: ", url);
    const response = await fetch(url, {
      method: 'GET',
      mode: 'no-cors'
      // body: JSON.stringify({
      //   name: 'John Smith',
      //   job: 'manager',
      // }),
      // headers: {
      // 'Content-Type': 'application/json',
      // Accept: 'application/json',
      // "Access-Control-Allow-Origin": '*'
      // },
    }).then(
      (data) => {
        console.log("response2: ", data)
      }
    );
    // window.location.href = "/act";
    window.location.href = `/act`;
  };
  return (
    <div className="flex flex-col items-center justify-center p-10 space-y-6 bg-white">
      <div className="w-full max-w-md space-y-4">
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium" htmlFor="model">
            Simulation Type:
          </label>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            id="model"
          >
            {/* <option>请选择环境</option> */}
            <option>offline</option>
            <option>online</option>
          </select>
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium" htmlFor="input1">
            Template:
          </label>
          <input
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            id="fork_sim"
            placeholder=""
            type="text"
            value="base_the_ville_isabella_maria_klaus"
          />
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium" htmlFor="input1">
            New Simulation Name:
          </label>
          <input
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            id="new_sim"
            placeholder=""
            type="text"
          />
        </div>
        <div className="flex flex-col space-y-2">
          <label className="text-sm font-medium" htmlFor="temperature">
            LLM:
          </label>
          <select
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            id="model"
          >
            <option>vicuna-13b-v1.5-16k</option>
            <option>llama-2-7b-chat</option>
          </select>
          {/* <inputh
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
            id="temperature"
            placeholder=""
            type="text"
          /> */}
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium" htmlFor="agent">
            Agent:
          </label>
          <div className="flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm">
            <span className="text-sm">Isabella.docx</span>
            <button className="ml-2 text-indigo-600 hover:text-indigo-900" type="button">
              <XIcon className="h-4 w-4" />
            </button>
          </div>
          <button className="p-2 text-white bg-blue-600 rounded-md hover:bg-blue-700" type="button">
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>
        <div className="flex items-center space-x-2">
          <label className="text-sm font-medium" htmlFor="knowledge">
            Knowledge Base:
          </label>
          <div className="flex items-center px-3 py-2 border border-gray-300 rounded-md shadow-sm">
            <span className="text-sm">knowledge.docx</span>
            <button className="ml-2 text-indigo-600 hover:text-indigo-900" type="button">
              <XIcon className="h-4 w-4" />
            </button>
          </div>
          <button className="p-2 text-white bg-blue-600 rounded-md hover:bg-blue-700" type="button">
            <PlusIcon className="h-4 w-4" />
          </button>
        </div>

        <button
          className="w-full px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          type="button"
          onClick={start_sim}
        >
          Start
        </button>
      </div>
    </div>
  )
}

function PlusIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M5 12h14" />
      <path d="M12 5v14" />
    </svg>
  )
}


function XIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M18 6 6 18" />
      <path d="m6 6 12 12" />
    </svg>
  )
}

export default StartApp;
