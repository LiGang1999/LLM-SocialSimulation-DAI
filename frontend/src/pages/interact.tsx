import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectItem, SelectTrigger, SelectValue, SelectContent } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ChevronDown, Send, MapPin, MessageSquare, Bot, FileText, Clock, Image, Paperclip, Trash2, MoreHorizontal, RefreshCw } from 'lucide-react';
import { apis } from '@/lib/api';
import { ChatMessage, useSimContext } from '@/SimContext';
import { RandomAvatar } from '@/components/Avatars';


const ChatMessageBox: React.FC<ChatMessage> = ({ sender, content, timestamp, subject }) => (
    <div className={`flex ${sender === 'user' ? 'justify-end' : 'justify-start'} mb-4 items-start`}>
        {sender !== 'user' && (
            <Avatar className="mr-2 mt-1">
                <RandomAvatar name={sender} className='h-8 w-8' />
            </Avatar>
        )}
        <div className={`max-w-[70%] ${sender === 'user' ? 'bg-primary text-primary-foreground' : 'bg-secondary'} rounded-lg p-3`}>
            {sender !== 'user' && (
                <p className="text-xs font-semibold mb-1">
                    {sender}
                    {subject && <span className="text-muted-foreground"> about <span className="font-normal italic">{subject}</span></span>}
                </p>
            )}
            <p className="text-sm">{content}</p>
            <span className="text-xs text-muted-foreground block mt-1">{timestamp}</span>
        </div>
        {sender === 'user' && (
            <Avatar className="ml-2 mt-1">
                <RandomAvatar name="Administrator" className='h-8 w-8' />
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


// Update DialogTab to accept messages as a prop
const DialogTab: React.FC<{ messages: ChatMessage[] }> = ({ messages }) => {
    return (
        <ScrollArea className="h-[calc(100vh-200px)] border-4 border-gray-100 rounded-md pl-2">
            {messages.map((msg, index) => (
                <ChatMessageBox key={index} {...msg} />
            ))}
        </ScrollArea>
    );
};


const MapTab: React.FC = () => {
    return <div id="phaser-container" />;
};


const AgentStatusCard: React.FC<{ agent: apis.Agent, onViewFullInfo: (agentName: string) => void }> = ({ agent, onViewFullInfo }) => {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card className="mb-4">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-4">
                    <Avatar>
                        <RandomAvatar name={`${agent.first_name} ${agent.last_name}`} />
                    </Avatar>
                    <h3 className="text-lg font-semibold">{`${agent.first_name} ${agent.last_name}`}</h3>
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
                        <p><strong>Innate Traits:</strong> {agent.innate}</p>
                        <p><strong>Learned Traits:</strong> {agent.learned}</p>
                    </>
                )}
            </CardContent>
            {expanded && (
                <CardFooter>
                    <Button variant="outline" size="sm" className="w-full" onClick={() => onViewFullInfo(agent.name)}>
                        查看全部信息
                    </Button>
                </CardFooter>
            )}
        </Card>
    );
};

const AgentStatusTab: React.FC = () => {
    const [agents, setAgents] = useState<apis.Agent[]>([]);
    const [selectedAgent, setSelectedAgent] = useState<apis.Agent | null>(null);

    const { data } = useSimContext();

    const fetchAgentStatus = async () => {
        const agentsInfo = await apis.agentsInfo(data.currSimCode || "");
        setAgents(agentsInfo);
    };

    useEffect(() => {
        fetchAgentStatus();
    }, []);

    const handleViewFullInfo = async (agentName: string) => {
        try {
            const agentDetail = await apis.agentDetail(data.currSimCode || "", agentName);
            setSelectedAgent(agentDetail);
        } catch (error) {
            console.error('Error fetching agent detail:', error);
            // Handle error (e.g., show an error message to the user)
        }
    };

    return (
        <>
            <div className="flex justify-end mb-4">
                <Button onClick={fetchAgentStatus}>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>
            <ScrollArea className="h-[calc(100vh-400px)]">
                {agents.map((agent, index) => (
                    <AgentStatusCard key={index} agent={agent} onViewFullInfo={handleViewFullInfo} />
                ))}
            </ScrollArea>
            {selectedAgent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                    <Card className="w-2/3 max-h-[80vh] overflow-y-auto">
                        <CardHeader>
                            <h2 className="text-2xl font-bold">{selectedAgent.name} - Full Information</h2>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p><strong>Name:</strong> {selectedAgent.name}</p>
                                    <p><strong>First Name:</strong> {selectedAgent.first_name}</p>
                                    <p><strong>Last Name:</strong> {selectedAgent.last_name}</p>
                                    <p><strong>Age:</strong> {selectedAgent.age}</p>
                                    <p><strong>Daily Plan Requirement:</strong> {selectedAgent.daily_plan_req}</p>
                                    <p><strong>Innate Traits:</strong> {selectedAgent.innate}</p>
                                    <p><strong>Learned Traits:</strong> {selectedAgent.learned}</p>
                                    <p><strong>Currently:</strong> {selectedAgent.currently}</p>
                                    <p><strong>Lifestyle:</strong> {selectedAgent.lifestyle}</p>
                                    <p><strong>Living Area:</strong> {selectedAgent.living_area}</p>
                                </div>
                                <div>
                                    <p><strong>Current Time:</strong> {selectedAgent.curr_time}</p>
                                    <p><strong>Current Tile:</strong> {selectedAgent.curr_tile}</p>
                                    <p><strong>Daily Requirements:</strong> {selectedAgent.daily_req?.join(', ')}</p>
                                    <p><strong>Daily Schedule:</strong> {selectedAgent.f_daily_schedule?.join(', ')}</p>
                                    <p><strong>Hourly Schedule:</strong> {selectedAgent.f_daily_schedule_hourly_org?.join(', ')}</p>
                                    <p><strong>Current Activity:</strong> {selectedAgent.act_description}</p>
                                    <p><strong>Activity Start Time:</strong> {selectedAgent.act_start_time}</p>
                                    <p><strong>Activity Duration:</strong> {selectedAgent.act_duration}</p>
                                    <p><strong>Chatting With:</strong> {selectedAgent.chatting_with}</p>
                                    <p><strong>Chatting End Time:</strong> {selectedAgent.chatting_end_time}</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <p><strong>Memory:</strong> {selectedAgent.memory?.join(', ')}</p>
                                <p><strong>Plan:</strong> {selectedAgent.plan?.join(', ')}</p>
                                <p><strong>Bibliography:</strong> {selectedAgent.bibliography}</p>
                                <p><strong>Current Event:</strong> {selectedAgent.act_event?.join(', ')}</p>
                                <p><strong>Planned Path:</strong> {selectedAgent.planned_path?.join(' → ')}</p>
                            </div>
                        </CardContent>
                        <CardFooter>
                            <Button onClick={() => setSelectedAgent(null)}>Close</Button>
                        </CardFooter>
                    </Card>
                </div>
            )}
        </>
    );
};


const LogTab: React.FC<{ logs: string[], addLog: (log: string) => void, clearLogs: () => void, setIsRunning: (isRunning: boolean) => void }> = ({ logs, addLog, clearLogs, setIsRunning }) => {
    const [command, setCommand] = useState('');

    const handleCommand = async () => {
        setIsRunning(true);
        addLog(`> ${command}`);
        // Process command here
        await apis.sendCommand(command);
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

    const [isRunning, setIsRunning] = useState(true);
    const [privateChatAgent, setPrivateChatAgent] = useState<string>("");
    const [simRounds, setSimRounds] = useState<number>(1);

    // New state for messages
    const [publicMessages, setPublicMessages] = useState<ChatMessage[]>([]);
    const [privateMessages, setPrivateMessages] = useState<Record<string, ChatMessage[]>>({});

    const addPublicMessage = (message: ChatMessage) => {
        setPublicMessages(prevMessages => [...prevMessages, message]);
    };

    const addPrivateMessage = (agentName: string, message: ChatMessage) => {
        setPrivateMessages(prevMessages => ({
            ...prevMessages,
            [agentName]: [...(prevMessages[agentName] || []), message]
        }));
    };


    const addLog = (log: string) => {
        setLogs(prevLogs => [...prevLogs, log]);
    };

    const clearLogs = () => {
        setLogs([]);
    };

    const handleRunSimulation = async (rounds: number) => {
        try {
            setIsRunning(true);
            await apis.runSim(rounds);
        } catch (error) {
            console.error("Error running simulation:", error);
            // Handle the error, e.g., show an error message to the user
        } finally {
            setIsRunning(false);
        }
    };

    useEffect(() => {
        const checkStatus = async () => {
            const status = await apis.queryStatus();
            setIsRunning(status === 'running');
        };

        // Check status immediately on mount
        checkStatus();

        // Set up interval to check status
        const intervalId = setInterval(checkStatus, 500); // Check every 5 seconds

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, []);


    useEffect(() => {
        console.log('Entering interact page')
        // console.log(Object.keys(ctx.data.agents).length)
        if (!ctx.data.agents || Object.keys(ctx.data.agents).length === 0) {
            const personasObject = (ctx.data.currentTemplate?.personas || []).reduce((acc, persona) => {
                if (persona.name) {
                    acc[persona.name] = persona;
                }
                return acc;
            }, {} as Record<string, any>);

            const updatedData = {
                ...ctx.data,
                agents: personasObject
            };

            ctx.setData(updatedData);

            // console.log(ctx.data.agents)
            // console.log(personasObject)

            // Set the privateChatAgent to the first agent's name
            if (Object.keys(personasObject).length > 0) {
                setPrivateChatAgent(Object.keys(personasObject)[0]);
            }
        } else if (privateChatAgent === "" && Object.keys(ctx.data.agents).length > 0) {
            // If agents already exist but privateChatAgent is not set, set it to the first agent
            setPrivateChatAgent(Object.keys(ctx.data.agents)[0]);
        }

        console.log(ctx.data)

    }, [ctx.data.currentTemplate, ctx.data.agents]);

    const [chatSocket, setChatSocket] = useState<WebSocket | null>(null);
    const [logSocket, setLogSocket] = useState<WebSocket | null>(null);

    useEffect(() => {
        // Create WebSocket connections when the component mounts
        const newChatSocket = apis.chatSocket();
        const newLogSocket = apis.logSocket();

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
            logSocket.onmessage = (event) => {
                console.log("Receive log data!!!")
                console.log(event.data)
                addLog(`• ${event.data}`);
            };
        }
    }, [logSocket]);


    // console.log(ctx.data)
    // const currentAgent = ctx.data.agents[privateChatAgent];


    const ChatFooter: React.FC<{ simCode: string, agentName: string }> = ({ simCode, agentName }) => {
        const [message, setMessage] = useState('');
        const [chatType, setChatType] = useState<'whisper' | 'analysis'>('whisper');

        const handleSendMessage = async () => {
            if (message.trim()) {
                try {
                    setIsRunning(true);
                    const response = await apis.privateChat(simCode, agentName, chatType, privateMessages[agentName], message);
                    // Handle the response, e.g., update the chat messages
                    console.log(response);
                    // Clear the input after sending
                    setMessage('');
                } catch (error) {
                    console.error("Error sending private chat:", error);
                    // Handle the error, e.g., show an error message to the user
                }
            }
        };

        return (
            <CardFooter className="p-4 flex-col">
                <div className="flex w-full justify-start space-x-2 mb-2">
                    <Button size="sm" variant="outline">
                        <Image className="h-4 w-4 mr-1" />
                        发布事件
                    </Button>
                    <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleRunSimulation(1)}
                        disabled={isRunning}
                    >
                        {isRunning ? '模拟中...' : '模拟1轮'}
                    </Button>
                    <div className="flex items-center space-x-1">

                        <Button
                            size="sm"
                            variant="outline"
                            onClick={() => { if (!isRunning) handleRunSimulation(simRounds) }}
                            disabled={isRunning}
                        >
                            {isRunning ? '模拟中...' : `模拟${simRounds}轮`}
                        </Button>
                        <Input
                            type="number"
                            value={simRounds}
                            onChange={(e) => setSimRounds(Math.max(1, parseInt(e.target.value) || 1))}
                            className="w-16 h-8"
                            min="1"
                        />
                    </div>
                </div>
                <div className="flex w-full items-center space-x-2">
                    <Button size="icon" variant="outline">
                        <Paperclip className="h-4 w-4" />
                    </Button>
                    <Select
                        value={chatType}
                        onValueChange={(value: 'whisper' | 'analysis') => setChatType(value)}
                    >
                        <SelectTrigger className="w-[100px]">
                            <SelectValue placeholder="Chat type" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="whisper">Whisper</SelectItem>
                            <SelectItem value="analysis">Analysis</SelectItem>
                        </SelectContent>
                    </Select>
                    <Input
                        className="flex-grow"
                        placeholder="说点什么..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                    />
                    <Button onClick={handleSendMessage}>
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </CardFooter>
        );
    };

    return (
        <div className="flex flex-col min-h-screen bg-background">
            <Navbar />
            <div className="container flex w-full mx-auto mt-4 mb-4 px-4 flex-grow">
                {/* Left panel with tabs and status bar */}
                <div className="w-2/3 pr-4 flex flex-col">
                    <Tabs defaultValue="map" className="w-full flex-grow"
                    // onValueChange={(value) => value === 'ai' && fetchAgentStatus()}
                    >
                        <TabsList className="grid w-full grid-cols-4">
                            <TabsTrigger value="dialog"><MessageSquare className="mr-2 h-4 w-4" />对话</TabsTrigger>
                            <TabsTrigger value="map"><MapPin className="mr-2 h-4 w-4" />地图</TabsTrigger>
                            <TabsTrigger value="ai"><Bot className="mr-2 h-4 w-4" />智能体状态</TabsTrigger>
                            <TabsTrigger value="log"><FileText className="mr-2 h-4 w-4" />日志</TabsTrigger>
                        </TabsList>
                        <TabsContent value="dialog" className="flex-grow">
                            <DialogTab messages={publicMessages} />
                        </TabsContent>
                        {ctx.data.currentTemplate?.meta.sim_mode == "offline" && <TabsContent value="map" className="flex-grow">
                            <MapTab />
                        </TabsContent>}
                        <TabsContent value="ai" className="flex-grow">
                            <AgentStatusTab />
                        </TabsContent>
                        <TabsContent value="log" className="flex-grow">
                            <LogTab logs={logs} addLog={addLog} clearLogs={clearLogs} setIsRunning={setIsRunning} />
                        </TabsContent>

                    </Tabs>
                    <StatusBar isRunning={isRunning} />
                </div>

                {/* Right panel with chat */}
                <div className="w-1/3 pl-4">
                    <Card className="h-full flex flex-col">
                        <CardHeader className="flex flex-row items-center space-x-4 pb-6 mb-6 border-b border-b-gray-300">
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" className="p-0 hover:bg-transparent">
                                        <Avatar>
                                            {privateChatAgent && ctx.data.agents && <RandomAvatar className='w-12 h-12' name={`${ctx.data.agents[privateChatAgent].first_name} ${ctx.data.agents[privateChatAgent].last_name}`} />}
                                        </Avatar>
                                        <div className="ml-2 text-left">
                                            {privateChatAgent && ctx.data.agents && <h2 className="text-xl font-bold">{ctx.data.agents[privateChatAgent].name}</h2>}
                                        </div>
                                        <ChevronDown className="ml-2" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align='start'>
                                    {ctx.data.currentTemplate && ctx.data.currentTemplate.personas.map((persona: apis.Agent) => (
                                        <DropdownMenuItem key={persona.name} onSelect={() => setPrivateChatAgent(persona.name)} className='flex flex-row items-center align-center'>
                                            <Avatar className="mr-2">
                                                <RandomAvatar className='w-8 h-8 mt-1' name={`${persona.first_name} ${persona.last_name}`} />
                                            </Avatar>
                                            <span>{`${persona.first_name} ${persona.last_name}`}</span>
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>

                            </DropdownMenu>
                        </CardHeader>
                        <CardContent className="flex-grow overflow-hidden">
                            <ScrollArea className="h-[calc(100vh-350px)] px-4">
                                {privateChatAgent && privateMessages[privateChatAgent]?.map((msg, index) => (
                                    <ChatMessageBox key={index} {...msg} />
                                )) || (
                                        <p>No private messages with {privateChatAgent}</p>
                                    )}
                            </ScrollArea>
                        </CardContent>
                        <ChatFooter simCode={ctx.data.currSimCode || ""} agentName={privateChatAgent} />
                    </Card>
                </div>
            </div>
        </div>
    );
};
