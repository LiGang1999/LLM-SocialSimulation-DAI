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

const mockAgents: (apis.Agent & { id: number })[] = [
    {
        id: 1,
        name: 'Isabella Rodriguez',
        firstName: 'Isabella',
        lastName: 'Rodriguez',
        age: 34,
        dailyPlanReq: 'Isabella Rodriguez opens Hobbs Cafe at 8am everyday, and works at the counter until 8pm, at which point she closes the cafe.',
        innate: 'friendly, outgoing, hospitable',
        learned: 'Isabella Rodriguez is a cafe owner of Hobbs Cafe who loves to make people feel welcome. She is always looking for ways to make the cafe a place where people can come to relax and enjoy themselves. She is concerned with environmental issues and big global events, although she does not have professional knowledge in these areas.',
        currently: undefined,
        lifestyle: 'Busy cafe owner, health-conscious',
        livingArea: 'Small apartment above Hobbs Cafe',
        plan: undefined,
        memory: undefined,
        bibliography: 'Local business owner, community pillar'
    },
    // Add more mock agents if needed
    {
        id: 2,
        name: 'Marcus Chen',
        firstName: 'Marcus',
        lastName: 'Chen',
        age: 28,
        dailyPlanReq: 'Marcus Chen starts his day at 7am with a morning run. He works as a software developer from 9am to 6pm, with a lunch break at noon. After work, he often attends local tech meetups or works on personal coding projects until around 10pm.',
        innate: 'analytical, introverted, creative',
        learned: 'Marcus Chen is a talented software developer who specializes in AI and machine learning. He\'s passionate about technology and its potential to solve complex problems.He\'s also an advocate for open - source software and contributes to several projects in his free time.',
        currently: undefined,
        lifestyle: 'Tech-savvy, fitness enthusiast',
        livingArea: 'Modern studio apartment in the city center',
        plan: undefined,
        memory: undefined,
        bibliography: 'Rising star in the local tech scene'
    },
    {
        id: 3,
        name: 'Aisha Patel',
        firstName: 'Aisha',
        lastName: 'Patel',
        age: 42,
        dailyPlanReq: 'Aisha Patel begins her day at 6am with yoga and meditation. She sees patients at her clinic from 9am to 5pm, with a break for lunch and paperwork. In the evenings, she often volunteers at a local community health center or attends medical conferences.',
        innate: 'empathetic, detail-oriented, calm',
        learned: 'Aisha Patel is a respected pediatrician with over 15 years of experience. She\'s known for her holistic approach to healthcare, combining Western medicine with traditional practices.She\'s actively involved in public health initiatives and regularly gives talks on child nutrition and preventive care.',
        currently: undefined,
        lifestyle: 'Health-focused, community-oriented',
        livingArea: 'Spacious family home in a quiet suburb',
        plan: undefined,
        memory: undefined,
        bibliography: 'Renowned pediatrician and public health advocate'
    },
];

export const AgentsPage = () => {
    const ctx = useSimContext();

    const [agents, setAgents] = useState<(apis.Agent & { id: number })[]>([]);
    const [selectedAgentId, setSelectedAgentId] = useState<number | null>(null);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.currSimCode && !ctx.data.currentTemplate) {
                    const templateData = await apis.fetchTemplate(ctx.data.currSimCode);
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
        } else {
            setAgents(mockAgents);
            setSelectedAgentId(mockAgents[0].id);
        }
    }, [ctx.data.currentTemplate]);

    const handleAgentSelect = (id: number) => {
        setSelectedAgentId(id);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        if (selectedAgentId !== null) {
            setAgents(agents.map(agent =>
                agent.id === selectedAgentId
                    ? { ...agent, [e.target.name]: e.target.value }
                    : agent
            ));
        }
    };

    const handleSave = () => {
        updateContextPersonas(agents);
    };

    const handleAddAgent = () => {
        const newId = Math.max(...agents.map(a => a.id), 0) + 1;
        const newAgent: apis.Agent & { id: number } = {
            id: newId,
            name: 'New Agent',
            firstName: '',
            lastName: '',
            age: 0,
            dailyPlanReq: '',
            innate: '',
            learned: '',
            currently: undefined,
            lifestyle: '',
            livingArea: '',
            plan: undefined,
            memory: undefined,
            bibliography: ''
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

    const selectedAgent = agents.find(agent => agent.id === selectedAgentId);

    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">自定义智能体</h2>
                <Card className="shadow-lg overflow-hidden">
                    <CardContent className='px-0'>
                        <div className="flex">
                            <div className={`${selectedAgent ? 'w-1/3' : 'w-full'} border-r border-gray-200`}>
                                <div className="p-4">
                                    <div className="space-y-2">
                                        {agents.map(agent => (
                                            <Button
                                                key={agent.id}
                                                variant={selectedAgentId === agent.id ? "secondary" : "ghost"}
                                                className="w-full justify-start py-3 px-4 rounded-lg transition-colors duration-200"
                                                onClick={() => handleAgentSelect(agent.id)}
                                            >
                                                <div className="flex items-center space-x-4">
                                                    <Avatar className="h-10 w-10">
                                                        <AvatarFallback>{agent.firstName[0]}{agent.lastName[0]}</AvatarFallback>
                                                    </Avatar>
                                                    <span className="font-medium">{`${agent.firstName} ${agent.lastName}`}</span>
                                                </div>
                                            </Button>
                                        ))}
                                    </div>
                                    <Button onClick={handleAddAgent} className="w-full mt-6 bg-indigo-500 hover:bg-indigo-600 text-white">
                                        <PlusCircle className="mr-2 h-4 w-4" /> 添加新智能体
                                    </Button>
                                </div>
                            </div>

                            {selectedAgent && (
                                <div className="w-2/3 bg-white">
                                    <div className="p-6">
                                        <div className="flex items-center justify-between mb-6">
                                            <div className="flex items-center space-x-4">
                                                <Avatar className="h-16 w-16">
                                                    <AvatarFallback>{selectedAgent.firstName[0]}{selectedAgent.lastName[0]}</AvatarFallback>
                                                </Avatar>
                                                <h2 className="text-2xl font-bold">{selectedAgent.name}</h2>
                                            </div>
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                                                <Input name="firstName" value={selectedAgent.firstName} onChange={handleInputChange} placeholder="First Name" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                                                <Input name="lastName" value={selectedAgent.lastName} onChange={handleInputChange} placeholder="Last Name" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Age</label>
                                                <Input name="age" type="number" value={selectedAgent.age} onChange={handleInputChange} placeholder="Age" className="w-full" />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Lifestyle</label>
                                                <Input name="lifestyle" value={selectedAgent.lifestyle} onChange={handleInputChange} placeholder="Lifestyle" className="w-full" />
                                            </div>
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Daily Plan Requirements</label>
                                            <Textarea name="dailyPlanReq" value={selectedAgent.dailyPlanReq} onChange={handleInputChange} placeholder="Daily Plan Requirements" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Innate Characteristics</label>
                                            <Textarea name="innate" value={selectedAgent.innate} onChange={handleInputChange} placeholder="Innate Characteristics" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Learned Information</label>
                                            <Textarea name="learned" value={selectedAgent.learned} onChange={handleInputChange} placeholder="Learned Information" className="w-full h-20" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Living Area</label>
                                            <Input name="livingArea" value={selectedAgent.livingArea} onChange={handleInputChange} placeholder="Living Area" className="w-full" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Bibliography</label>
                                            <Textarea name="bibliography" value={selectedAgent.bibliography} onChange={handleInputChange} placeholder="Bibliography" className="w-full h-20" />
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