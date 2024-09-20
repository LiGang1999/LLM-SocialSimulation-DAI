import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar"
import { BottomNav } from "@/components/BottomNav"
import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { PlusCircle, Trash2 } from 'lucide-react'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { RandomAvatar } from '@/components/Avatars';
import { AutoResizeTextarea } from '@/components/autoResizeTextArea';
import DescriptionCard from '@/components/DescriptionCard';
import { InfoTooltip } from '@/components/Tooltip';

import backgroundImage from '@/assets/Untitled.png'


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
    const [errors, setErrors] = useState<{ [agentId: number]: { [field: string]: string } }>({});
    const [nextAgentNumber, setNextAgentNumber] = useState<number>(1);

    const validateAgent = (agent: apis.Agent) => {
        const agentErrors: { [field: string]: string } = {};
        if (!agent.first_name || agent.first_name.trim() === '') {
            agentErrors['first_name'] = 'First name is required.';
        }
        if (!agent.last_name || agent.last_name.trim() === '') {
            agentErrors['last_name'] = 'Last name is required.';
        }
        if (!agent.innate || agent.innate.trim() === '') {
            agentErrors['innate'] = 'Innate characteristics are required.';
        }
        if (!agent.daily_plan_req || agent.daily_plan_req.trim() === '') {
            agentErrors['daily_plan_req'] = 'Daily plan requirements are required.';
        }
        if (!agent.learned || agent.learned.trim() === '') {
            agentErrors['learned'] = 'Learned information is required.';
        }
        return agentErrors;
    };


    useEffect(() => {
        // Validate all agents whenever agents change
        const newErrors: { [agentId: number]: { [field: string]: string } } = {};
        for (const agent of agents) {
            const agentErrors = validateAgent(agent);
            if (Object.keys(agentErrors).length > 0) {
                newErrors[agent.id] = agentErrors;
            }
        }
        setErrors(newErrors);
    }, [agents]);


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
            setNextAgentNumber(agentsWithId.length + 1);
            // If current selected Agent id is within all ids:
            if (!(selectedAgentId && agentsWithId.map(a => a.id).includes(selectedAgentId))) {
                setSelectedAgentId(agentsWithId[0].id);

            }
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
            const { name, value } = e.target;
            let updatedAgent = { ...localAgent, [name]: value };

            if (name === 'first_name' || name === 'last_name') {
                updatedAgent.name = `${updatedAgent.first_name} ${updatedAgent.last_name}`.trim();
            }

            setLocalAgent(updatedAgent);

            setAgents(prevAgents =>
                prevAgents.map(agent =>
                    agent.id === updatedAgent.id ? updatedAgent : agent
                )
            );

            updateContextPersonas(agents.map(agent =>
                agent.id === updatedAgent.id ? updatedAgent : agent
            ));

            // Validate agent and update errors
            const agentErrors = validateAgent(updatedAgent);
            setErrors(prevErrors => {
                const newErrors = { ...prevErrors };
                if (Object.keys(agentErrors).length > 0) {
                    newErrors[updatedAgent.id] = agentErrors;
                } else {
                    delete newErrors[updatedAgent.id];
                }
                return newErrors;
            });
        }
    };



    const handleAddAgent = () => {
        const newId = nextAgentNumber;
        const newName = `Agent ${newId}`;

        const newAgent: apis.Agent & { id: number } = {
            id: newId,
            curr_time: undefined,
            curr_tile: undefined,
            daily_plan_req: '',
            name: newName,
            first_name: 'Agent',
            last_name: `${newId}`,
            age: 0,
            innate: '',
            learned: '',
            currently: '',
            lifestyle: '',
            living_area: '',
            daily_req: [],
            f_daily_schedule: [],
            f_daily_schedule_hourly_org: [],
            act_address: undefined,
            act_start_time: undefined,
            act_duration: undefined,
            act_description: undefined,
            act_pronunciatio: undefined,
            act_event: [newName, undefined, undefined],
            act_obj_description: undefined,
            act_obj_pronunciatio: undefined,
            act_obj_event: [undefined, undefined, undefined],
            chatting_with: undefined,
            chat: undefined,
            chatting_with_buffer: {},
            chatting_end_time: undefined,
            act_path_set: false,
            planned_path: [],
            // Additional fields from your original mapping
            plan: [],
            memory: [],
            bibliography: '',
        };

        const updatedAgents = [...agents, newAgent];
        setAgents(updatedAgents);
        setSelectedAgentId(newId);
        setNextAgentNumber(nextAgentNumber + 1);
        updateContextPersonas(updatedAgents);

        // Validate new agent and update errors
        const agentErrors = validateAgent(newAgent);
        setErrors(prevErrors => {
            if (Object.keys(agentErrors).length > 0) {
                return { ...prevErrors, [newAgent.id]: agentErrors };
            } else {
                return prevErrors;
            }
        });
    };

    const handleRemoveAgent = (agentId: number) => {
        const updatedAgents = agents.filter(agent => agent.id !== agentId);
        setAgents(updatedAgents);
        setSelectedAgentId(updatedAgents.length > 0 ? updatedAgents[0].id : null);
        updateContextPersonas(updatedAgents);

        // Remove errors related to the deleted agent
        setErrors(prevErrors => {
            const { [agentId]: _, ...rest } = prevErrors;
            return rest;
        });

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

    const isNextDisabled = Object.keys(errors).length > 0 || agents.length === 0;

    return (
        <div className="flex flex-col min-h-screen bg-gray-100" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 3.</span>自定义智能体</h2>

                <DescriptionCard
                    title="配置仿真智能体"
                    description="您可以自定义社会仿真实验中的各个智能体。您可以添加新的智能体，编辑现有智能体的各项属性，如姓名、年龄、性格特征、日常计划、生活方式和居住区域等。这些设置将决定智能体在仿真中的行为模式、互动方式和决策过程。通过精心配置这些参数，您可以创建更真实、更丰富的仿真环境，从而获得更有价值的实验结果。"
                />


                <Card className="bg-opacity-70 bg-white overflow-hidden">
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
                                                            <AlertDialogTitle>您确定要删除这个智能体吗？</AlertDialogTitle>
                                                            <AlertDialogDescription>
                                                                该操作无法撤销。数据将从服务器上永远清除。
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
                                <div className="w-2/3 p-6">
                                    <div className="flex items-center justify-between mb-6">
                                        <div className="flex items-center space-x-6">
                                            <RandomAvatar
                                                className="h-24 w-24 rounded-full"
                                                name={`${localAgent.first_name} ${localAgent.last_name}`}
                                            />
                                            <h1 className="text-3xl font-bold">{`${localAgent.first_name} ${localAgent.last_name}`}</h1>
                                        </div>
                                    </div>
                                    <div className="grid grid-cols-2 gap-6">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">姓氏</label>
                                            <Input
                                                name="first_name"
                                                value={localAgent.first_name}
                                                onChange={handleInputChange}
                                                placeholder="First Name"
                                                className={`w-full ${errors[localAgent.id]?.first_name ? 'border-red-500' : ''}`}
                                            />
                                            {errors[localAgent.id]?.first_name && <p className="text-red-500 text-sm mt-1">{errors[localAgent.id]?.first_name}</p>}
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">名字</label>
                                            <Input
                                                name="last_name"
                                                value={localAgent.last_name}
                                                onChange={handleInputChange}
                                                placeholder="Last Name"
                                                className={`w-full ${errors[localAgent.id]?.last_name ? 'border-red-500' : ''}`}
                                            />
                                            {errors[localAgent.id]?.last_name && <p className="text-red-500 text-sm mt-1">{errors[localAgent.id]?.last_name}</p>}
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">年龄</label>
                                            <Input name="age" type="number" value={localAgent.age} onChange={handleInputChange} placeholder="Age" className="w-full" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-1">生活方式</label>
                                            <Input name="lifestyle" value={localAgent.lifestyle} onChange={handleInputChange} placeholder="Lifestyle" className="w-full" />
                                        </div>
                                    </div>
                                    <div className="mt-6">
                                        <div className="flex items-center align-center space-x-2 mb-1 relative">
                                            <label className="block text-sm font-medium text-gray-700">每日计划要求</label>
                                            <InfoTooltip message='a1' />
                                        </div>
                                        <AutoResizeTextarea
                                            name="daily_plan_req"
                                            value={localAgent.daily_plan_req}
                                            onChange={handleInputChange}
                                            placeholder="Daily Plan Requirements"
                                            className={`w-full min-h-[80px] ${errors[localAgent.id]?.daily_plan_req ? 'border-red-500' : ''}`}
                                        />
                                        {errors[localAgent.id]?.daily_plan_req && <p className="text-red-500 text-sm mt-1">{errors[localAgent.id]?.daily_plan_req}</p>}
                                    </div>
                                    <div className="mt-6">
                                        <div className="flex items-center align-center space-x-2 mb-1 relative">
                                            <label className="block text-sm font-medium text-gray-700">内在性格</label>
                                            <InfoTooltip message='a1' />
                                        </div>
                                        <AutoResizeTextarea
                                            name="innate"
                                            value={localAgent.innate}
                                            onChange={handleInputChange}
                                            placeholder="Innate Characteristics"
                                            className={`w-full min-h-[80px] ${errors[localAgent.id]?.innate ? 'border-red-500' : ''}`}
                                        />
                                        {errors[localAgent.id]?.innate && <p className="text-red-500 text-sm mt-1">{errors[localAgent.id]?.innate}</p>}
                                    </div>
                                    <div className="mt-6">
                                        <div className="flex items-center align-center space-x-2 mb-1 relative">
                                            <label className="block text-sm font-medium text-gray-700">当前处境</label>
                                            <InfoTooltip message='a2' />
                                        </div>
                                        <AutoResizeTextarea
                                            name="learned"
                                            value={localAgent.learned}
                                            onChange={handleInputChange}
                                            placeholder="Learned Information"
                                            className={`w-full min-h-[80px] ${errors[localAgent.id]?.learned ? 'border-red-500' : ''}`}
                                        />
                                        {errors[localAgent.id]?.learned && <p className="text-red-500 text-sm mt-1">{errors[localAgent.id]?.learned}</p>}
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">居住区域</label>
                                        <Input name="living_area" value={localAgent.living_area} onChange={handleInputChange} placeholder="Living Area" className="w-full" />
                                    </div>
                                    <div className="mt-6">
                                        <label className="block text-sm font-medium text-gray-700 mb-1">生平</label>
                                        <AutoResizeTextarea name="bibliography" value={localAgent.bibliography || ''} onChange={handleInputChange} placeholder="Bibliography" className="w-full min-h-[80px]" />
                                    </div>
                                </div>
                            )}
                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/events' nextLink='/llmconfig' currStep={2} disabled={isNextDisabled} className='my-8' />
            </div>
        </div>
    )
}