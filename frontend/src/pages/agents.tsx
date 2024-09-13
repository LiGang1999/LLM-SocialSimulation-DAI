import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar"
import { BottomNav } from "@/components/BottomNav"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { PlusCircle, Save, Trash2 } from 'lucide-react'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { RandomAvatar } from '@/components/Avatars';
import { AutoResizeTextarea } from '@/components/autoResizeTextArea';
import { InfoIcon } from 'lucide-react';

const mockAgents: (apis.Agent & { id: number })[] = [
    {
        id: 1,
        name: 'Isabella Rodriguez',
        first_name: 'Isabella',
        last_name: 'Rodriguez',
        age: 34,
        daily_plan_req: 'Isabella Rodriguez opens Hobbs Cafe at 8am everyday, and works at the counter until 8pm, at which point she closes the cafe.',
        daily_req: [],
        f_daily_schedule: [],
        f_daily_schedule_hourly_org: [],
        innate: 'friendly, outgoing, hospitable',
        learned: 'Isabella Rodriguez is a cafe owner of Hobbs Cafe who loves to make people feel welcome. She is always looking for ways to make the cafe a place where people can come to relax and enjoy themselves. She is concerned with environmental issues and big global events, although she does not have professional knowledge in these areas.',
        currently: '',
        lifestyle: 'Busy cafe owner, health-conscious',
        living_area: 'Small apartment above Hobbs Cafe',
        plan: [],
        memory: [],
        bibliography: 'Local business owner, community pillar',
        act_event: [''],
        act_obj_event: [],
        act_path_set: false,
        planned_path: [],
        chatting_with_buffer: {}
    },
    {
        id: 2,
        name: 'Marcus Chen',
        first_name: 'Marcus',
        last_name: 'Chen',
        age: 28,
        daily_plan_req: 'Marcus Chen starts his day at 7am with a morning run. He works as a software developer from 9am to 6pm, with a lunch break at noon. After work, he often attends local tech meetups or works on personal coding projects until around 10pm.',
        daily_req: [],
        f_daily_schedule: [],
        f_daily_schedule_hourly_org: [],
        innate: 'analytical, introverted, creative',
        learned: 'Marcus Chen is a talented software developer who specializes in AI and machine learning. He\'s passionate about technology and its potential to solve complex problems. He\'s also an advocate for open-source software and contributes to several projects in his free time.',
        currently: '',
        lifestyle: 'Tech-savvy, fitness enthusiast',
        living_area: 'Modern studio apartment in the city center',
        plan: [],
        memory: [],
        bibliography: 'Rising star in the local tech scene',
        act_event: [''],
        act_obj_event: [],
        act_path_set: false,
        planned_path: [],
        chatting_with_buffer: {}
    },
    {
        id: 3,
        name: 'Aisha Patel',
        first_name: 'Aisha',
        last_name: 'Patel',
        age: 42,
        daily_plan_req: 'Aisha Patel begins her day at 6am with yoga and meditation. She sees patients at her clinic from 9am to 5pm, with a break for lunch and paperwork. In the evenings, she often volunteers at a local community health center or attends medical conferences.',
        daily_req: [],
        f_daily_schedule: [],
        f_daily_schedule_hourly_org: [],
        innate: 'empathetic, detail-oriented, calm',
        learned: 'Aisha Patel is a respected pediatrician with over 15 years of experience. She\'s known for her holistic approach to healthcare, combining Western medicine with traditional practices. She\'s actively involved in public health initiatives and regularly gives talks on child nutrition and preventive care.',
        currently: '',
        lifestyle: 'Health-focused, community-oriented',
        living_area: 'Spacious family home in a quiet suburb',
        plan: [],
        memory: [],
        bibliography: 'Renowned pediatrician and public health advocate',
        act_event: [''],
        act_obj_event: [],
        act_path_set: false,
        planned_path: [],
        chatting_with_buffer: {}
    }
];

export const AgentsPage = () => {
    const ctx = useSimContext();

    const [agents, setAgents] = useState<(apis.Agent & { id: number })[]>([]);
    const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);
    const [localAgent, setLocalAgent] = useState<(apis.Agent & { id: number }) | null>(null);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.templateCode && !ctx.data.currentTemplate) {
                    const templateData = await apis.fetchTemplate(ctx.data.templateCode);
                    ctx.setData({
                        ...ctx.data,
                        currentTemplate: templateData
                    });
                }
            } catch (err) {
                console.error("Failed to fetch template detail:", err);
            }
        }

        fetchTemplates();
    }, []);

    useEffect(() => {
        if (ctx.data.currentTemplate?.personas && ctx.data.currentTemplate.personas.length > 0) {
            const agentsWithId = ctx.data.currentTemplate.personas.map((agent, index) => ({
                ...agent,
                id: index + 1,
            }));
            setAgents(agentsWithId);
            setSelectedAgentId(agentsWithId[0].id);
            // If current selected Agent id is within all ids:
            // if (agentsWithId.map(a => a.id).includes(selectedAgentId)) {

            // }
            console.log(agentsWithId[0].id, "a")
        } else if (!ctx.data.currentTemplate && agents.length === 0) {
            setAgents(mockAgents);
            setSelectedAgentId(mockAgents[0].id);
            console.log(mockAgents[0].id, "b")
        } else if (ctx.data.currentTemplate && ctx.data.currentTemplate.personas.length === 0) {
            setAgents([]);
            setSelectedAgentId(null);
            console.log(null, "c")
        }
    }, [ctx.data.currentTemplate]);

    useEffect(() => {
        if (selectedAgentId) {
            const agent = agents.find(a => a.id === selectedAgentId);
            setLocalAgent(agent ? { ...agent } : null);
        }
    }, [selectedAgentId, agents]);

    const handleAgentSelect = (id: number) => {
        setSelectedAgentId(id);
        console.log(id, "d")
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        if (localAgent) {
            const { name, value } = e.target;
            const updatedAgent = { ...localAgent, [name]: value };
            setLocalAgent(updatedAgent);

            setAgents(prevAgents =>
                prevAgents.map(agent =>
                    agent.id === updatedAgent.id ? updatedAgent : agent
                )
            );
            updateContextPersonas(agents.map(agent =>
                agent.id === updatedAgent.id ? updatedAgent : agent
            ));
        }
    };


    const handleAddAgent = () => {
        const newId = Math.max(...agents.map(a => a.id), 0) + 1;

        const existingNumbers = agents
            .map(a => a.name.match(/智能体 (\d+)/))
            .filter(Boolean)
            .map(match => parseInt((match || "")[1], 10));
        const highestNumber = Math.max(...existingNumbers, 0);
        const newNumber = highestNumber + 1;

        const newName = `智能体 ${newNumber}`;

        const newAgent: apis.Agent & { id: number } = {
            id: newId,
            name: newName,
            first_name: newName.split(' ')[0],  // Assuming newName might include a last name
            last_name: newName.split(' ').slice(1).join(' ') || '',  // Get last name if exists
            age: 0,
            daily_plan_req: '',
            daily_req: [],
            f_daily_schedule: [],
            f_daily_schedule_hourly_org: [],
            innate: '',
            learned: '',
            currently: '',
            lifestyle: '',
            living_area: '',
            plan: [],
            memory: [],
            bibliography: '',
            act_event: ['', '', ''],
            act_obj_event: ['', '', ''],
            act_path_set: false,
            act_address: '',
            act_description: '',
            act_duration: '',
            act_start_time: '',
            act_obj_description: '',
            act_obj_pronunciatio: '',
            act_pronunciatio: '',
            chatting_with_buffer: {},
            planned_path: [],  // This was missing in the original object
            curr_time: 0,  // Added with a default value
            curr_tile: '',  // Added with a default value
        };

        const updatedAgents = [...agents, newAgent];
        setAgents(updatedAgents);
        setSelectedAgentId(newId);
        console.log(newId, "e")
        updateContextPersonas(updatedAgents);
    };

    const handleRemoveAgent = (agentId: number) => {
        const updatedAgents = agents.filter(agent => agent.id !== agentId);
        setAgents(updatedAgents);
        setSelectedAgentId(updatedAgents.length > 0 ? updatedAgents[0].id : null);
        console.log(updatedAgents.length > 0 ? updatedAgents[0].id : null, "f")
        updateContextPersonas(updatedAgents);

        if (updatedAgents.length === 0) {
            ctx.setData({
                ...ctx.data,
                currentTemplate: ctx.data.currentTemplate ? {
                    ...ctx.data.currentTemplate,
                    personas: []
                } : undefined
            });
        }
    };

    const updateContextPersonas = (updatedAgents: (apis.Agent & { id: number })[]) => {
        ctx.setData({
            ...ctx.data,
            currentTemplate: ctx.data.currentTemplate ? {
                ...ctx.data.currentTemplate,
                personas: updatedAgents.map(({ id, ...agent }) => agent)
            } : undefined
        });
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 3.</span>自定义智能体</h2>

                <div className="  mb-8">
                    <div className="flex items-center mb-4">
                        <InfoIcon className="w-6 h-6 text-blue-500 mr-2" />
                        <h3 className="text-xl font-semibold text-gray-800">什么是仿真模板？</h3>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                        仿真模板是预先配置好的社会情境和参数集合，集成了大型语言模型（LLM）技术。每个模板都代表一个独特的社交场景，如公共事件讨论、市长竞选或社区互动。这些模板预设了智能体数量、环境特征和互动规则，让您可以快速开始探索复杂的社会动态。选择一个模板，即可启动一个由AI驱动的、高度逼真的社会仿真实验。
                    </p>

                </div>


                <Card className="shadow-lg overflow-hidden">
                    <CardContent className='px-0'>
                        <div className="flex">
                            <div className={`${localAgent ? 'w-1/3' : 'w-full'} border-r border-gray-200`}>
                                <div className="p-4">
                                    <div className="space-y-2">
                                        {agents.map(agent => (
                                            <div
                                                key={agent.id}
                                                className={`flex items-center justify-between p-2 rounded-lg transition-colors duration-200 cursor-pointer ${selectedAgentId === agent.id ? 'bg-secondary' : 'hover:bg-secondary/50'
                                                    }`}
                                                onClick={() => handleAgentSelect(agent.id)}
                                            >
                                                <div className="flex items-center space-x-4 flex-grow">
                                                    <RandomAvatar className="h-10 w-10" name={`${agent.first_name} ${agent.last_name}`} />
                                                    <span className="font-medium">{`${agent.first_name} ${agent.last_name}`}</span>
                                                </div>
                                                <AlertDialog>
                                                    <AlertDialogTrigger asChild>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            className="text-gray-400 hover:text-red-600 hover:bg-red-50 transition-all duration-200 ml-2"
                                                            onClick={(e) => e.stopPropagation()}
                                                        >
                                                            <Trash2 className="h-4 w-4" />
                                                        </Button>
                                                    </AlertDialogTrigger>
                                                    <AlertDialogContent>
                                                        <AlertDialogHeader>
                                                            <AlertDialogTitle>确定要删除这个智能体吗？</AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                此操作无法撤销。这将永久删除该智能体并从我们的服务器中移除其数据。
                                                            </AlertDialogDescription>
                                                        </AlertDialogHeader>
                                                        <AlertDialogFooter>
                                                            <AlertDialogCancel>取消</AlertDialogCancel>
                                                            <AlertDialogAction
                                                                onClick={(e) => {
                                                                    e.stopPropagation();
                                                                    handleRemoveAgent(agent.id);
                                                                }}
                                                                className="bg-red-600 hover:bg-red-700"
                                                            >
                                                                删除
                                                            </AlertDialogAction>
                                                        </AlertDialogFooter>
                                                    </AlertDialogContent>
                                                </AlertDialog>
                                            </div>
                                        ))}
                                    </div>
                                    <Button onClick={handleAddAgent} className="w-full mt-6 bg-indigo-500 hover:bg-indigo-600 text-white">
                                        <PlusCircle className="mr-2 h-4 w-4" /> 添加新智能体
                                    </Button>
                                </div>
                            </div>

                            {localAgent && (
                                <div className="w-2/3 bg-white p-6">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center space-x-4">
                                            <RandomAvatar
                                                className="h-20 w-20"
                                                name={`${localAgent.first_name} ${localAgent.last_name}`}
                                            />
                                            <Input
                                                name="name"
                                                value={localAgent.name}
                                                onChange={handleInputChange}
                                                placeholder="Full Name"
                                                className="text-2xl font-bold w-64"
                                            />
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">名字</label>
                                            <div className="p-2 bg-gray-100 rounded">{localAgent.first_name}</div>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">姓氏</label>
                                            <div className="p-2 bg-gray-100 rounded">{localAgent.last_name}</div>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">年龄</label>
                                            <Input name="age" type="number" value={localAgent.age} onChange={handleInputChange} placeholder="年龄" className="w-full" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">生活方式</label>
                                            <Input name="lifestyle" value={localAgent.lifestyle} onChange={handleInputChange} placeholder="生活方式" className="w-full" />
                                        </div>
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">日常计划要求</label>
                                        <AutoResizeTextarea
                                            name="daily_plan_req"
                                            value={localAgent.daily_plan_req}
                                            onChange={handleInputChange}
                                            placeholder="日常计划要求"
                                            className="w-full min-h-[80px]"
                                        />
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">固有特征</label>
                                        <AutoResizeTextarea name="innate" value={localAgent.innate} onChange={handleInputChange} placeholder="固有特征" className="w-full min-h-[80px]" />
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">学习信息</label>
                                        <AutoResizeTextarea name="learned" value={localAgent.learned} onChange={handleInputChange} placeholder="学习信息" className="w-full min-h-[80px]" />
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">居住区域</label>
                                        <Input name="living_area" value={localAgent.living_area} onChange={handleInputChange} placeholder="居住区域" className="w-full" />
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">个人简介</label>
                                        <AutoResizeTextarea name="bibliography" value={localAgent.bibliography || ''} onChange={handleInputChange} placeholder="个人简介" className="w-full min-h-[80px]" />
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/events' nextLink='/llmconfig' currStep={2} disabled={false} className='my-8' />
            </div>
        </div>
    )
}