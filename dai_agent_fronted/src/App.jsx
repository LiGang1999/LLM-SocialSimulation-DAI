import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

/**
 * v0 by Vercel.
 * @see https://v0.dev/t/TPKUJgBr1Wy
 * Documentation: https://v0.dev/docs#integrating-generated-code-into-your-nextjs-app
 */

import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { DropdownMenuTrigger, DropdownMenuItem, DropdownMenuContent, DropdownMenu } from "@/components/ui/dropdown-menu"
import { Input } from "@/components/ui/input"
import fs from 'fs'
import yaml from 'js-yaml'
import avatar from './avatar.png'

const AvatarImg = () => {
  return (
    <img
      alt="User Avatar"
      className="rounded-full"
      height={40}
      src="avatar.png"
      style={{
        aspectRatio: "40/40",
        objectFit: "cover",
      }}
      width={40}
    />
  )
}

import { useState, useRef, useEffect } from 'react'

function App() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;
  const [chatType, setChatType] = useState('Command');
  const [showLogs, setShowLogs] = useState(false);
  const [logs, setLogs] = useState([]);
  const [autoScroll, setAutoScroll] = useState(true);


  const chatBoxRef = useRef(null);
  const chatUserRef = useRef(null);
  const inputRef = useRef(null);
  const logWebSocket = useRef(null);
  const logPanelRef = useRef(null);
  const [chatList, setChatList] = useState([]);

  function add_chat(role, username, content) {
    setChatList(prevList => [...prevList, { role, username, content }]);
  }

  const interact = async () => {
    if (!chatUserRef.current || !inputRef.current) return;

    const chat_type = chatUserRef.current.value;
    console.log("chat_type: ", chat_type);

    const chat_user = chatUserRef.current.value;
    console.log("chat user: ", chat_user);

    let params, response;

    if (chatType === 'Chat') {
      const cmd = `call -- analysis ${chat_user}`;
      console.log("cmd: ", cmd);
      params = new URLSearchParams();
      params.append('command', cmd);
      const url = `http://${server_ip}:${back_port}/command/?${params.toString()}`;
      add_chat("admin", "Admin", "Command: " + cmd, false);
      response = await fetch(url, {
        method: 'GET',
        mode: 'no-cors'
      });
    }

    const cmd = inputRef.current.value;
    params = new URLSearchParams();
    params.append('command', cmd);
    const url = `http://${server_ip}:${back_port}/command/?${params.toString()}`;
    add_chat("admin", "Admin", "Command: " + cmd, false);
    response = await fetch(url, {
      method: 'GET',
      mode: 'no-cors'
    });

    // Clear the input
    inputRef.current.value = '';
  };

  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      interact();
    }
  };

  const handleLogScroll = () => {
    if (!logPanelRef.current) return;

    const tolerance = 10; // Adjust this value as needed for how lenient the auto-scroll should be
    const isAtBottom =
      logPanelRef.current.scrollHeight - logPanelRef.current.scrollTop <= logPanelRef.current.clientHeight + tolerance;

    setAutoScroll(isAtBottom);
  };


  useEffect(() => {
    if (autoScroll && logPanelRef.current) {
      logPanelRef.current.scrollTop = logPanelRef.current.scrollHeight;
    }
  }, [logs]); // This useEffect will trigger whenever logs change


  useEffect(() => {
    const url = `http://${server_ip}:${back_port}/persona/`;
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        const personas = xhr.response['personas'];
        if (chatUserRef.current) {
          chatUserRef.current.innerHTML = '';
          personas.forEach(persona => {
            const user_option = document.createElement("option");
            user_option.textContent = persona;
            chatUserRef.current.appendChild(user_option);
          });
        }
      } else {
        console.error('Request failed with status:', xhr.status);
      }
    };

    xhr.onerror = function () {
      console.error('Request error...');
    };

    xhr.send();

    // Set up WebSocket connection for logs
    logWebSocket.current = new WebSocket(`ws://${server_ip}:${back_port}/ws/log`);
    logWebSocket.current.onmessage = (event) => {
      setLogs(prevLogs => [...prevLogs, event.data]);
    };

    return () => {
      if (logWebSocket.current) {
        logWebSocket.current.close();
      }
    };
  }, [server_ip, back_port]);

  useEffect(() => {
    const chatWebSocket = new WebSocket(`ws://${server_ip}:${back_port}/ws/chat`);

    chatWebSocket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      add_chat(message.role, message.name, message.content);
    };

    return () => {
      chatWebSocket.close();
    };
  }, [server_ip, back_port]);

  const toggleLogs = () => {
    setShowLogs(!showLogs);
  };

  return (
    <div className="flex flex-col items-center justify-center h-[100vh] w-full bg-gradient-to-br from-blue-200 to-red-200">
      <div className="flex h-[65vh] w-[70vw]">
        <div className="flex-1 flex flex-col border rounded-lg bg-white">
          <div className="flex-1 overflow-auto border-b p-4">
            <div className="space-y-4" id="chatBox" ref={chatBoxRef}>
              {chatList.map((chat, index) => (
                <div
                  key={index}
                  className={`flex ${chat.role === 'admin' ? 'justify-end' : 'justify-start'} items-center gap-3`}
                >
                  {chat.role !== 'admin' && (
                    <img
                      alt="User Avatar"
                      className="rounded-full"
                      height={40}
                      src="user.svg"
                      style={{
                        aspectRatio: "40/40",
                        objectFit: "cover",
                      }}
                      width={40}
                    />
                  )}
                  <div className={`flex flex-col ${chat.role === 'admin' ? 'items-end' : 'items-start'}`}>
                    <div className="font-medium text-sm">{chat.username}</div>
                    <div
                      className={`rounded-lg p-3 text-sm ${chat.role === 'admin' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'
                        }`}
                    >
                      <p>{chat.content}</p>
                    </div>
                  </div>
                  {chat.role === 'admin' && (
                    <img
                      alt="Admin Avatar"
                      className="rounded-full"
                      height={40}
                      src="admin.svg"
                      style={{
                        aspectRatio: "40/40",
                        objectFit: "cover",
                      }}
                      width={40}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>
          <div className="flex flex-col gap-2 border-t p-4">
            <div className="flex items-center gap-2">
              <Label className="font-medium" htmlFor="chat-type">
                Chat Type:
              </Label>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button className="flex-1 justify-between" size="sm" variant="outline">
                    <span>{chatType}</span>
                    <ChevronDownIcon className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent>
                  <DropdownMenuItem onClick={() => setChatType('Command')}>Command</DropdownMenuItem>
                  <DropdownMenuItem onClick={() => setChatType('Chat')}>Chat</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
              <Label className="font-medium" htmlFor="chat-user">
                Chat User:
              </Label>
              <select
                className="block flex-1 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
                id="chat_user"
                ref={chatUserRef}
              >
                <option>John Doe</option>
                <option>Jane Smith</option>
                <option>Bob Johnson</option>
              </select>
            </div>
            <div className="flex items-center">
              <Input
                className="flex-1"
                id="input"
                placeholder={(chatType === 'Chat' ? 'Please input chat content' : 'Please input your command') + "..."}
                onKeyDown={handleKeyDown}
                ref={inputRef}
              />
              <Button className="ml-2" size="sm" variant="primary" onClick={interact}>
                <SendIcon className="h-4 w-4" />
              </Button>
              <Button className="ml-2" size="sm" variant="secondary" onClick={toggleLogs}>
                {showLogs ? 'Hide Logs' : 'Show Logs'}
              </Button>
            </div>
          </div>
        </div>
        {showLogs && (
          <div
            className="w-1/2 ml-4 border rounded-lg bg-white flex flex-col"
            style={{ maxHeight: '100%' }}
          >
            {/* Fixed Title Section */}
            <div className="p-4 border-b">
              <div className="flex justify-between items-center">
                <h3 className="font-bold">Logs</h3>
                <Button variant="danger" onClick={() => setLogs([])}>
                  Clear Logs
                </Button>
              </div>
            </div>

            {/* Scrollable Log Content */}
            <div
              className="flex-1 overflow-auto p-4 custom-scrollbar"
              ref={logPanelRef}
              onScroll={handleLogScroll}
              style={{ fontFamily: 'monospace' }}
            >
              {logs.map((log, index) => (
                <div key={index} className="text-sm mb-1">
                  • {log}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function ChevronDownIcon(props) {
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
      <path d="m6 9 6 6 6-6" />
    </svg>
  )
}

function SendIcon(props) {
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
      <path d="m22 2-7 20-4-9-9-4Z" />
      <path d="M22 2 11 13" />
    </svg>
  )
}

export default App
