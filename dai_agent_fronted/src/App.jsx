import { useState } from 'react'
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

function App() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;
  const interact = async () => {

    var input = document.getElementById("input").value;
    const params = new URLSearchParams();
    params.append('command', input);
    var url = `http://${server_ip}:${back_port}/command/?${params.toString()}`;
    const response = await fetch(url, {
      method: 'GET',
      mode: 'no-cors'
    });
  };
  return (
    <div className="flex h-screen flex-col">
      <div className="flex-1 overflow-auto border-b p-4">
        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <img
              alt="User Avatar"
              className="rounded-full"
              height={40}
              src="/avatar.png"
              style={{
                aspectRatio: "40/40",
                objectFit: "cover",
              }}
              width={40}
            />
            <div className="rounded-lg bg-gray-100 p-3 text-sm dark:bg-gray-800">
              <p>Hi there! How can I help you today?</p>
            </div>
          </div>
          <div className="flex justify-end items-start gap-3">
            <div className="rounded-lg bg-blue-500 p-3 text-sm text-white">
              <p>Hello! I have a few questions about your product.</p>
            </div>
            <img
              alt="User Avatar"
              className="rounded-full"
              height={40}
              src="avatar2.png"
              style={{
                aspectRatio: "40/40",
                objectFit: "cover",
              }}
              width={40}
            />
          </div>
          <div className="flex items-start gap-3">
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
            <div className="rounded-lg bg-gray-100 p-3 text-sm dark:bg-gray-800">
              <p>Sure, I'd be happy to answer your questions. What would you like to know?</p>
            </div>
          </div>
          <div className="flex justify-end items-start gap-3">
            <div className="rounded-lg bg-blue-500 p-3 text-sm text-white">
              <p>I'm interested in the pricing and features of your product. Can you provide more details?</p>
            </div>
            <img
              alt="User Avatar"
              className="rounded-full"
              height={40}
              src="avatar2.png"
              style={{
                aspectRatio: "40/40",
                objectFit: "cover",
              }}
              width={40}
            />
          </div>
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
                <span>Command</span>
                <ChevronDownIcon className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem>Chat</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Label className="font-medium" htmlFor="chat-user">
            Chat User:
          </Label>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button className="flex-1 justify-between" size="sm" variant="outline">
                <span>John Doe</span>
                <ChevronDownIcon className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem>John Doe</DropdownMenuItem>
              <DropdownMenuItem>Jane Smith</DropdownMenuItem>
              <DropdownMenuItem>Bob Johnson</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <div className="flex items-center">
          <Input className="flex-1" id="input" placeholder="Type your message..." />
          <Button className="ml-2" size="sm" variant="primary" onClick={interact}>
            <SendIcon className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
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
