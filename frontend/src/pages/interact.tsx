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
import { api, apiBaseUrl, apis } from '@/lib/api';
import { ChatMessage, useSimContext } from '@/SimContext';


const ChatMessageBox: React.FC<ChatMessage> = ({ sender, content, timestamp, avatar }) => (
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


const DialogTab: React.FC = () => {
    const { data } = useSimContext();

    return (
        <ScrollArea className="h-[calc(100vh-350px)]">
            {data.publicMessages.map((msg, index) => (
                <ChatMessageBox key={index} {...msg} />
            ))}
        </ScrollArea>
    );
};


const MapTab: React.FC = () => {
    return <div id="phaser-container" />;
};


const AgentStatusCard: React.FC<{ agent: apis.Agent }> = ({ agent }) => {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card className="mb-4">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Avatar>
                        <AvatarImage src={agent.avatar} alt={`${agent.firstName} ${agent.lastName}`} />
                        <AvatarFallback>{agent.firstName[0]}</AvatarFallback>
                    </Avatar>
                    <h3 className="text-lg font-semibold">{`${agent.firstName} ${agent.lastName}`}</h3>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setExpanded(!expanded)}>
                    <MoreHorizontal className="h-4 w-4" />
                </Button>
            </CardHeader>
            <CardContent>
                <p><strong>Age:</strong> {agent.age}</p>
                <p><strong>Lifestyle:</strong> {agent.lifestyle}</p>
                <p><strong>Currently:</strong> {agent.currently}</p>
                {expanded && (
                    <>
                        <p><strong>Memory:</strong> {agent.memory?.join(', ')}</p>
                        <p><strong>Plan:</strong> {agent.plan?.join(', ')}</p>
                        <p><strong>Bibliography:</strong> {agent.bibliography}</p>
                        <p><strong>Innate Traits:</strong> {JSON.stringify(agent.innate)}</p>
                        <p><strong>Learned Traits:</strong> {JSON.stringify(agent.learned)}</p>
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


const AgentStatusTab: React.FC<{ agents: apis.Agent[], fetchAgentStatus: () => void }> = ({ agents, fetchAgentStatus }) => (
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
    const ctx = useSimContext();

    const [logs, setLogs] = useState<string[]>([]);
    const [isRunning, setIsRunning] = useState(false);
    const [privateChatAgent, setPrivateChatAgent] = useState<string>("");


    const addPublicMessage = (message: ChatMessage) => {
        ctx.setData({
            ...ctx.data,
            publicMessages: [...ctx.data.publicMessages, message]
        });
    };

    const addPrivateMessage = (agentName: string, message: ChatMessage) => {
        ctx.setData({
            ...ctx.data,
            privateMessages: {
                ...ctx.data.privateMessages,
                [agentName]: [...(ctx.data.privateMessages[agentName] || []), message]
            }
        });
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
                const message: ChatMessage = JSON.parse(event.data);

                if (message.type === 'public') {
                    addPublicMessage(message);
                } else if (message.type === 'private') {
                    addPrivateMessage(message.sender, message);
                }
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
                            <DialogTab />
                        </TabsContent>
                        <TabsContent value="map" className="flex-grow">
                            <MapTab />
                        </TabsContent>
                        <TabsContent value="ai" className="flex-grow">
                            <AgentStatusTab agents={ctx.data.agents} fetchAgentStatus={fetchAgentStatus} />
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
                                            <AvatarImage src={ctx.data.agents[privateChatAgent].avatar} alt={ctx.data.agents[privateChatAgent].name} />
                                            <AvatarFallback>{ctx.data.agents[privateChatAgent].name[0]}</AvatarFallback>
                                        </Avatar>
                                        <div className="ml-2 text-left">
                                            <h2 className="text-xl font-bold">{ctx.data.agents[privateChatAgent].name}</h2>
                                            {/* <p className="text-sm text-muted-foreground">{ctx.data.agents[privateChatAgent].status}</p> */}
                                        </div>
                                        <ChevronDown className="ml-2" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align='start'>
                                    {ctx.data.currentTemplate && ctx.data.currentTemplate.personas.map((persona: apis.Agent) => (
                                        <DropdownMenuItem key={persona.name} onSelect={() => setPrivateChatAgent(persona.name)}>
                                            <Avatar className="mr-2">
                                                <AvatarImage src={persona.avatar} alt={`${persona.firstName} ${persona.lastName}`} />
                                                <AvatarFallback>{persona.firstName[0]}</AvatarFallback>
                                            </Avatar>
                                            <span>{`${persona.firstName} ${persona.lastName}`}</span>
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>

                            </DropdownMenu>
                        </CardHeader>
                        <CardContent className="flex-grow overflow-hidden">
                            <ScrollArea className="h-[calc(100vh-350px)]">
                                {ctx.data.privateMessages[selectedAgent.name]?.map((msg, index) => (
                                    <ChatMessageBox key={index} {...msg} />
                                )) || (
                                        <p>No private messages with {selectedAgent.name}</p>
                                    )}
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
