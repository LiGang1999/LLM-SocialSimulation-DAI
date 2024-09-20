import React, { useState, useEffect, useRef } from 'react';
import { Navbar } from "@/components/Navbar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardHeader, CardFooter } from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Select, SelectItem, SelectTrigger, SelectValue, SelectContent } from "@/components/ui/select";
import { ScrollArea } from "@/components/ui/scroll-area";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { ChevronDown, Send, MapPin, MessageSquare, Bot, FileText, Clock, Image, Paperclip, Trash2, MoreHorizontal, RefreshCw, ArrowUp, ArrowDown, ArrowLeft, ArrowRight, RotateCcw, XCircle, AlertTriangle, Info, Bug, Terminal, AlertOctagon } from 'lucide-react';
import { apis } from '@/lib/api';
import { ChatMessage, useSimContext } from '@/SimContext';
import { RandomAvatar } from '@/components/Avatars';
import mockBg from '@/assets/map.png';
import SimulationGuide from '@/components/SimulationGuide';
import { CSSTransition } from 'react-transition-group';


import backgroundImage from '@/assets/Untitled.png'

import { Loader } from 'lucide-react';  // Import the Loader icon


interface LogEntry {
    level: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR' | 'CRITICAL' | 'COMMAND';
    message: string;
};

interface ChatFooterProps {
    simCode: string;
    agentName: string;
    showGuide: boolean;
    setShowGuide: (show: boolean) => void;
    isRunning: boolean;
    handleRunSimulation: (rounds: number) => void;
    simRounds: number;
    setSimRounds: (rounds: number) => void;
}

const ChatMessageBox: React.FC<ChatMessage & { variant?: 'public' | 'private' }> = ({ sender, content, timestamp, subject, variant = 'public' }) => (
    <div className={`flex ${sender === 'Interviewer' ? 'justify-end' : 'justify-start'} mb-4 items-start`}>
        {sender !== 'Interviewer' && (
            <Avatar className="mr-2 mt-1">
                <RandomAvatar name={sender} className='h-8 w-8' />
            </Avatar>
        )}
        <div className={`max-w-[70%] ${sender === 'Interviewer' ? 'bg-primary text-primary-foreground' : 'bg-secondary'} rounded-lg p-3`}>
            {sender !== 'Interviewer' && (
                <p className="text-xs font-semibold mb-1">
                    {sender}
                    {variant === 'public' && subject && <span className="text-muted-foreground"> about <span className="font-normal italic">{subject}</span></span>}
                </p>
            )}
            <p className="text-sm">{content}</p>
            <span className="text-xs text-muted-foreground block mt-1">{timestamp}</span>
        </div>
        {sender === 'Interviewer' && (
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
        <div className="flex justify-between items-center bg-white bg-opacity-70 p-2 border-2 border-blue rounded-md mt-4">
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
const DialogTab: React.FC<{ messages: ChatMessage[], isRunning: boolean }> = ({ messages, isRunning }) => {
    const scrollRef = useRef<HTMLDivElement>(null);
    const [isAtBottom, _] = useState(true);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    };

    useEffect(() => {
        scrollToBottom()
    }, [JSON.stringify(messages)]);

    return (
        <div className="relative h-[calc(100vh-200px)]">
            <ScrollArea
                className="h-full rounded-md bg-white bg-opacity-70 border-gray-100 pl-2"
                ref={scrollRef}
            >
                <div className="p-4">
                    {messages.map((msg, index) => (
                        <ChatMessageBox key={index} {...msg} />
                    ))}
                </div>
                <div ref={messagesEndRef} />
            </ScrollArea>
            {!isAtBottom && (
                <Button
                    className="absolute bottom-4 right-4 rounded-full"
                    onClick={scrollToBottom}
                >
                    <ArrowDown className="h-4 w-4 mr-2" />
                    Back to Bottom
                </Button>
            )}
            {/* 3. Display the loading overlay when isRunning is true */}
            {isRunning && (
                <>
                    <div className="absolute inset-0 bg-white opacity-50 rounded-lg" />
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-4 flex items-center z-10">
                        <Loader className="animate-spin w-6 h-6 text-gray-500 mr-3" />
                        <div className="font-bold text-sm">仿真正在运行，请稍等...</div>
                    </div>
                </>
            )}
        </div>
    );
};



const MapTab: React.FC<{ isRunning: boolean }> = ({ isRunning }) => {
    const [position, setPosition] = useState({ x: 0, y: 0 });
    const moveStep = 50; // pixels to move per click

    const moveMap = (direction: 'up' | 'down' | 'left' | 'right') => {
        setPosition(prev => {
            switch (direction) {
                case 'up': return { ...prev, y: prev.y + moveStep };
                case 'down': return { ...prev, y: prev.y - moveStep };
                case 'left': return { ...prev, x: prev.x + moveStep };
                case 'right': return { ...prev, x: prev.x - moveStep };
            }
        });
    };

    const resetPosition = () => setPosition({ x: 0, y: 0 });

    return (
        <div className="relative w-full h-[calc(100vh-200px)] overflow-hidden">
            <img
                src={mockBg}
                alt="Map"
                className="w-full h-full object-cover absolute"
                style={{
                    transform: `translate(${position.x}px, ${position.y}px)`,
                    transition: 'transform 0.3s ease-out',
                }}
            />
            <div className="absolute bottom-4 right-4">
                <div className="grid grid-cols-3 gap-2">
                    <div></div>
                    <button className="p-2 bg-white rounded-full shadow-md" onClick={() => moveMap('up')}><ArrowUp /></button>
                    <div></div>
                    <button className="p-2 bg-white rounded-full shadow-md" onClick={() => moveMap('left')}><ArrowLeft /></button>
                    <button className="p-2 bg-white rounded-full shadow-md" onClick={resetPosition}><RotateCcw /></button>
                    <button className="p-2 bg-white rounded-full shadow-md" onClick={() => moveMap('right')}><ArrowRight /></button>
                    <div></div>
                    <button className="p-2 bg-white rounded-full shadow-md" onClick={() => moveMap('down')}><ArrowDown /></button>
                    <div></div>
                </div>
            </div>
            {isRunning && (
                <>
                    <div className="absolute inset-0 bg-white opacity-50 rounded-lg" />
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-4 flex items-center z-10">
                        <Loader className="animate-spin w-6 h-6 text-gray-500 mr-3" />
                        <div className="font-bold text-sm">仿真正在运行，请稍等...</div>
                    </div>
                </>
            )}
        </div>
    );
};


const AgentStatusCard: React.FC<{ agent: apis.Agent, onViewFullInfo: (agentName: string) => void }> = ({ agent, onViewFullInfo }) => {
    const [expanded, setExpanded] = useState(false);

    return (
        <Card className="mb-4">
            <CardHeader className="flex flex-row items-center justify-between">
                <div className="flex items-center space-x-4">
                    <RandomAvatar name={`${agent.first_name} ${agent.last_name}`} className='w-14 h-14' />
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

const AgentStatusTab: React.FC<{ isRunning: boolean }> = ({ isRunning }) => {
    const [agents, setAgents] = useState<apis.Agent[]>([]);
    const [selectedAgent, setSelectedAgent] = useState<apis.Agent | null>(null);

    const { data } = useSimContext();

    const fetchAgentStatus = async () => {
        const agentsInfo = await apis.agentsInfo(data.currSimCode || "");
        console.log(agentsInfo);
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
        <div className="relative">

            <ScrollArea className="h-[calc(100vh-230px)] bg-white bg-opacity-70 p-4 rounded-lg">
                {agents.map((agent, index) => (
                    <AgentStatusCard key={index} agent={agent} onViewFullInfo={handleViewFullInfo} />
                ))}

            </ScrollArea>
            <div className="w-full">
                <Button onClick={fetchAgentStatus} className='w-full'>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Refresh
                </Button>
            </div>
            {selectedAgent && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
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
            {isRunning && (
                <>
                    <div className="absolute inset-0 bg-white opacity-50 rounded-lg" />
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-4 flex items-center z-10">
                        <Loader className="animate-spin w-6 h-6 text-gray-500 mr-3" />
                        <div className="font-bold text-sm">仿真正在运行，请稍等...</div>
                    </div>
                </>
            )}
        </div>
    );
};


const LogTab: React.FC<{
    logs: LogEntry[],
    addLog: (log: LogEntry) => void,
    clearLogs: () => void,
    setIsRunning: (isRunning: boolean) => void,
    isRunning: boolean
}> = ({ logs, addLog, clearLogs, setIsRunning, isRunning }) => {
    const [command, setCommand] = useState('');
    const ctx = useSimContext();
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const scrollRef = useRef<HTMLDivElement>(null);

    const handleCommand = async () => {
        setIsRunning(true);
        addLog({ level: 'COMMAND', message: command });
        // Process command here
        await apis.sendCommand(command, ctx.data.currSimCode || "");
        setCommand("")
    };

    const getLogColor = (level: LogEntry['level']) => {
        switch (level) {
            case 'DEBUG': return 'text-gray-500';
            case 'INFO': return 'text-blue-500';
            case 'WARNING': return 'text-yellow-500';
            case 'ERROR': return 'text-red-500';
            case 'CRITICAL': return 'text-red-700 font-bold';
            case 'COMMAND': return 'text-purple-500';
            default: return 'text-gray-700';
        }
    };

    const getLogIcon = (level: LogEntry['level']) => {
        switch (level) {
            case 'DEBUG': return <Bug className="h-4 w-4 mr-2" />;
            case 'INFO': return <Info className="h-4 w-4 mr-2" />;
            case 'WARNING': return <AlertTriangle className="h-4 w-4 mr-2" />;
            case 'ERROR': return <XCircle className="h-4 w-4 mr-2" />;
            case 'CRITICAL': return <AlertOctagon className="h-4 w-4 mr-2" />;
            case 'COMMAND': return <Terminal className="h-4 w-4 mr-2" />;
            default: return null;
        }
    };

    const scrollToBottom = () => {
        // if (autoScroll) {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        // }
    };

    // const handleWheel = (event: React.WheelEvent<HTMLDivElement>) => {
    //     if (scrollRef.current) {
    //         const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
    //         const atBottom = Math.abs(scrollHeight - clientHeight - scrollTop) < 20;

    //         if (event.deltaY < 0) { // Scrolling up
    //             setAutoScroll(false);
    //             console.log("User scrolled up using mouse wheel");
    //         } else if (event.deltaY > 0 && atBottom) { // Scrolling down and at bottom
    //             setAutoScroll(true);
    //             console.log("User scrolled to bottom using mouse wheel");
    //         }
    //     }
    // };



    useEffect(() => {
        scrollToBottom()
    }, [JSON.stringify(logs)]);

    return (
        <div className="flex-col rounded-lg bg-white bg-opacity-70 p-4 relative">
            <ScrollArea
                className="font-mono text-sm h-[calc(100vh-280px)]"
                // onScrollCapture={handleScroll}
                // onWheel={handleWheel}
                // ref={scrollRef}
                viewportRef={scrollRef}
            >
                {logs.map((log, index) => (
                    <div key={index} className={`flex items-start ${getLogColor(log.level)} mb-1`}>
                        <div className="flex items-center mr-2 flex-shrink-0">
                            {getLogIcon(log.level)}
                            <span className="font-bold">{log.level}</span>
                        </div>
                        <p className="m-0 break-words">{log.message}</p>
                    </div>
                ))}
                <div ref={messagesEndRef} />
            </ScrollArea>
            <div className="flex mt-4">
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
            {isRunning && (
                <>
                    <div className="absolute inset-0 bg-white opacity-50 rounded-lg" />
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-white rounded-lg p-4 flex items-center z-10">
                        <Loader className="animate-spin w-6 h-6 text-gray-500 mr-3" />
                        <div className="font-bold text-sm">仿真正在运行，请稍等...</div>
                    </div>
                </>
            )}
        </div>
    );
};





export const InteractPage: React.FC = () => {
    const ctx = useSimContext();
    const [logs, setLogs] = useState<LogEntry[]>([]);

    const [buttonPosition, setButtonPosition] = useState({ top: 0, left: 0, width: 0, height: 0 });
    const [chatTypes, setChatTypes] = useState<Record<string, 'whisper' | 'interview'>>({});

    const runButtonRef = useRef<HTMLButtonElement>(null);

    const [isRunning, setIsRunning] = useState(true);
    const [privateChatAgent, setPrivateChatAgent] = useState<string>("");
    const [simRounds, setSimRounds] = useState<number>(1);
    const [demo, _] = useState(true);
    const [showGuide, setShowGuide] = useState(false);

    // New state for messages
    const [publicMessages, setPublicMessages] = useState<ChatMessage[]>([]);
    const [privateMessages, setPrivateMessages] = useState<Record<string, ChatMessage[]>>({});
    const [isOffline, setIsOffline] = useState<boolean>(false);
    const [agents, setAgents] = useState<apis.Agent[]>([]);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const fetchedAgents = await apis.agentsInfo(ctx.data.currSimCode || "");
                setAgents(fetchedAgents);
                console.log('fetched agents', fetchedAgents)

                // Set the privateChatAgent to the first agent's name
                if (fetchedAgents.length > 0) {
                    setPrivateChatAgent(fetchedAgents[0].name);
                }

                // Initialize privateMessages and chatTypes with empty arrays and 'interview' for each agent
                const initialPrivateMessages = fetchedAgents.reduce((acc, agent) => {
                    acc[agent.name] = [];
                    return acc;
                }, {} as Record<string, ChatMessage[]>);
                setPrivateMessages(initialPrivateMessages);

                const initialChatTypes = fetchedAgents.reduce((acc, agent) => {
                    acc[agent.name] = 'interview';
                    return acc;
                }, {} as Record<string, 'whisper' | 'interview'>);
                setChatTypes(initialChatTypes);
            } catch (error) {
                console.error("Error fetching agents:", error);
            }
        };

        fetchAgents();
        setIsOffline(ctx.data.currentTemplate?.meta.sim_mode != "online");
    }, [ctx.data.currSimCode, ctx.data.currentTemplate?.meta.sim_mode]);

    useEffect(() => {
        if (runButtonRef.current && showGuide) {
            const rect = runButtonRef.current.getBoundingClientRect();
            setButtonPosition({
                top: rect.top,
                left: rect.left,
                width: rect.width,
                height: rect.height
            });
        }
    }, [showGuide]);




    const addPublicMessage = (message: ChatMessage) => {
        setPublicMessages(prevMessages => [...prevMessages, message]);
    };

    const addPrivateMessage = (agentName: string, message: ChatMessage) => {
        setPrivateMessages(prevMessages => ({
            ...prevMessages,
            [agentName]: [...(prevMessages[agentName] || []), message]
        }));
    };


    const addLog = (log: LogEntry) => {
        setLogs(prevLogs => [...prevLogs, log]);
    };
    const clearLogs = () => {
        setLogs([]);
    };

    const handleRunSimulation = async (rounds: number) => {
        try {
            setIsRunning(true);
            await apis.runSim(rounds, ctx.data.currSimCode || "");
        } catch (error) {
            console.error("Error running simulation:", error);
            // Handle the error, e.g., show an error message to the user
        } finally {
            setIsRunning(false);
        }
    };

    useEffect(() => {
        if (demo && ctx.data.currentTemplate?.personas) {
            const demoMessagesForAgents: Record<string, ChatMessage[]> = {};

            ctx.data.currentTemplate.personas.forEach((persona: apis.Agent) => {
                const agentName = persona.name;
                demoMessagesForAgents[agentName] = [
                    {
                        sender: agentName,
                        content: `Hello! I'm ${persona.first_name} ${persona.last_name}. How can I assist you today?`,
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'private',
                        role: 'agent',
                        subject: 'Introduction'
                    },
                    {
                        sender: 'user',
                        content: `Hi ${persona.first_name}! What's your primary focus right now?`,
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'private',
                        role: 'user',
                        subject: 'Current Focus'
                    },
                    {
                        sender: agentName,
                        content: `Great question! My current primary focus is ${persona.currently}. I'm really passionate about ${persona.innate} and always looking to improve my skills in ${persona.learned}.`,
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'private',
                        role: 'agent',
                        subject: 'Current Focus and Interests'
                    }
                ];
            });

            setPrivateMessages(demoMessagesForAgents);
            console.log(demoMessagesForAgents)
        }
    }, [demo, ctx.data.currentTemplate]);

    const initialCheckRef = useRef(true);

    useEffect(() => {
        const checkStatus = async () => {
            const status = await apis.queryStatus(ctx.data.currSimCode || '');
            setIsRunning(status === 'running');
            if (status !== 'running' && initialCheckRef.current) {
                setShowGuide(true);
                initialCheckRef.current = false;  // 标记为已检查
            }
        };

        checkStatus();  // 初始检查

        // Set up interval to check status
        const intervalId = setInterval(checkStatus, 1000); // Check every 5 seconds

        // Clean up interval on unmount
        return () => clearInterval(intervalId);
    }, [ctx.data.currSimCode]);


    const [messageSocket, setMessageSocket] = useState<WebSocket | null>(null);

    useEffect(() => {
        // Create WebSocket connections when the component mounts
        const newMessageSocket = apis.messageSocket(ctx.data.currSimCode || "");

        // Update state with the new WebSocket instances
        setMessageSocket(newMessageSocket);

        // Clean up WebSocket connections when the component unmounts
        return () => {
            newMessageSocket.close();
        };


    }, [ctx.data.currSimCode]);

    useEffect(() => {
        if (messageSocket) {
            messageSocket.onmessage = (event) => {
                const d = JSON.parse(event.data);
                if (d.type == "log") {
                    const e: LogEntry = d.message;
                    const level = e.level;
                    const message = e.message;
                    addLog({ level, message });
                } else if (d.type == "chat") {
                    const e: ChatMessage = d.message;
                    if (e.type == "public") {
                        addPublicMessage(e);
                    } else if (e.type == "private") {
                        addPrivateMessage(e.sender, e);
                    }
                }
            };
        }
    }, [messageSocket]);



    // console.log(ctx.data)
    // const currentAgent = ctx.data.agents[privateChatAgent];


    const ChatFooter: React.FC<ChatFooterProps> = ({
        simCode,
        agentName,
        showGuide,
        setShowGuide,
        isRunning,
        handleRunSimulation,
        simRounds,
        setSimRounds
    }) => {

        const [message, setMessage] = useState('');
        const runButtonRef = useRef<HTMLButtonElement>(null);

        const handleSendMessage = async () => {
            if (message.trim()) {
                try {
                    setIsRunning(true);

                    const userMessage: ChatMessage = {
                        sender: 'Interviewer',
                        content: message,
                        timestamp: new Date().toLocaleTimeString(),
                        type: 'private',
                        role: 'user',
                        subject: chatTypes[agentName]
                    };

                    const response = await apis.privateChat(simCode, agentName, chatTypes[agentName], privateMessages[agentName], message);
                    console.log(response);

                    addPrivateMessage(agentName, userMessage);

                    setMessage('');
                    setIsRunning(false);
                } catch (error) {
                    console.error("Error sending private chat:", error);
                    setIsRunning(false);
                }
            }
        };

        useEffect(() => {
            if (runButtonRef.current && showGuide) {
                const rect = runButtonRef.current.getBoundingClientRect();
                setButtonPosition({
                    top: rect.top,
                    left: rect.left,
                    width: rect.width,
                    height: rect.height
                });
            }
        }, [showGuide]);

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
                            ref={runButtonRef}
                            size="sm"
                            variant={showGuide ? "default" : "outline"}
                            onClick={() => {
                                handleRunSimulation(simRounds);
                                setShowGuide(false);
                            }}
                            disabled={isRunning}
                            className={`
        ${showGuide ? "animate-pulse bg-primary text-primary-foreground" : ""}
        ${showGuide ? "z-[500] relative shadow-lg" : ""}
    `}
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
                        value={chatTypes[agentName]}
                        onValueChange={(value: 'whisper' | 'interview') => setChatTypes(prev => ({ ...prev, [agentName]: value }))}
                    >
                        <SelectTrigger className="w-[100px]">
                            <SelectValue placeholder="Interview" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="whisper">Whisper</SelectItem>
                            <SelectItem value="interview">Interview</SelectItem>
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
        <div className="flex flex-col min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar />
            <div className="container flex w-full mx-auto mt-4 mb-4 px-4 flex-grow">
                {/* Left panel with tabs and status bar */}
                <div className="w-2/3 pr-4 flex flex-col">
                    <Tabs defaultValue="dialog" className="w-full flex-grow"
                    // onValueChange={(value) => value === 'ai' && fetchAgentStatus()}
                    >
                        <TabsList className={isOffline ? `grid w-full grid-cols-4` : `grid w-full grid-cols-3` + " bg-white bg-opacity-50"}>
                            <TabsTrigger value="dialog"><MessageSquare className="mr-2 h-4 w-4" />对话</TabsTrigger>
                            {isOffline && <TabsTrigger value="map"><MapPin className="mr-2 h-4 w-4" />地图</TabsTrigger>}
                            <TabsTrigger value="ai"><Bot className="mr-2 h-4 w-4" />智能体状态</TabsTrigger>
                            <TabsTrigger value="log"><FileText className="mr-2 h-4 w-4" />日志</TabsTrigger>
                        </TabsList>
                        <TabsContent value="dialog" className="flex-grow">
                            <DialogTab messages={publicMessages} isRunning={isRunning} />
                        </TabsContent>
                        {isOffline && <TabsContent value="map" className="h-full w-full">
                            <MapTab isRunning={isRunning} />
                        </TabsContent>}
                        <TabsContent value="ai" className="flex-grow">
                            <AgentStatusTab isRunning={isRunning} />
                        </TabsContent>
                        <TabsContent value="log" className="flex-grow">
                            <LogTab logs={logs} addLog={addLog} clearLogs={clearLogs} setIsRunning={setIsRunning} isRunning={isRunning} />
                        </TabsContent>

                    </Tabs>
                    <StatusBar isRunning={isRunning} />
                </div>

                {/* Right panel with chat */}
                <div className="w-1/3 pl-4">
                    <Card className="h-full flex flex-col bg-white bg-opacity-70">
                        <CardHeader className="flex flex-row items-center space-x-4 pb-6 mb-6 border-b border-b-gray-300">
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" className="p-0 hover:bg-transparent">
                                        <Avatar>
                                            {privateChatAgent && agents && <RandomAvatar className='w-12 h-12' name={`${agents.find(a => a.name === privateChatAgent)?.first_name} ${agents.find(a => a.name === privateChatAgent)?.last_name}`} />}
                                        </Avatar>
                                        <div className="ml-2 text-left">
                                            {privateChatAgent && agents && <h2 className="text-xl font-bold">{agents.find(a => a.name === privateChatAgent)?.name}</h2>}
                                        </div>
                                        <ChevronDown className="ml-2" />
                                    </Button>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent align='start'>
                                    {agents.map((agent) => (
                                        <DropdownMenuItem key={agent.name} onSelect={() => setPrivateChatAgent(agent.name)} className='flex flex-row items-center align-center'>
                                            <Avatar className="mr-2">
                                                <RandomAvatar className='w-8 h-8 mt-1' name={`${agent.first_name} ${agent.last_name}`} />
                                            </Avatar>
                                            <span>{`${agent.first_name} ${agent.last_name}`}</span>
                                        </DropdownMenuItem>
                                    ))}
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </CardHeader>
                        <CardContent className="flex-grow overflow-hidden">
                            <ScrollArea className="h-[calc(100vh-350px)] px-4">
                                {privateChatAgent && privateMessages[privateChatAgent]?.map((msg, index) => (
                                    <ChatMessageBox key={index} {...msg} variant="private" />
                                )) || (
                                        <p>No private messages with {privateChatAgent}</p>
                                    )}
                            </ScrollArea>
                        </CardContent>
                        <ChatFooter
                            simCode={ctx.data.currSimCode || ""}
                            agentName={privateChatAgent}
                            showGuide={showGuide}
                            setShowGuide={setShowGuide}
                            isRunning={isRunning}
                            handleRunSimulation={handleRunSimulation}
                            simRounds={simRounds}
                            setSimRounds={setSimRounds}
                        />
                    </Card>
                </div>
            </div>
            <CSSTransition
                in={showGuide}
                timeout={300} // Duration of the animation in milliseconds
                classNames="fade"
                unmountOnExit
            >
                <SimulationGuide
                    onClose={() => setShowGuide(false)}
                    simRounds={simRounds}
                    buttonPosition={buttonPosition}
                />
            </CSSTransition>

        </div>
    );
};
