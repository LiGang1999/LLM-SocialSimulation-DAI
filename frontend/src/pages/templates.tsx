import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Navbar } from '@/components/Navbar';

import start2 from '@/assets/start2.jpg';
import { BottomNav } from '@/components/BottomNav';

import { useSimContext } from '@/SimContext';

// TODO Add background for this webpage

export const TemplatePage = () => {
    const [selectedTemplate, setSelectedTemplate] = useState(1);

    const templates = [
        {
            id: 1,
            name: 'Ecosystem Dynamics',
            image: start2,
            info1: 'Predator-Prey Model',
            info2: 'Population Cycles',
            description: 'Simulate interactions between species in a closed ecosystem.'
        },
        {
            id: 2,
            name: 'Climate Change',
            image: start2,
            info1: 'CO2 Emissions',
            info2: 'Temperature Trends',
            description: 'Model long-term climate patterns and human impact.'
        },
        {
            id: 3,
            name: 'Pandemic Spread',
            image: start2,
            info1: 'SIR Model',
            info2: 'Vaccination Strategies',
            description: 'Analyze disease transmission and intervention effectiveness.'
        },
        {
            id: 4,
            name: 'Urban Planning',
            image: start2,
            info1: 'Traffic Flow',
            info2: 'Resource Distribution',
            description: 'Optimize city layouts and infrastructure for efficiency.'
        },
    ];

    const handleSelectTemplate = (templateId: number) => {
        setSelectedTemplate(templateId === selectedTemplate ? 1 : templateId);
    };

    const ctx = useSimContext();

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <main className="container flex-grow mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">选择仿真模板</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {templates.map((template) => (
                        <Card
                            key={template.id}
                            className={`w-full rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-150 cursor-pointer ${selectedTemplate === template.id ? 'ring-4 ring-indigo-600 ring-offset-4' : ''
                                }`}
                            onClick={() => handleSelectTemplate(template.id)}
                        >
                            <img src={template.image} alt={template.name} className="w-full h-48 object-cover" />
                            <CardHeader className="p-4 bg-gradient-to-r from-purple-600 to-blue-500">
                                <CardTitle className="text-xl font-semibold text-white">{template.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="p-4">
                                <ul className="list-disc list-inside text-sm mb-2 text-gray-700">
                                    <li>{template.info1}</li>
                                    <li>{template.info2}</li>
                                </ul>
                                <p className="text-sm text-gray-600">{template.description}</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <BottomNav prevLink='/welcome' nextLink='/events' currStep={0} disabled={!selectedTemplate} className='mt-16'></BottomNav>
            </main>
        </div >
    );
};