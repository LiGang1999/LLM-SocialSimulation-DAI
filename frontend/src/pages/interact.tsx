import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ChevronDown, Send, MapPin, MessageSquare, Bot, FileText, Clock, Image, Paperclip, Trash2, MoreHorizontal, RefreshCw } from 'lucide-react';
import { api, apiBaseUrl } from '@/lib/api';

interface Agent {
    name: string;
    avatar: string;
    status: 'Online' | 'Offline' | 'Away';
}

interface ChatMessage {
    sender: 'user' | 'agent';
    content: string;
    timestamp: string;
    avatar: string;
}

const ChatMessage: React.FC<ChatMessage> = ({ sender, content, timestamp, avatar }) => (
    <div className={`flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4 items-end`}>
        {sender !== 'user' && (
            <Avatar className="mr-2">
                <AvatarImage src={avatar} alt={sender} />
                <AvatarFallback>{sender[0].toUpperCase()}</AvatarFallback>
            </Avatar>
        )}
        <div className={`max-w-[70%] ${sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'} rounded-lg p-3`}>
            <p className="text-sm">{content}</p>
            <span className="text-xs text-muted-foreground">{timestamp}</span>
        </div>
        {sender === 'user' && (
            <Avatar className="ml-2">
                <AvatarImage src={avatar} alt={sender} />
                <AvatarFallback>U</AvatarFallback>
            </Avatar>
        )}
    </div>
);

const StatusBar: React.FC<{ isRunning: boolean }> = ({ isRunning }) => {
    const [currentTime, setCurrentTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <div className="flex justify-between items-center bg-secondary p-2 rounded-md mt-4">
            <div className="flex items-center">
                <Clock className="h-4 w-4 mr-1" />
                <span className="text-sm">{currentTime.toLocaleTimeString()}</span>
            </div>
            {isRunning && (
                <div className="flex items-center space-x-2 flex-grow mx-16">
                    <span className="text-sm text-nowrap ">仿真正在运行，请稍等...</span>
                    <div className="w-full bg-primary/20 rounded-full h-2 overflow-hidden">
                        <div
                            className="bg-primary h-full rounded-full animate-stripe"
                            style={{
                                backgroundImage: 'linear-gradient(45deg, rgba(255,255,255,.30) 25%, transparent 25%, transparent 50%, rgba(255,255,255,.30) 50%, rgba(255,255,255,.30) 75%, transparent 75%, transparent)',
                                backgroundSize: '1rem 1rem',
                                width: '100%'
                            }}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};


const DialogTab: React.FC<{ messages: ChatMessage[] }> = ({ messages }) => (
    <ScrollArea className="h-[calc(100vh-350px)]">
        {messages.map((msg, index) => (
            <ChatMessage key={index} {...msg} />
        ))}
    </ScrollArea>
);

const MapTab: React.FC = () => {
    return <div id="phaser-container" />;
};

interface AgentStatus {
    name: string;
    avatar: string;
    personality: string;
    memory: string;
    currentDoing: string;
    plan: string;
}

const AgentStatusCard: React.FC<{ agent: AgentStatus }> = ({ agent }) => {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card className="mb-4">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Avatar>
                        <AvatarImage src={agent.avatar} alt={agent.name} />
                        <AvatarFallback>{agent.name[0]}</AvatarFallback>
                    </Avatar>
                    <h3 className="text-lg font-semibold">{agent.name}</h3>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setExpanded(!expanded)}>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </CardHeader>
            <CardContent>
                <p><strong>Personality:</strong> {agent.personality}</p>
                <p><strong>Current Task:</strong> {agent.currentDoing}</p>
                {expanded && (
                    <>
                        <p><strong>Memory:</strong> {agent.memory}</p>
                        <p><strong>Plan:</strong> {agent.plan}</p>
                    </>
                )}
            </CardContent>
            {expanded && (
                <CardFooter>
                    <Button variant="outline" size="sm" className="w-full">
                        查看全部信息
                    </Button>
                </CardFooter>
            )}
        </Card>
    );
};

const AgentStatusTab: React.FC<{ agents: AgentStatus[], fetchAgentStatus: () => void }> = ({ agents, fetchAgentStatus }) => (
    <>
        <div className="flex justify-end mb-4">
            <Button onClick={fetchAgentStatus}>
                <RefreshCw className="mr-2 h-4 w-4" />
                Refresh
            </Button>
        </div>
        <ScrollArea className="h-[calc(100vh-400px)]">
            {agents.map((agent, index) => (
                <AgentStatusCard key={index} agent={agent} />
            ))}
        </ScrollArea>
    </>
);


const LogTab: React.FC<{ logs: string[], addLog: (log: string) => void, clearLogs: () => void }> = ({ logs, addLog, clearLogs }) => {
    const [command, setCommand] = useState('');

    const handleCommand = () => {
        addLog(`> ${command}`);
        // Process command here
        setCommand('');
    };

    return (
        <div className="flex-col">
            <ScrollArea className="font-mono text-sm h-[calc(100vh-250px)]">
                {logs.map((log, index) => (
                    <div key={index}>{log}</div>
                ))}
            </ScrollArea>
            <div className="flex mt-4 ">
                <Input
                    value={command}
                    onChange={(e) => setCommand(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleCommand()}
                    placeholder="Enter command..."
                    className="flex-grow"
                />
                <Button onClick={handleCommand} className="ml-2">
                    <Send className="h-4 w-4 mr-2" />
                    Send
                </Button>
                <Button onClick={clearLogs} variant="outline" className="ml-2">
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear
                </Button>
            </div>
        </div>
    );
};

export const InteractPage: React.FC = () => {
    const [selectedAgent, setSelectedAgent] = useState<Agent>({
        name: "不加咖啡的奶茶",
        avatar: "/api/placeholder/32/32",
        status: "Online"
    });

    const [messages, setMessages] = useState<ChatMessage[]>([
        { sender: 'agent', content: '你好!很近如何?', timestamp: '15:22', avatar: "/api/placeholder/32/32" },
        { sender: 'user', content: '下周我有一场新工作面试,你有什么建议吗?', timestamp: '15:22', avatar: "/api/placeholder/32/32" },
        { sender: 'agent', content: '完美的!我很高兴为你提供一些建议。', timestamp: '15:22', avatar: "/api/placeholder/32/32" },
    ]);

    const [agentStatus, setAgentStatus] = useState<AgentStatus[]>([
        {
            name: "Agent 1",
            avatar: "/api/placeholder/32/32",
            personality: "Friendly and helpful",
            memory: "Remembers recent conversations",
            currentDoing: "Assisting with customer inquiries",
            plan: "Improve response time and accuracy"
        },
        // Add more agents as needed
    ]);

    const [logs, setLogs] = useState<string[]>([]);
    const [isRunning, setIsRunning] = useState(false);

    const agents: Agent[] = [
        { name: "不加咖啡的奶茶", avatar: "/api/placeholder/32/32", status: "Online" },
        { name: "Agent 2", avatar: "/api/placeholder/32/32", status: "Offline" },
        { name: "Agent 3", avatar: "/api/placeholder/32/32", status: "Away" },
    ];

    const addChat = (sender: 'user' | 'agent', content: string) => {
        const newMessage: ChatMessage = {
            sender,
            content,
            timestamp: new Date().toLocaleTimeString(),
            avatar: sender === 'user' ? "/api/placeholder/32/32" : selectedAgent.avatar
        };
        setMessages(prevMessages => [...prevMessages, newMessage]);
    };

    const addLog = (log: string) => {
        setLogs(prevLogs => [...prevLogs, log]);
    };

    const clearLogs = () => {
        setLogs([]);
    };

    const fetchAgentStatus = async () => {
        try {
            const response = await api.get('/agentStatus');
            setAgentStatus(response.data);
        } catch (error) {
            console.error('Error fetching agent status:', error);
        }
    };

    useEffect(() => {
        fetchAgentStatus();
    }, []);

    const [chatSocket, setChatSocket] = useState<WebSocket | null>(null);
    const [logSocket, setLogSocket] = useState<WebSocket | null>(null);

    useEffect(() => {
        // Create WebSocket connections when the component mounts
        const newChatSocket = new WebSocket('ws://your-chat-websocket-url');
        const newLogSocket = new WebSocket('ws://your-log-websocket-url');

        // Update state with the new WebSocket instances
        setChatSocket(newChatSocket);
        setLogSocket(newLogSocket);

        // Clean up WebSocket connections when the component unmounts
        return () => {
            newChatSocket.close();
            newLogSocket.close();
        };
    }, []);

    useEffect(() => {
        if (chatSocket) {
            // Listen for messages from the chat WebSocket
            chatSocket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                addChat(message.sender, message.content);
            };
        }
    }, [chatSocket]);

    useEffect(() => {
        if (logSocket) {
            // Listen for messages from the log WebSocket
            logSocket.onmessage = (event) => {
                const log = JSON.parse(event.data);
                addLog(log.message);
            };
        }
    }, [logSocket]);

    return (
        <div className="flex flex-col min-h-screen bg-background">
            <Navbar />
            <div className="container flex w-full mx-auto mt-4 mb-4 px-4 flex-grow">
                {/* Left panel with tabs and status bar */}
                <div className="w-2/3 pr-4 flex flex-col">
                    <Tabs defaultValue="map" className="w-full flex-grow"
                        onValueChange={(value) => value === 'ai' && fetchAgentStatus()}
                    >
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="dialog"><MessageSquare className="mr-2 h-4 w-4" />对话</TabsTrigger>
                            <TabsTrigger value="map"><MapPin className="mr-2 h-4 w-4" />地图</TabsTrigger>
                            <TabsTrigger value="ai"><Bot className="mr-2 h-4 w-4" />智能体状态</TabsTrigger>
                            <TabsTrigger value="log"><FileText className="mr-2 h-4 w-4" />日志</TabsTrigger>
                        </TabsList>
                        <TabsContent value="dialog" className="flex-grow">
                            <DialogTab messages={messages} />
                        </TabsContent>
                        <TabsContent value="map" className="flex-grow">
                            <MapTab />
                        </TabsContent>
                        <TabsContent value="ai" className="flex-grow">
                            <AgentStatusTab agents={agentStatus} fetchAgentStatus={fetchAgentStatus} />
                        </TabsContent>
                        <TabsContent value="log" className="flex-grow">
                            <LogTab logs={logs} addLog={addLog} clearLogs={clearLogs} />
                        </TabsContent>
                    </Tabs>
                    <StatusBar isRunning={true} />
                </div>

                {/* Right panel with chat */}
                <div className="w-1/3 pl-4">
                    <Card className="h-full flex flex-col">
                        <CardHeader className="flex flex-row items-center space-x-4 pb-6 mb-6 border-b border-b-gray-300">
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" className="p-0 hover:bg-transparent">
                                        <Avatar>
                                            <AvatarImage src={selectedAgent.avatar} alt={selectedAgent.name} />
                                            <AvatarFallback>{selectedAgent.name[0]}</AvatarFallback>
                                        </Avatar>
                                        <div className="ml-2 text-left">
                                            <h2 className="text-xl font-bold">{selectedAgent.name}</h2>
                                            <p className="text-sm text-muted-foreground">{selectedAgent.status}</p>
                                        </div>
                                        <ChevronDown className="ml-2" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align='start'>
                                    {agents.map((agent) => (
                                        <DropdownMenuItem key={agent.name} onSelect={() => setSelectedAgent(agent)}>
                                            <Avatar className="mr-2">
                                                <AvatarImage src={agent.avatar} alt={agent.name} />
                                                <AvatarFallback>{agent.name[0]}</AvatarFallback>
                                            </Avatar>
                                            <span>{agent.name}</span>
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </CardHeader>
                        <CardContent className="flex-grow overflow-hidden">
                            <ScrollArea className="h-[calc(100vh-350px)]">
                                {messages.map((msg, index) => (
                                    <ChatMessage key={index} {...msg} />
                                ))}
                            </ScrollArea>
                        </CardContent>
                        <CardFooter className="p-4 flex-col">
                            <div className="flex w-full justify-start space-x-2 mb-2">
                                <Button size="sm" variant="outline">
                                    <Image className="h-4 w-4 mr-1" />
                                    发布事件
                                </Button>
                                <Button size="sm" variant="outline" onClick={() => setIsRunning(!isRunning)}>
                                    {isRunning ? '停止模拟' : '模拟1轮'}
                                </Button>
                                <Button size="sm" variant="outline">
                                    9999
                                </Button>
                            </div>
                            <div className="flex w-full items-center space-x-2">
                                <Button size="icon" variant="outline">
                                    <Paperclip className="h-4 w-4" />
                                </Button>
                                <Input className="flex-grow" placeholder="说点什么..." />
                                <Button onClick={() => addChat('user', 'Test message')}>
                                    <Send className="h-4 w-4" />
                                </Button>
                            </div>
                        </CardFooter>
                    </Card>
                </div>
            </div>
        </div>
    );
};
