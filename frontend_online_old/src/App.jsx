// Imports
import React, { useState, useRef, useEffect, Fragment } from 'react'
import { CheckIcon, ChevronDownIcon } from '@heroicons/react/20/solid'
import { FaCog } from 'react-icons/fa'
import { Menu, MenuItem, MenuItems, Listbox, ListboxButton, ListboxOptions, ListboxOption, MenuButton, Dialog, Transition } from '@headlessui/react'
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

// Constants
const chatTypes = [
  { id: 1, name: 'Command' },
  { id: 2, name: 'Chat' },
]

const users = [
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
  { id: 3, name: 'Bob Johnson' },
]

// Utility Components

// Custom hook for auto-resizing textarea
const useAutoResizeTextArea = (value) => {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      ref.current.style.height = 'auto';
      ref.current.style.height = ref.current.scrollHeight + 'px';
    }
  }, [value]);

  return ref;
};

// AutoResizeTextArea component
const AutoResizeTextArea = ({ value, onChange, placeholder, className }) => {
  const textareaRef = useAutoResizeTextArea(value);

  return (
    <textarea
      ref={textareaRef}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`w-full px-3 py-2 text-gray-700 border rounded-lg focus:outline-none ${className}`}
      rows={1}
      style={{
        resize: 'none',
        minHeight: '2.5rem',
        overflow: 'hidden',
      }}
      onInput={(e) => {
        e.target.style.height = 'auto';
        e.target.style.height = e.target.scrollHeight + 'px';
      }}
    />
  );
};

const PublishEventDialog = ({ isOpen, closeDialog }) => {
  const [description, setDescription] = useState('')
  const [websearch, setWebsearch] = useState('')
  const [policy, setPolicy] = useState('')
  const [accessList, setAccessList] = useState('')

  const handleSubmit = async () => {
    const requestBody = {
      description,
      websearch,
      policy,
      access_list: accessList
    }
    const url = `http://${server_ip}:${back_port}/publish_events/`
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })
      // Handle response
      closeDialog()
    } catch (e) {
      console.log("Publish event failed with error:", e)
    }
  }

  return (
    <Dialog open={isOpen} onClose={closeDialog} className="relative z-50">
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="w-full max-w-md rounded bg-white p-6 shadow-lg">
          <Dialog.Title className="text-lg font-medium leading-6 text-gray-900 mb-4">
            Publish Event
          </Dialog.Title>
          <div className="mt-2 space-y-4">
            <AutoResizeTextArea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Description"
            />
            <AutoResizeTextArea
              value={websearch}
              onChange={(e) => setWebsearch(e.target.value)}
              placeholder="Websearch"
            />
            <AutoResizeTextArea
              value={policy}
              onChange={(e) => setPolicy(e.target.value)}
              placeholder="Policy"
            />
            <AutoResizeTextArea
              value={accessList}
              onChange={(e) => setAccessList(e.target.value)}
              placeholder="Access List"
            />
          </div>
          <div className="mt-4">
            <Button onClick={handleSubmit} className="mr-2">
              Publish
            </Button>
            <Button onClick={closeDialog} variant="secondary">
              Cancel
            </Button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}
const SelectionListbox = ({ value, onChange, options, label }) => (
  <div className='relative flex w-full items-center'>
    <Label className="font-medium whitespace-nowrap mr-2">{label} :</Label>
    <Listbox value={value} onChange={onChange}>
      <ListboxButton className="relative cursor-pointer w-full rounded-md border border-gray-300 bg-white py-1 pl-3 pr-10 text-left shadow-sm focus:outline-none focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm flex items-center">
        {value.name}
        <ChevronDownIcon
          className="absolute pointer-events-none right-1 size-4 fill-white/60"
        />
      </ListboxButton>
      <ListboxOptions anchor="bottom" className="z-10 max-h-60 overflow-auto rounded-md bg-white text-base shadow-lg ring-1 ring-black ring-opacity-15 focus:outline-none sm:text-sm w-[var(--button-width)]">
        {options.map((option) => (
          <ListboxOption
            key={option.id}
            value={option}
            className={({ active, selected }) => `
              relative cursor-default select-none pl-4 pr-4 sm:text-sm
              ${active ? 'bg-indigo-100 text-indigo-900' : 'text-gray-900'}
              ${selected ? 'bg-indigo-200' : ''}
            `}
          >
            {({ selected }) => (
              <div className="py-1">
                <span className={`block truncate ${selected ? 'font-medium' : 'font-normal'}`}>
                  {option.name}
                </span>
                {selected && (
                  <span className="absolute inset-y-0 right-2 flex items-center pl-2 text-indigo-600">
                    <CheckIcon className="h-4 w-4" aria-hidden="true" />
                  </span>
                )}
              </div>
            )}
          </ListboxOption>
        ))}
      </ListboxOptions>
    </Listbox>
  </div>
);

// Icon Components
const SettingsIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="black"
    strokeWidth="2"
  >
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V20a2 2 0 1 1-4 0v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H4a2 2 0 1 1 0-4h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33h.09A1.65 1.65 0 0 0 10 4.09V4a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 .33h.09a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82v.09a1.65 1.65 0 0 0 1 1h.09a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </svg>
)

const LogsIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="black"
    strokeWidth="2"
    strokeLinecap=""
    strokeLinejoin=""
  >
    <rect x="3" y="4" width="18" height="18" rx="0" ry="0" />
    <line x1="9" y1="9" x2="15" y2="9" />
    <line x1="9" y1="13" x2="15" y2="13" />
    <line x1="9" y1="17" x2="15" y2="17" />
  </svg>
)

const RunIcon = (props) => (
  <svg
    {...props}
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="black"
    strokeWidth="2.5"
  >
    <path d="M5 3l14 9-14 9V3z" />
  </svg>
)

const SendIcon = (props) => (
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

// Main App Component
function App() {
  const config_data = import.meta.env
  const server_ip = config_data.VITE_server_ip
  const back_port = config_data.VITE_back_port

  // State
  const [showLogs, setShowLogs] = useState(false)
  const [logs, setLogs] = useState([])
  const [autoScroll, setAutoScroll] = useState(true)
  const [count, setCount] = useState(1)
  const [chatType, setChatType] = useState(chatTypes[0])
  const [selectedUser, setSelectedUser] = useState(users[0])
  const [chatList, setChatList] = useState([])
  const [showSettings, setShowSettings] = useState(false)
  const [isPublishEventDialogOpen, setIsPublishEventDialogOpen] = useState(false)

  // Refs
  const chatBoxRef = useRef(null)
  const chatUserRef = useRef(null)
  const inputRef = useRef(null)
  const logWebSocket = useRef(null)
  const logPanelRef = useRef(null)
  const settingsButtonRef = useRef(null)
  const settingsPopupRef = useRef(null)

  // Functions
  const add_chat = (role, username, content) => {
    setChatList(prevList => [...prevList, { role, username, content }])
  }

  const interact = async () => {
    if (!chatUserRef.current || !inputRef.current) return

    const chat_type = chatUserRef.current.value
    const chat_user = chatUserRef.current.value
    let params, response

    if (chatType.name === 'Chat') {
      const cmd = `call -- analysis ${chat_user}`
      params = new URLSearchParams()
      params.append('command', cmd)
      const url = `http://${server_ip}:${back_port}/command/?${params.toString()}`
      add_chat("admin", "Admin", "Command: " + cmd, false)
      response = await fetch(url, { method: 'GET', mode: 'no-cors' })
    }

    const cmd = inputRef.current.value
    params = new URLSearchParams()
    params.append('command', cmd)
    const url = `http://${server_ip}:${back_port}/command/?${params.toString()}`
    add_chat("admin", "Admin", "Command: " + cmd, false)
    response = await fetch(url, { method: 'GET', mode: 'no-cors' })

    inputRef.current.value = ''
  }



  const handleKeyDown = (event) => {
    if (event.key === 'Enter') {
      interact()
    }
  }

  const handleLogScroll = () => {
    if (!logPanelRef.current) return
    const tolerance = 10
    const isAtBottom =
      logPanelRef.current.scrollHeight - logPanelRef.current.scrollTop <= logPanelRef.current.clientHeight + tolerance
    setAutoScroll(isAtBottom)
  }

  const runCommand = async () => {
    var params = new URLSearchParams()
    params.append('count', count)
    const url = `http://${server_ip}:${back_port}/run/?${params.toString()}`
    try {
      await fetch(url, { method: 'GET', mode: 'no-cors' })
    } catch (e) {
      console.log("Run command failed with error:", e)
    }
  }

  const publishEvent = async () => {
    const requestBody = {
      description: description,
      websearch: websearch,
      policy: policy,
      access_list: access_list
    }
    const url = `http://${server_ip}:${back_port}/publish_events/`;
    try {
      const response = await fetch(
        url, {
        ethod: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      }
      );
    } catch (e) {
      console.log("Publish event failed with error:", e);
    }
  }

  const toggleLogs = () => {
    setShowLogs(!showLogs)
  }

  // Effects
  useEffect(() => {
    if (autoScroll && logPanelRef.current) {
      logPanelRef.current.scrollTop = logPanelRef.current.scrollHeight
    }
  }, [logs])

  useEffect(() => {
    const url = `http://${server_ip}:${back_port}/persona/`
    const xhr = new XMLHttpRequest()
    xhr.open('GET', url, true)
    xhr.responseType = 'json'
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        const personas = xhr.response['personas']
        if (chatUserRef.current) {
          chatUserRef.current.innerHTML = ''
          personas.forEach(persona => {
            const user_option = document.createElement("option")
            user_option.textContent = persona
            chatUserRef.current.appendChild(user_option)
          })
        }
      } else {
        console.error('Request failed with status:', xhr.status)
      }
    }

    xhr.onerror = function () {
      console.error('Request error...')
    }

    xhr.send()

    logWebSocket.current = new WebSocket(`ws://${server_ip}:${back_port}/ws/log`)
    logWebSocket.current.onmessage = (event) => {
      setLogs(prevLogs => [...prevLogs, event.data])
    }

    return () => {
      if (logWebSocket.current) {
        logWebSocket.current.close()
      }
    }
  }, [server_ip, back_port])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (settingsButtonRef.current && !settingsButtonRef.current.contains(event.target) &&
        settingsPopupRef.current && !settingsPopupRef.current.contains(event.target)) {
        setShowSettings(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => {
      document.removeEventListener("mousedown", handleClickOutside)
    }
  }, [])

  useEffect(() => {
    const chatWebSocket = new WebSocket(`ws://${server_ip}:${back_port}/ws/chat`)

    chatWebSocket.onmessage = (event) => {
      const message = JSON.parse(event.data)
      add_chat(message.role, message.name, message.content)
    }

    return () => {
      chatWebSocket.close()
    }
  }, [server_ip, back_port])

  // Render
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
                      className={`rounded-lg p-3 text-sm ${chat.role === 'admin' ? 'bg-blue-500 text-white' : 'bg-gray-300 text-black'}`}
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
              <div className="flex items-center gap-4 w-full ">
                <SelectionListbox
                  value={chatType}
                  onChange={setChatType}
                  options={chatTypes}
                  label="Chat Type"
                  className="w-1/2"
                />
                <SelectionListbox
                  value={selectedUser}
                  onChange={setSelectedUser}
                  options={users}
                  label="Chat User"
                  className="w-1/2"
                />
              </div>
            </div>
            <div className="flex items-center">
              <Input
                className="flex-1"
                id="input"
                placeholder={(chatType.name === 'Chat' ? 'Please input chat content' : 'Please input your command') + "..."}
                onKeyDown={handleKeyDown}
                ref={inputRef}
              />
              <Button className="ml-2" size="sm" variant="primary" onClick={interact}>
                <SendIcon className="h-4 w-4" />
              </Button>
              <div className="relative w-24 ml-2">
                <Input
                  className="pr-10"
                  type="number"
                  value={count}
                  onChange={(e) => setCount(e.target.value)}
                  placeholder="1"
                  min="1"
                />
                <button
                  className="absolute inset-y-0 right-0 flex items-center pr-2"
                  onClick={() => runCommand()}
                >
                  <RunIcon className="h-4 w-4 text-gray-500" />
                </button>
              </div>
              <Button
                className={`ml-2 flex items-center justify-center ${showLogs
                  ? 'bg-gray-300 text-white'
                  : 'bg-white text-gray-300 border-gray-250 border'
                  }`}
                size="sm"
                variant="secondary"
                onClick={toggleLogs}
              >
                <LogsIcon className="h-4 w-4 text-gray-500" />
              </Button>
              <Menu as="div" className="relative ml-auto">
                {({ open }) => (
                  <>
                    <MenuButton className={`flex items-center justify-center ${open ? 'bg-gray-300' : 'bg-white'} text-gray-1000 ml-2 border-gray-300 border p-2 rounded-md`}>
                      <FaCog className="h-4 w-4" />
                    </MenuButton>
                    <MenuItems
                      className="absolute right-0 mt-2 w-48 bg-white shadow-lg border border-gray-300 rounded-lg z-10 overflow-hidden"
                    >
                      <MenuItem>
                        {({ active }) => (
                          <button
                            className={`${active ? 'bg-gray-100' : ''} block w-full text-left px-4 py-2 text-sm`}
                            onClick={() => setIsPublishEventDialogOpen(true)}
                          >
                            Publish events
                          </button>
                        )}
                      </MenuItem>
                      <MenuItem>
                        {({ active }) => (
                          <button
                            className={`${active ? 'bg-gray-100' : ''
                              } block w-full text-left px-4 py-2 text-sm`}
                          >
                            More settings
                          </button>
                        )}
                      </MenuItem>
                    </MenuItems>
                  </>
                )}
              </Menu>
              {showSettings && (
                <div
                  ref={settingsPopupRef}
                  className="absolute right-0 mt-2 w-48 bg-white shadow-lg border border-gray-300 rounded-lg z-10"
                  style={{ top: '100%', right: 0 }}
                >
                  <ul className="py-2">
                    <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">Setting 1</li>
                    <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">Setting 2</li>
                    <li className="px-4 py-2 hover:bg-gray-100 cursor-pointer">Setting 3</li>
                  </ul>
                </div>
              )}
              <PublishEventDialog
                isOpen={isPublishEventDialogOpen}
                closeDialog={() => setIsPublishEventDialogOpen(false)}
              />
            </div>
          </div>
        </div>
        {showLogs && (
          <div
            className="w-1/2 ml-4 border rounded-lg bg-white flex flex-col"
            style={{ maxHeight: '100%' }}
          >
            <div className="p-4 border-b">
              <div className="flex justify-between items-center">
                <h3 className="font-bold">Logs</h3>
                <Button variant="danger" onClick={() => setLogs([])}>
                  Clear Logs
                </Button>
              </div>
            </div>
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
  )
}

export default App