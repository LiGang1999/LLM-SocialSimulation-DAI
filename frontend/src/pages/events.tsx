import React, { useState } from 'react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { X, Plus, Edit, ChevronRight } from "lucide-react";

interface Event {
    id: number;
    name: string;
    policies: string;
    websearchResult: string;
    description: string;
}

export const EventsPage = () => {
    const [experimentName, setExperimentName] = useState('');
    const [replicateCount, setReplicateCount] = useState('');
    const [events, setEvents] = useState<Event[]>([
        { id: 1, name: '事件 1', policies: '', websearchResult: '', description: '' },
        { id: 2, name: '事件 2', policies: '', websearchResult: '', description: '' },
    ]);
    const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);

    const addNewEvent = () => {
        const newEvent = {
            id: events.length + 1,
            name: `事件 ${events.length + 1}`,
            policies: '',
            websearchResult: '',
            description: '',
        };
        setEvents([...events, newEvent]);
    };

    const removeEvent = (id: number) => {
        setEvents(events.filter(event => event.id !== id));
        if (selectedEvent && selectedEvent.id === id) {
            setSelectedEvent(null);
        }
    };

    const updateEvent = (field: keyof Event, value: string) => {
        if (selectedEvent) {
            const updatedEvent = { ...selectedEvent, [field]: value };
            setSelectedEvent(updatedEvent);
            setEvents(events.map(e => e.id === selectedEvent.id ? updatedEvent : e));
        }
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">方案设计</h2>
                <Card className="shadow-lg">
                    {/* <CardHeader className='border-b border-gray-200 py-8'>
                        <CardTitle className="text-4xl font-semibold text-black-800">方案设计</CardTitle>
                    </CardHeader> */}
                    <CardContent className='pt-8'>
                        <div className="grid md:grid-cols-2  gap-8">
                            <div className="space-y-6">
                                <div className='grid grid-cols-2 gap-4'>
                                    <div>
                                        <label htmlFor="experimentName" className="block text-sm font-medium text-gray-700 mb-1">实验名称</label>
                                        <Input
                                            id="experimentName"
                                            value={experimentName}
                                            onChange={(e) => setExperimentName(e.target.value)}
                                            placeholder="请输入实验名称"
                                            className="w-full"
                                        />
                                    </div>

                                    <div>
                                        <label htmlFor="replicateCount" className="block text-sm font-medium text-gray-700 mb-1">初始仿真轮数</label>
                                        <div className="flex items-center">
                                            <Input
                                                id="replicateCount"
                                                value={replicateCount}
                                                onChange={(e) => setReplicateCount(e.target.value)}
                                                placeholder="请输入仿真轮数"
                                                className="mr-2"
                                            />
                                            <span className="text-gray-600">轮</span>
                                        </div>
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold text-gray-700 mb-3">事件列表</h3>
                                    <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
                                        {events.map((event) => (
                                            <div key={event.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg transition-shadow">
                                                <span className="text-gray-700 font-medium">{event.name}</span>
                                                <div>
                                                    <Button variant="ghost" size="sm" onClick={() => setSelectedEvent(event)} className="text-blue-500 hover:text-blue-700">
                                                        <Edit className="h-4 w-4 mr-1" /> 编辑
                                                    </Button>
                                                    <Button variant="ghost" size="sm" onClick={() => removeEvent(event.id)} className="text-red-500 hover:text-red-700">
                                                        <X className="h-4 w-4 mr-1" /> 删除
                                                    </Button>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                    <Button
                                        variant="outline"
                                        className="w-full justify-center text-blue-600 mt-4 hover:bg-blue-50"
                                        onClick={addNewEvent}
                                    >
                                        <Plus className="mr-2 h-4 w-4" /> 添加新事件
                                    </Button>
                                </div>
                            </div>

                            <div className="bg-gray-50 p-6 rounded-lg">
                                <h3 className="text-lg font-semibold text-gray-700 mb-4">事件详情</h3>
                                {selectedEvent ? (
                                    <div className="space-y-4">
                                        <div>
                                            <label htmlFor="eventName" className="block text-sm font-medium text-gray-700 mb-1">事件名称</label>
                                            <Input
                                                id="eventName"
                                                value={selectedEvent.name}
                                                onChange={(e) => updateEvent('name', e.target.value)}
                                                placeholder="请输入事件名称"
                                            />
                                        </div>
                                        <div>
                                            <label htmlFor="eventPolicies" className="block text-sm font-medium text-gray-700 mb-1">事件政策</label>
                                            <Textarea
                                                id="eventPolicies"
                                                value={selectedEvent.policies}
                                                onChange={(e) => updateEvent('policies', e.target.value)}
                                                placeholder="请输入事件政策"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label htmlFor="eventWebsearch" className="block text-sm font-medium text-gray-700 mb-1">网络搜索结果</label>
                                            <Textarea
                                                id="eventWebsearch"
                                                value={selectedEvent.websearchResult}
                                                onChange={(e) => updateEvent('websearchResult', e.target.value)}
                                                placeholder="请输入网络搜索结果"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label htmlFor="eventDescription" className="block text-sm font-medium text-gray-700 mb-1">事件描述</label>
                                            <Textarea
                                                id="eventDescription"
                                                value={selectedEvent.description}
                                                onChange={(e) => updateEvent('description', e.target.value)}
                                                placeholder="请输入事件描述"
                                                rows={3}
                                            />
                                        </div>
                                    </div>
                                ) : (
                                    <p className="text-gray-500 text-center">请选择一个事件来查看和编辑详情</p>
                                )}
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/templates' nextLink='/agents' currStep={1} disabled={false} className='my-8' />
            </div>
        </div>
    );
}