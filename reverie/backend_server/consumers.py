# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio
import subprocess
from reverie import online_relation
from threading import Thread
import time

class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'console_log'
        print("connecting..")
        await self.accept()
        print("connected")
        self.proc = await asyncio.create_subprocess_exec(
            'tail', '-f', 'stdout.log',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        await self.watch_log_and_send()
    
    async def watch_log_and_send(self):
        print("watch log and send")
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            await self.send(text_data=json.dumps({'message': line.decode('utf-8')}))
    
    async def disconnect(self, close_code):
        pass

class OnlineConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.thread = Thread(target=self.get_online)
        self.thread.daemon = True
        self.thread.start()
        
    async def connect(self):
        print("online connecting..")
        await self.accept()
        print("online connected")
    
    def get_online(self):
        print("online - watch log and send")
        while True:
            if not online_relation.empty():
                line = online_relation.get()
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(self.send(text_data=json.dumps({'message': line})))
                except Exception as e:
                    print("error: ", e)
            time.sleep(1)

    async def disconnect(self, close_code):
        pass