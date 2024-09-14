import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Navbar } from '@/components/Navbar';

import start1 from '@/assets/template2.png';
import chat from '@/assets/chat.png';
import stf from '@/assets/start2.jpg'

import { ProgressBar } from '@/components/ProgressBar';
import { BottomNav } from '@/components/BottomNav';


import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { InfoIcon } from 'lucide-react';
import DescriptionCard from '@/components/DescriptionCard';

// TODO Add background for this webpage
const getTemplateImage = (template: apis.TemplateListItem) => {
    if (template.template_sim_code === 'base_the_ville_isabella_maria_klaus_online') {
        return chat;
    } else if (template.template_sim_code === 'base_the_ville_isabella_maria_klaus') {
        return start1;
    }
    else if (template.template_sim_code === 'base_the_ville_n25') {
        return stf;
    }
}

const mockTemplates: apis.TemplateListItem[] = [
    {
        template_sim_code: "ecosystem_dynamics",
        name: "Ecosystem Dynamics",
        bullets: ["Predator-Prey Model", "Population Cycles"],
        description: "Simulate interactions between species in a closed ecosystem.",
        start_date: "2023-09-04",
        curr_time: "2023-09-04 00:00:00",
        sec_per_step: 10,
        maze_name: "ecosystem",
        persona_names: ["Wolf", "Rabbit", "Grass"],
        step: 0,
        sim_mode: "online"
    },
    {
        template_sim_code: "climate_change",
        name: "Climate Change",
        bullets: ["CO2 Emissions", "Temperature Trends"],
        description: "Model long-term climate patterns and human impact on global temperatures.",
        start_date: "2023-09-05",
        curr_time: "2023-09-05 00:00:00",
        sec_per_step: 86400, // 1 day per step
        maze_name: "earth",
        persona_names: ["Scientist", "Policymaker", "Industrialist"],
        step: 0,
        sim_mode: "online"
    },
    {
        template_sim_code: "pandemic_spread",
        name: "Pandemic Spread",
        bullets: ["SIR Model", "Vaccination Strategies"],
        description: "Analyze disease transmission and intervention effectiveness in a population.",
        start_date: "2023-09-06",
        curr_time: "2023-09-06 00:00:00",
        sec_per_step: 3600, // 1 hour per step
        maze_name: "city",
        persona_names: ["Doctor", "Patient", "Health Official"],
        step: 0,
        sim_mode: "online"
    }
];


export const TemplatePage = () => {
    const ctx = useSimContext();


    const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
    const [templates, setTemplates] = useState<apis.TemplateListItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const fetchedTemplates = await apis.fetchTemplates();
                setTemplates(fetchedTemplates.envs);
                setIsLoading(false);
                ctx.setData(
                    {
                        ...ctx.data,
                        allTemplates: fetchedTemplates.envs,
                        allEnvs: fetchedTemplates.all_templates
                    }
                )
            } catch (err) {
                console.error("Failed to fetch templates:", err);
                setTemplates(mockTemplates);
                setIsLoading(false);
            }
        };

        fetchTemplates();

        if (ctx.data.templateCode) {
            setSelectedTemplate(ctx.data.templateCode)
        }
    }, []);


    // Lesson lerant from this: You should never call a setState twice at one place, otherwise there will be race conditions
    const handleSelectTemplate = (templateCode: string) => {
        const updatedData = {
            ...ctx.data,
            currentTemplate: undefined,
            templateCode: templateCode
        };

        ctx.setData(updatedData);
        setSelectedTemplate(templateCode);
    };



    return (
        <div className="flex flex-col bg-gray-100 min-h-screen">
            <Navbar />
            <main className="container flex-grow mx-auto">

                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 1.</span>选择仿真模板</h2>

                <DescriptionCard
                    title="什么是仿真模板？"
                    description="仿真模板是预先配置好的社会情境和参数集合，集成了大型语言模型（LLM）技术。每个模板都代表一个独特的社交场景，如公共事件讨论、市长竞选或社区互动。这些模板预设了智能体数量、环境特征和互动规则，让您可以快速开始探索复杂的社会动态。选择一个模板，即可启动一个由AI驱动的、高度逼真的社会仿真实验。"
                />

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    {templates.map((template) => (
                        <Card
                            key={template.template_sim_code}
                            className={`w-full rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-150 cursor-pointer ${selectedTemplate === template.template_sim_code ? 'ring-4 ring-indigo-600 ring-offset-4' : ''
                                }`}
                            onClick={() => handleSelectTemplate(template.template_sim_code)}
                        >
                            <img
                                src={getTemplateImage(template)}
                                alt={template.name}
                                className="w-full h-48 object-cover"
                            />
                            <CardHeader className="p-4 bg-gradient-to-r from-purple-600 to-blue-500">
                                <CardTitle className="text-xl font-semibold text-white">{template.name}</CardTitle>
                            </CardHeader>
                            <CardContent className="p-4">
                                <ul className="list-disc list-inside text-sm mb-2 text-gray-700">
                                    {template.bullets.map((bullet, index) => (
                                        <li key={index}>{bullet}</li>
                                    ))}
                                </ul>
                                <p className="text-sm text-gray-600">{template.description}</p>
                            </CardContent>
                        </Card>
                    ))}
                    {/* 敬请期待 Card */}
                    <Card className="w-full rounded-xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-150">
                        <div className="w-full h-48 bg-gray-200 flex items-center justify-center">
                            <span className="text-4xl text-gray-500 text-center">COMING SOON</span>
                        </div>
                        <CardHeader className="p-4 bg-gradient-to-r from-gray-400 to-gray-500">
                            <CardTitle className="text-xl font-semibold text-white">敬请期待...</CardTitle>
                        </CardHeader>
                        <CardContent className="p-4">
                            <p className="text-sm text-gray-600">更多仿真模板正在开发中，敬请期待！</p>
                        </CardContent>
                    </Card>
                </div>
                <BottomNav
                    prevLink='/welcome'
                    nextLink='/events'
                    currStep={0}
                    disabled={!selectedTemplate}
                    className='my-8'
                />
            </main>
        </div>
    );
};