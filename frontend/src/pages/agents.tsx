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

interface Agent {
    id: number;
    name: string;
    firstName: string;
    lastName: string;
    age: number;
    dailyPlanReq: string;
    innate: string;
    learned: string;
    avatar: string;
}

const initialAgents: Agent[] = [
    {
        id: 1,
        name: 'Isabella Rodriguez',
        firstName: 'Isabella',
        lastName: 'Rodriguez',
        age: 34,
        dailyPlanReq: 'Isabella Rodriguez opens Hobbs Cafe at 8am everyday, and works at the counter until 8pm, at which point she closes the cafe.',
        innate: 'friendly, outgoing, hospitable',
        learned: 'Isabella Rodriguez is a cafe owner of Hobbs Cafe who loves to make people feel welcome. She is always looking for ways to make the cafe a place where people can come to relax and enjoy themselves. She is concerned with environmental issues and big global events, although she does not have professional knowledge in these areas.',
        avatar: '/api/placeholder/40/40'
    },
    { id: 2, name: 'Maria Lopez', firstName: 'Maria', lastName: 'Lopez', age: 0, dailyPlanReq: '', innate: '', learned: '', avatar: '/api/placeholder/40/40' },
    { id: 3, name: 'Klaus Mueller', firstName: 'Klaus', lastName: 'Mueller', age: 0, dailyPlanReq: '', innate: '', learned: '', avatar: '/api/placeholder/40/40' },
];

export const AgentsPage = () => {
    const ctx = useSimContext();

    const [agents, setAgents] = useState<Agent[]>(initialAgents);
    const [selectedAgent, setSelectedAgent] = useState<Agent | null>(agents[0]);

    const handleAgentSelect = (agent: Agent) => {
        setSelectedAgent(agent);
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        if (selectedAgent) {
            setSelectedAgent({ ...selectedAgent, [e.target.name]: e.target.value });
        }
    };

    const handleSave = () => {
        if (selectedAgent) {
            setAgents(agents.map(agent => agent.id === selectedAgent.id ? selectedAgent : agent));
        }
    };

    const handleAddAgent = () => {
        const newAgent: Agent = {
            id: agents.length + 1,
            name: 'New Agent',
            firstName: '',
            lastName: '',
            age: 0,
            dailyPlanReq: '',
            innate: '',
            learned: '',
            avatar: '/api/placeholder/40/40'
        };
        setAgents([...agents, newAgent]);
        setSelectedAgent(newAgent);
    };

    const handleRemoveAgent = () => {
        if (selectedAgent) {
            const updatedAgents = agents.filter(agent => agent.id !== selectedAgent.id);
            setAgents(updatedAgents);
            setSelectedAgent(updatedAgents.length > 0 ? updatedAgents[0] : null);
        }
    };


    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.currSimCode && !ctx.data.currentTemplate) {
                    // should fetch the template data!
                    const templateData = await apis.fetchTemplate(ctx.data.currSimCode);
                    ctx.setData({
                        ...ctx.data,
                        currentTemplate: templateData
                    })
                }
            } catch (err) {
                console.error("Failed to fetch template detail:", err);
            }
        }

        fetchTemplates();
    }, [])


    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">自定义智能体</h2>
                <Card className="shadow-lg overflow-hidden">
                    {/* <CardHeader className="bg-white">
                        <CardTitle className="text-3xl font-semibold">自定义您的智能体</CardTitle>
                    </CardHeader> */}
                    <CardContent className='px-0'>
                        <div className="flex">
                            <div className={`${selectedAgent ? 'w-1/3' : 'w-full'} border-r border-gray-200`}>
                                <div className="p-4">
                                    <div className="space-y-2">
                                        {agents.map(agent => (
                                            <Button
                                                key={agent.id}
                                                variant={selectedAgent?.id === agent.id ? "secondary" : "ghost"}
                                                className="w-full justify-start py-3 px-4 rounded-lg transition-colors duration-200"
                                                onClick={() => handleAgentSelect(agent)}
                                            >
                                                <div className="flex items-center space-x-4">
                                                    <Avatar className="h-10 w-10">
                                                        <AvatarImage src={agent.avatar} alt={agent.name} />
                                                        <AvatarFallback>{agent.firstName[0]}{agent.lastName[0]}</AvatarFallback>
                                                    </Avatar>
                                                    <span className="font-medium">{agent.name}</span>
                                                </div>
                                            </Button>
                                        ))}
                                    </div>
                                    <Button onClick={handleAddAgent} className="w-full mt-6 bg-green-500 hover:bg-green-600 text-white">
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
                                                    <AvatarImage src={selectedAgent.avatar} alt={selectedAgent.name} />
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
                                                <label className="block text-sm font-medium text-gray-700 mb-1">Avatar URL</label>
                                                <Input name="avatar" value={selectedAgent.avatar} onChange={handleInputChange} placeholder="Avatar URL" className="w-full" />
                                            </div>
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Daily Plan Requirements</label>
                                            <Textarea name="dailyPlanReq" value={selectedAgent.dailyPlanReq} onChange={handleInputChange} placeholder="Daily Plan Requirements" className="w-full h-12" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Innate Characteristics</label>
                                            <Input name="innate" value={selectedAgent.innate} onChange={handleInputChange} placeholder="Innate Characteristics" className="w-full" />
                                        </div>
                                        <div className="mt-4">
                                            <label className="block text-sm font-medium text-gray-700 mb-1">Learned Information</label>
                                            <Textarea name="learned" value={selectedAgent.learned} onChange={handleInputChange} placeholder="Learned Information" className="w-full h-12" />
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