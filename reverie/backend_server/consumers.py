# consumers.py
import json
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
import asyncio
import subprocess


class LogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "console_log"
        print("connecting..")
        await self.accept()
        # self.watch_log_and_send()
        # 启动一个进程来监听日志输出，并将其发送到 WebSocket 连接
        # async_to_sync(self.channel_layer.group_add)(
        #     self.room_name,
        #     self.channel_name
        # )
        print("connected")
        self.proc = await asyncio.create_subprocess_exec(
            "tail", "-f", "stdout.log", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        await self.watch_log_and_send()
        # print("watch log and send")
        # self.proc = subprocess.Popen(['tail', '-f', 'stdout.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # while True:
        #     line = self.proc.stdout.readline().decode('utf-8')
        #     print("line: ", line)
        #     if not line:
        #         break
        #     self.send(text_data=json.dumps({'message': line}))
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name,
        #     {
        #         'type': 'watch_log_and_send',
        #         'message': none
        #     }
        # )
        # self.task = asyncio.create_task(self.watch_log_and_send())
        # while True:
        #     a = 2 + 8
        # self.send(text_data=json.dumps({"text": "Hey, slow it down"}, ensure_ascii=False))

    async def watch_log_and_send(self):
        print("watch log and send")
        # self.proc = subprocess.Popen(['tail', '-f', 'stdout.log'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        while True:
            # line = self.proc.stdout.readline().decode('utf-8')
            line = await self.proc.stdout.readline()
            # print("line: ", line)
            if not line:
                break
            await self.send(text_data=json.dumps({"message": line.decode("utf-8")}))
            # print("send success")

    async def disconnect(self, close_code):
        pass
        # async_to_sync(self.channel_layer.group_discard)(
        #     self.room_group_name,
        #     self.channel_name
        # )

    # async def send_message(self, event):
    #     print("send_message: ", event["message"])
    #     await self.send(text_data=json.dumps({
    #         "message": event["message"]
    #     }))
