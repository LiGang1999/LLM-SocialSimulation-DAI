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

function App() {
  const config_data = import.meta.env;
  const server_ip = config_data.VITE_server_ip;
  const back_port = config_data.VITE_back_port;
  function add_chat(msg, is_start) {
    var chat_box = document.getElementById("chatBox");
    var chat_div = document.createElement("div");
    console.log("add chat in chat box");
    if (is_start) {
    } else {
      chat_div.className = 'flex justify-end items-start gap-3 items-center'

      // create chat_left div
      var chat_left_div = document.createElement("div");
      chat_left_div.className = "flex flex-col items-end";
      
      // create Name div
      var name_div = document.createElement("div");
      name_div.className = "font-medium text-sm";
      name_div.innerHTML = "Admin";
      chat_left_div.appendChild(name_div);

      // create message div
      var mes_div = document.createElement("div");
      mes_div.className = "rounded-lg bg-blue-500 p-3 text-sm text-white";

      var mes_p = document.createElement("p");
      mes_p.innerHTML = msg;
      mes_div.appendChild(mes_p);
      chat_left_div.appendChild(mes_div);

      // create avatar
      var avatar_img = document.createElement("img");
      avatar_img.alt = "User Avatar";
      avatar_img.className = "rounded-full";
      avatar_img.height = 40;
      avatar_img.src = 'admin.svg';
      avatar_img.style = {
        aspectRatio: "40/40",
        objectFit: "cover",
      };
      avatar_img.width = 40;

      chat_div.appendChild(chat_left_div);
      chat_div.appendChild(avatar_img);
    }
    chat_box.appendChild(chat_div);
  }

  const interact = async () => {
    var chat_type = document.getElementById("chat_type").value;
    console.log("chat_type: ", chat_type)
    var chat_user = document.getElementById("chat_user").value;
    console.log("chat user: ", chat_user)
    var params, response;
    if (chat_type == 'Chat') {
      // open the conversion to chat user
      var cmd = `call -- analysis ${chat_user}`
      console.log("cmd: ", cmd)
      params = new URLSearchParams();
      params.append('command', cmd);
      var url = `http://${server_ip}:${back_port}/command/?${params.toString()}`;
      add_chat("Command: " + cmd, false);
      response = await fetch(url, {
        method: 'GET',
        mode: 'no-cors'
      });
    }

    var cmd = document.getElementById("input").value;
    params = new URLSearchParams();
    params.append('command', cmd);
    var url = `http://${server_ip}:${back_port}/command/?${params.toString()}`;
    add_chat("Command: " + cmd, false);
    response = await fetch(url, {
      method: 'GET',
      mode: 'no-cors'
    });
  };

  // add agent name in chat user list
  var url = `http://${server_ip}:${back_port}/persona/`;
  var xhr = new XMLHttpRequest();
  xhr.open('GET', url, true);
  xhr.responseType = 'json';
  xhr.onload = function() {
      if (xhr.status >= 200 && xhr.status < 300) {
          // 请求成功
          console.log('Response:', xhr.response['personas']);
          var personas = xhr.response['personas'];
          var chat_user = document.getElementById("chat_user");
          chat_user.innerHTML = '';
          for (var i = 0; i < personas.length; i++) {
            console.log("person: ", personas[i])
            var user_option = document.createElement("option");
            user_option.textContent = personas[i];
            chat_user.appendChild(user_option)
          }
      } else {
          // 请求失败
          console.error('Request failed with status:', xhr.status);
      }
  };

  xhr.onerror = function() {
      // 请求过程中发生错误
      console.error('Request error...');
  };

  xhr.send();

  return (
    <div className="flex flex-col items-center justify-center h-[100vh] w-full bg-gradient-to-br from-blue-200 to-red-200">
    <div className="flex h-[65vh] w-[70vw] flex-col border rounded-lg bg-white">
      <div className="flex-1 overflow-auto border-b p-4">
        <div className="space-y-4" id="chatBox">
          <div className="flex justify-end items-start gap-3 items-center">
            <div className="flex flex-col items-end">
              <div className="font-medium text-sm">Admin</div>
              <div className="rounded-lg bg-blue-500 p-3 text-sm text-white">
                <p>Please begin your conversation.</p>
              </div>
            </div>
            <img
              alt="User Avatar"
              className="rounded-full"
              height={40}
              src="admin.svg"
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
          <select
            className="block flex-1 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            id="chat_type"
          >
            <option>Command</option>
            <option>Chat</option>
          </select>
          <Label className="font-medium" htmlFor="chat-user">
            Chat User:
          </Label>
          <select
            className="block flex-1 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm"
            id="chat_user"
          >
            <option>John Doe</option>
            <option>Jane Smith</option>
            <option>Bob Jonhnson</option>
          </select>
        </div>
        <div className="flex items-center">
          <Input className="block flex-1 px-3 py-1 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500" id="input" placeholder="Type your message..." />
          <Button className="ml-2" size="sm" onClick={interact}>
            <SendIcon className="h-4 w-4" />
          </Button>
        </div>
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
