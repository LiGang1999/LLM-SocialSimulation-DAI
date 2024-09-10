import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar"
import { BottomNav } from "@/components/BottomNav"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { PlusCircle, Save, Trash2 } from 'lucide-react'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { RandomAvatar } from '@/components/Avatars';
import { AutoResizeTextarea } from '@/components/autoResizeTextArea';

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
        } else if (!ctx.data.currentTemplate && agents.length === 0) {
            setAgents(mockAgents);
            setSelectedAgentId(mockAgents[0].id);
        } else if (ctx.data.currentTemplate && ctx.data.currentTemplate.personas.length === 0) {
            setAgents([]);
            setSelectedAgentId(null);
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
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        if (localAgent) {
            setLocalAgent({
                ...localAgent,
                [e.target.name]: e.target.value
            });
        }
    };

    const handleSave = () => {
        if (localAgent) {
            const updatedAgents = agents.map(agent =>
                agent.id === localAgent.id ? localAgent : agent
            );
            setAgents(updatedAgents);
            updateContextPersonas(updatedAgents);
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
        updateContextPersonas(updatedAgents);
    };

    const handleRemoveAgent = () => {
        if (selectedAgentId !== null) {
            const updatedAgents = agents.filter(agent => agent.id !== selectedAgentId);
            setAgents(updatedAgents);
            setSelectedAgentId(updatedAgents.length > 0 ? updatedAgents[0].id : null);
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
                <Card className="shadow-lg overflow-hidden">
                    <CardContent className='px-0'>
                        <div className="flex">
                            <div className={`${localAgent ? 'w-1/3' : 'w-full'} border-r border-gray-200`}>
                                <div className="p-4">
                                    <div className="space-y-2">
                                        {agents.map(agent => (
                                            <Button
                                                key={agent.id}
                                                variant={selectedAgentId === agent.id ? "secondary" : "ghost"}
                                                className="w-full justify-start py-3 h-12 px-4 rounded-lg transition-colors duration-200"
                                                onClick={() => handleAgentSelect(agent.id)}
                                            >
                                                <div className="flex items-center space-x-4">
                                                    <RandomAvatar className="h-10 w-10" name={`${agent.first_name} ${agent.last_name}`} />
                                                    <span className="font-medium">{`${agent.first_name} ${agent.last_name}`}</span>
                                                </div>
                                            </Button>
                                        ))}
                                    </div>
                                    <Button onClick={handleAddAgent} className="w-full mt-6 bg-indigo-500 hover:bg-indigo-600 text-white">
                                        <PlusCircle className="mr-2 h-4 w-4" /> 添加新智能体
                                    </Button>
                                </div>
                            </div>

                            {localAgent && (
                                <div className="w-2/3 bg-white">
                                    <div className="p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <div className="flex items-center space-x-4">
                                                <RandomAvatar
                                                    className="h-[80px] w-[80px]"
                                                    name={`${agents.find(a => a.id === localAgent.id)?.first_name} ${agents.find(a => a.id === localAgent.id)?.last_name}`}
                                                />
                                                <h2 className="text-2xl font-bold">{agents.find(a => a.id === localAgent.id)?.name}</h2>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">名字</label>
                                                <Input name="firstName" value={localAgent.first_name} onChange={handleInputChange} placeholder="名字" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">姓氏</label>
                                                <Input name="lastName" value={localAgent.last_name} onChange={handleInputChange} placeholder="姓氏" className="w-full" />
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
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">日常计划要求</label>
                                            <AutoResizeTextarea name="dailyPlanReq" value={localAgent.daily_plan_req} onChange={handleInputChange} placeholder="日常计划要求" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">固有特征</label>
                                            <AutoResizeTextarea name="innate" value={localAgent.innate} onChange={handleInputChange} placeholder="固有特征" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">学习信息</label>
                                            <AutoResizeTextarea name="learned" value={localAgent.learned} onChange={handleInputChange} placeholder="学习信息" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">居住区域</label>
                                            <Input name="livingArea" value={localAgent.living_area} onChange={handleInputChange} placeholder="居住区域" className="w-full" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">个人简介</label>
                                            <AutoResizeTextarea name="bibliography" value={localAgent.bibliography || ''} onChange={handleInputChange} placeholder="个人简介" className="w-full h-20" />
                                        </div>
                                        <div className="mt-6 flex justify-between items-center">
                                            <Button onClick={handleSave} className="bg-blue-500 hover:bg-blue-600 text-white">
                                                <Save className="mr-2 h-4 w-4" /> 保存更改
                                            </Button>
                                            <Button onClick={handleRemoveAgent} variant="destructive" className="bg-red-500 hover:bg-red-600 text-white">
                                                <Trash2 className="mr-2 h-4 w-4" /> 删除
                                            </Button>
                                        </div>
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