import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Navbar } from '@/components/Navbar';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger } from "@/components/ui/alert-dialog";
import { Trash2 } from 'lucide-react';
import { Button } from "@/components/ui/button";

import start1 from '@/assets/template2.png';
import chat from '@/assets/chat.png';
import stf from '@/assets/start2.jpg';
import shbz from '@/assets/444.png';
import hk5 from '@/assets/555.png';
import hk20 from '@/assets/666.png'


import { BottomNav } from '@/components/BottomNav';


import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import DescriptionCard from '@/components/DescriptionCard';

import backgroundImage from '@/assets/Untitled.png'

// TODO Add background for this webpage
const getTemplateImage = (template: apis.TemplateListItem) => {
    if (template.template_sim_code === 'shbz') {
        return shbz;
    }
    else if (template.template_sim_code === 'base_the_ville_isabella_maria_klaus_online') {
        return chat;
    } else if (template.template_sim_code === 'base_the_ville_isabella_maria_klaus') {
        return start1;
    }
    else if (template.template_sim_code === 'base_the_ville_n25_info') {
        return stf;
    }
    else if (template.template_sim_code === 'dragon_tv_demo') {
        return start1;
    }
    else if (template.template_sim_code === 'legislative_council') {
        return hk5;
    }
    else if (template.template_sim_code === 'legislative_council_life') {
        return hk20;
    } else if (template.template_sim_code == 'legislative_council_life_demo') {
        return hk20;
    } else return chat;
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
    const [_, setTemplates] = useState<apis.TemplateListItem[]>([]);
    const [public_templates, setPublicTemplates] = useState<apis.TemplateListItem[]>([]);
    const [user_templates, setUserTemplates] = useState<apis.TemplateListItem[]>([]);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                const { public_templates: pubTemplates, user_templates: userTemplates } = await apis.fetchTemplates();
                // Keep templates separate for grouped display
                setPublicTemplates(pubTemplates);
                setUserTemplates(userTemplates);
                setTemplates([...pubTemplates, ...userTemplates]);
                ctx.setData(
                    {
                        ...ctx.data,
                        allTemplates: [...pubTemplates, ...userTemplates],
                        allEnvs: [...pubTemplates, ...userTemplates].map(t => t.template_sim_code)
                    }
                )
            } catch (err) {
                // If there's an error (e.g., 401 unauthorized), use mock templates
                // This provides a fallback UI when the API is inaccessible
                console.error("Failed to fetch templates:", err);
                setTemplates(mockTemplates);
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
        <div className="flex flex-col bg-gray-100 min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
            <main className="container flex-grow mx-auto">

                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 1.</span>选择仿真模板</h2>

                <DescriptionCard
                    title="什么是仿真模板？"
                    description="仿真模板是预先配置好的社会情境和参数集合，集成了大型语言模型（LLM）技术。每个模板都代表一个独特的社交场景，如公共事件讨论、市长竞选或社区互动。这些模板预设了智能体数量、环境特征和互动规则，让您可以快速开始探索复杂的社会动态。选择一个模板，即可启动一个由AI驱动的、高度逼真的社会仿真实验。"
                />

                {public_templates.length > 0 && (
                    <>
                        <h3 className="text-3xl font-bold my-8 text-left text-black-800">公共模板</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
                            {public_templates.map((template) => (
                                <Card
                                    key={template.template_sim_code}
                                    className={`w-full rounded-xl bg-opacity-30 bg-white overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-150 cursor-pointer ${selectedTemplate === template.template_sim_code ? 'ring-4 ring-indigo-600 ring-offset-4' : ''
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
                        </div>
                    </>
                )}

                {user_templates.length > 0 && (
                    <>
                        <h3 className="text-3xl font-bold my-8 text-left text-black-800">您创建的模板</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
                            {user_templates.map((template: apis.TemplateListItem) => (
                                <Card
                                    key={template.template_sim_code}
                                    className={`w-full relative rounded-xl bg-opacity-30 bg-white overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-150 cursor-pointer ${selectedTemplate === template.template_sim_code ? 'ring-4 ring-indigo-600 ring-offset-4' : ''
                                        }`}
                                    onClick={() => handleSelectTemplate(template.template_sim_code)}
                                >
                                    <div className="absolute top-2 right-2">
                                        <AlertDialog>
                                            <AlertDialogTrigger asChild>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    className="bg-red-500 hover:bg-red-600 text-white p-1 rounded-full w-8 h-8 flex items-center justify-center"
                                                    onClick={(e) => e.stopPropagation()}
                                                >
                                                    <Trash2 className="h-4 w-4" />
                                                </Button>
                                            </AlertDialogTrigger>
                                            <AlertDialogContent>
                                                <AlertDialogHeader>
                                                    <AlertDialogTitle>您确定要删除这个模板吗？</AlertDialogTitle>
                                                    <AlertDialogDescription>
                                                        该操作无法撤销。模板 "{template.name}" 将从服务器上永久删除。
                                                    </AlertDialogDescription>
                                                </AlertDialogHeader>
                                                <AlertDialogFooter>
                                                    <AlertDialogCancel>取消</AlertDialogCancel>
                                                    <AlertDialogAction
                                                        onClick={async (e) => {
                                                            e.stopPropagation();
                                                            try {
                                                                await apis.deleteTemplate(template.template_sim_code);
                                                                // Update user templates state
                                                                const updatedUserTemplates = user_templates.filter(t => t.template_sim_code !== template.template_sim_code);
                                                                setUserTemplates(updatedUserTemplates);

                                                                // Update context with filtered templates
                                                                const allUpdatedTemplates = [...public_templates, ...updatedUserTemplates];
                                                                ctx.setData({
                                                                    ...ctx.data,
                                                                    allTemplates: allUpdatedTemplates,
                                                                    allEnvs: allUpdatedTemplates.map(t => t.template_sim_code)
                                                                });

                                                                // If deleted template was selected, clear selection
                                                                if (selectedTemplate === template.template_sim_code) {
                                                                    setSelectedTemplate(null);
                                                                    ctx.setData({
                                                                        ...ctx.data,
                                                                        templateCode: undefined,
                                                                        currentTemplate: undefined
                                                                    });
                                                                }
                                                            } catch (err) {
                                                                console.error("Failed to delete template:", err);
                                                                alert("删除模板失败");
                                                            }
                                                        }}
                                                        className="bg-red-600 hover:bg-red-700"
                                                    >
                                                        删除
                                                    </AlertDialogAction>
                                                </AlertDialogFooter>
                                            </AlertDialogContent>
                                        </AlertDialog>
                                    </div>
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
                                            {template.bullets.map((bullet: string, index: number) => (
                                                <li key={index}>{bullet}</li>
                                            ))}
                                        </ul>
                                        <p className="text-sm text-gray-600">{template.description}</p>
                                    </CardContent>
                                </Card>
                            ))}
                            {/* 敬请期待 Card */}
                            <Card className="w-full rounded-xl overflow-hidden bg-opacity-30 bg-white shadow-lg hover:shadow-2xl transition-all duration-150">
                                <div className="w-full h-48 bg-gray-200 bg-opacity-50 flex items-center justify-center">
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
                    </>
                )}
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
