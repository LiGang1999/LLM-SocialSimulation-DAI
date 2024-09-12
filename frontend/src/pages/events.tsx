import React, { useEffect, useState, useRef } from 'react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import { X, Plus, Edit, ChevronRight } from "lucide-react";
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { AutoResizeTextarea } from '@/components/autoResizeTextArea';

export interface Event {
    name: string;
    policy: string;
    websearch: string;
    description: string;
}

export const EventsPage = () => {
    const ctx = useSimContext();

    const [experimentName, setExperimentName] = useState(ctx.data.currSimCode || '');
    const [replicateCount, setReplicateCount] = useState(ctx.data.initialRounds?.toString() || '');
    const [events, setEvents] = useState<(Event & { id: number })[] | undefined>(
        ctx.data.currentTemplate?.events.map((event, index) => ({ ...event, id: index + 1 }))
    );

    const [selectedEvent, setSelectedEvent] = useState<(Event & { id: number }) | null>(null);
    const [nextEventId, setNextEventId] = useState(1);
    const [eventDescriptionError, setEventDescriptionError] = useState('');

    useEffect(() => {
        if (events && events.length > 0) {
            setNextEventId(Math.max(...events.map(e => e.id)) + 1);
        } else {
            setNextEventId(1);
        }
    }, [events]);


    const [errors, setErrors] = useState({
        experimentName: '',
        replicateCount: '',
    });

    useEffect(() => {
        const validateFields = () => {
            let newErrors = {
                experimentName: '',
                replicateCount: '',
            };

            if (experimentName.trim() === '') {
                newErrors.experimentName = '实验名称不能为空';
            } else if (ctx.data.allTemplates?.map(t => t.template_sim_code).includes(experimentName)) {
                newErrors.experimentName = '实验名称已存在';
            }

            const numValue = parseInt(replicateCount, 10);
            if (replicateCount.trim() === '') {
                newErrors.replicateCount = '初始仿真轮数不能为空';
            } else if (isNaN(numValue) || numValue < 0) {
                newErrors.replicateCount = '请输入有效的非负整数';
            }

            setErrors(newErrors);
        };

        validateFields();
    }, [experimentName, replicateCount, ctx.data.allTemplates]);

    const updateExperimentName = (value: string) => {
        setExperimentName(value);
        ctx.setData({
            ...ctx.data,
            currSimCode: value
        });
    };

    const updateReplicateCount = (value: string) => {
        setReplicateCount(value);
        const numValue = parseInt(value, 10);
        if (!isNaN(numValue) && numValue >= 0) {
            ctx.setData({
                ...ctx.data,
                initialRounds: numValue
            });
        } else {
            ctx.setData({
                ...ctx.data,
                initialRounds: undefined
            });
        }
    };

    const isFormValid = () => {
        const numValue = parseInt(replicateCount, 10);
        const allEventDescriptionsFilled = events?.every(event => event.description.trim() !== '');
        return experimentName.trim() !== '' &&
            !isNaN(numValue) &&
            numValue >= 0 &&
            !ctx.data.allTemplates?.map(t => t.template_sim_code).includes(experimentName) &&
            allEventDescriptionsFilled;
    };

    const addNewEvent = () => {
        const newEvent: Event & { id: number } = {
            id: nextEventId,
            name: `事件 ${nextEventId}`,
            policy: '',
            websearch: '',
            description: '',
        };
        setEvents([...events || [], newEvent]);
        setNextEventId(nextEventId + 1);
        setSelectedEvent(newEvent);
        setEventDescriptionError('事件描述不能为空');
        ctx.setData({
            ...ctx.data,
            currentTemplate: ctx.data.currentTemplate ? {
                ...ctx.data.currentTemplate,
                events: [...events || [], newEvent]
            } : undefined
        });
    };

    const removeEvent = (id: number) => {
        setEvents(events?.filter(event => event.id !== id));
        ctx.setData({
            ...ctx.data,
            currentTemplate: ctx.data.currentTemplate ? {
                ...ctx.data.currentTemplate,
                events: ctx.data.currentTemplate?.events.filter((event, index) => index + 1 !== id) || []
            } : undefined
        });
        if (selectedEvent && selectedEvent.id === id) {
            setSelectedEvent(null);
        }
    };

    const updateEvent = (field: keyof Event, value: string) => {
        if (selectedEvent) {
            const updatedEvent = { ...selectedEvent, [field]: value };
            setSelectedEvent(updatedEvent);
            setEvents(events?.map(e => e.id === selectedEvent.id ? updatedEvent : e));

            if (field === 'description') {
                if (value.trim() === '') {
                    setEventDescriptionError('事件描述不能为空');
                } else {
                    setEventDescriptionError('');
                }
            }

            ctx.setData({
                ...ctx.data,
                currentTemplate: ctx.data.currentTemplate ? {
                    ...ctx.data.currentTemplate,
                    events: events?.map((e, index) => index + 1 === selectedEvent.id ? updatedEvent : e) || []
                } : undefined
            });
        }
    };

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.templateCode && !ctx.data.currentTemplate) {
                    const templateData = await apis.fetchTemplate(ctx.data.templateCode);
                    const events = templateData.events.map((value, index) => ({
                        ...value,
                        id: index + 1,
                        name: value.name || `事件 ${index + 1}`
                    }));
                    ctx.setData({
                        ...ctx.data,
                        currentTemplate: {
                            ...templateData,
                            events: events
                        }
                    });
                    setEvents(events);
                }
            } catch (err) {
                console.error("Failed to fetch template detail:", err);
            }
        }

        fetchTemplates();
    }, []);

    return (
        <div className="flex flex-col min-h-screen bg-gray-100">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 2.</span>方案设计</h2>
                <Card className="shadow-lg">
                    <CardContent className='pt-8'>
                        <div className="grid md:grid-cols-2 gap-8">
                            <div className="space-y-6">
                                <div className='grid grid-cols-2 gap-4'>
                                    <div>
                                        <label htmlFor="experimentName" className="block text-sm font-medium text-gray-700 mb-1">实验名称</label>
                                        <Input
                                            id="experimentName"
                                            value={experimentName}
                                            onChange={(e) => updateExperimentName(e.target.value)}
                                            placeholder="请输入实验名称"
                                            className={`w-full ${errors.experimentName ? 'border-red-500' : ''}`}
                                        />
                                        {errors.experimentName && <p className="text-red-500 text-xs mt-1">{errors.experimentName}</p>}
                                    </div>

                                    <div>
                                        <label htmlFor="replicateCount" className="block text-sm font-medium text-gray-700 mb-1">初始仿真轮数</label>
                                        <div className="flex items-center">
                                            <Input
                                                id="replicateCount"
                                                type="number"
                                                min="1"
                                                step="1"
                                                value={replicateCount}
                                                onChange={(e) => updateReplicateCount(e.target.value)}
                                                placeholder="请输入仿真轮数"
                                                className={`mr-2 ${errors.replicateCount ? 'border-red-500' : ''}`}
                                            />
                                            <span className="text-gray-600">轮</span>
                                        </div>
                                        {errors.replicateCount && <p className="text-red-500 text-xs mt-1">{errors.replicateCount}</p>}
                                    </div>
                                </div>

                                <div>
                                    <h3 className="text-lg font-semibold text-gray-700 mb-3">事件列表</h3>
                                    <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
                                        <div className="space-y-2 max-h-80 overflow-y-auto pr-2">
                                            {events?.map((event) => (
                                                <div
                                                    key={event.id}
                                                    className={`flex items-center justify-between p-3 rounded-lg transition-shadow ${selectedEvent && selectedEvent.id === event.id
                                                        ? 'bg-blue-200'
                                                        : event.description.trim() === ''
                                                            ? 'bg-red-100'
                                                            : 'bg-indigo-50'
                                                        }`}
                                                >
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
                                    </div>
                                    <Button
                                        variant="outline"
                                        className="w-full justify-center text-blue-600 mt-4 hover:bg-blue-50"
                                        onClick={addNewEvent}
                                    >
                                        <Plus className="h-4 w-4 mr-2" /> 添加新事件
                                    </Button>
                                </div>
                            </div>

                            <div className="bg-indigo-50 p-6 rounded-lg">
                                <h3 className="text-lg font-semibold text-gray-700 mb-4">事件详情</h3>
                                {selectedEvent ? (
                                    <div className="space-y-4">
                                        <div>
                                            <label htmlFor="eventDescription" className="block text-sm font-medium text-gray-700 mb-1">事件描述</label>
                                            <AutoResizeTextarea
                                                id="eventDescription"
                                                value={selectedEvent.description}
                                                onChange={(e) => updateEvent('description', e.target.value)}
                                                placeholder="请输入事件描述"
                                                rows={3}
                                                className={selectedEvent.description == '' ? 'border-red-500' : ''}
                                            />
                                            {selectedEvent.description == '' && <p className="text-red-500 text-xs mt-1">{eventDescriptionError}</p>}
                                        </div>
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
                                            <label htmlFor="eventPolicy" className="block text-sm font-medium text-gray-700 mb-1">事件政策</label>
                                            <AutoResizeTextarea
                                                id="eventPolicy"
                                                value={selectedEvent.policy}
                                                onChange={(e) => updateEvent('policy', e.target.value)}
                                                placeholder="请输入事件政策"
                                                rows={3}
                                            />
                                        </div>
                                        <div>
                                            <label htmlFor="eventWebsearch" className="block text-sm font-medium text-gray-700 mb-1">网络搜索</label>
                                            <AutoResizeTextarea
                                                id="eventWebsearch"
                                                value={selectedEvent.websearch}
                                                onChange={(e) => updateEvent('websearch', e.target.value)}
                                                placeholder="请输入事件政策"
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
                <BottomNav
                    prevLink='/templates'
                    nextLink='/agents'
                    currStep={1}
                    disabled={!isFormValid()}
                    className='my-8'
                />
            </div>
        </div>
    );
}