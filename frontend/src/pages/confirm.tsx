import { useNavigate } from "react-router-dom";
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useSimContext } from '@/SimContext';
import { apis } from "@/lib/api";
import { RandomAvatar } from "@/components/Avatars";
import { useState, useEffect } from "react";

import start1 from '@/assets/template2.png';
import chat from '@/assets/chat.png';
import stf from '@/assets/start2.jpg'

import backgroundImage from '@/assets/Untitled.png'

const truncateString = (str: string, num: number) => {
    if (str.length <= num) {
        return str;
    }
    return str.slice(0, num) + '...';
};

export const ConfirmPage = () => {
    const ctx = useSimContext();
    const navigate = useNavigate();
    const [templateImage, setTemplateImage] = useState(stf);

    if (!ctx || !ctx.data.currentTemplate) {
        return <div>Loading...</div>;
    }

    const { currentTemplate, llmProviders } = ctx.data;


    const displayedAgents = currentTemplate.personas.slice(0, 4);
    const hasMoreAgents = currentTemplate.personas.length > 4;

    const handleNextClick = async () => {
        if (!ctx || !ctx.data.currentTemplate || !ctx.data.llmProviders) {
            console.error("Missing required data");
            return;
        }

        try {
            await apis.startSim(
                ctx.data.currSimCode || '',
                ctx.data.currentTemplate,
                ctx.data.llmProviders,
                ctx.data.initialRounds || 0
            );
            navigate('/interact');
        } catch (error) {
            console.error("Failed to start simulation:", error);
            // Handle error (e.g., show an error message to the user)
        }
    };

    useEffect(() => {
        if (ctx && ctx.data.currentTemplate?.simCode) {
            switch (ctx.data.currentTemplate.simCode) {
                case 'base_the_ville_isabella_maria_klaus_online':
                    setTemplateImage(chat);
                    break;
                case 'base_the_ville_isabella_maria_klaus':
                    setTemplateImage(start1);
                    break;
                case 'base_the_ville_n25':
                    setTemplateImage(stf);
                    break;
                case 'dragon_tv_demo':
                    setTemplateImage(start1);
                    break;
                case 'legislative_council':
                    setTemplateImage(chat);
                    break;
                case 'legislative_council_life':
                    setTemplateImage(chat);
                    break;
                case 'shbz':
                    setTemplateImage(chat);
                    break;
                default:
                    setTemplateImage(stf);
            }
        }
    }, [ctx, ctx?.data.currentTemplate.simCode]);

    return (
        <div className="flex flex-col bg-gray-100 min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800"><span className="font-mono">Step 5.</span>确认您的方案</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
                    <Card className="rounded-lg bg-white bg-opacity-50">
                        <CardHeader>
                            <CardTitle>模板信息</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="flex flex-col md:flex-row items-start">
                                {/* 左侧的文本信息 */}
                                <div className="w-full md:w-1/2">
                                    <h3 className="font-semibold">{currentTemplate.meta.name}</h3>
                                    <ul className="list-disc list-inside">
                                        {currentTemplate.meta.bullets.map((bullet, index) => (
                                            <li key={index}>{bullet}</li>
                                        ))}
                                    </ul>
                                </div>
                                {/* 右侧的图片，稍微放大图片尺寸 */}
                                <div className="w-full md:w-1/2 md:ml-4 flex justify-center">
                                    <img
                                        src={templateImage}
                                        alt="模板图片"
                                        className="rounded-md"
                                        style={{ maxWidth: '140px', height: 'auto' }}
                                    />
                                </div>
                            </div>
                        </CardContent>
                    </Card>


                    <Card className="rounded-lg bg-opacity-50 bg-white">
                        <CardHeader>
                            <CardTitle>智能体配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>智能体数量: {currentTemplate.personas.length}</p>
                            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                                {displayedAgents.map((agent, index) => (
                                    <div key={index} className="flex items-center mb-2">
                                        <RandomAvatar className="h-10 w-10 mr-4" name={`${agent.name}`} />
                                        <div>
                                            <p className="font-semibold">{agent.name}</p>
                                            <p className="text-sm">{agent.age}岁</p>
                                        </div>
                                    </div>
                                ))}
                                {hasMoreAgents && (
                                    <div className="flex items-center mb-2">
                                        <p className="text-sm text-gray-500">...</p>
                                    </div>
                                )}
                            </div>
                        </CardContent>
                    </Card>

                    <Card className=" rounded-lg bg-opacity-50 bg-white">
                        <CardHeader>
                            <CardTitle>方案设计</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>事件数量: {currentTemplate.events.length}</p>
                            <ul className="list-disc list-inside mt-2">
                                {currentTemplate.events.map((event, index) => (
                                    <li key={index}>
                                        {event.name}: {truncateString(event.description, 50)}
                                    </li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    <Card className="rounded-lg bg-opacity-50 bg-white">
                        <CardHeader>
                            <CardTitle>模型参数配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {llmProviders && Object.keys(llmProviders).length > 0 ? (
                                Object.entries(llmProviders).map(([providerName, config]) => (
                                    <div key={providerName} className="mb-4">
                                        <h4 className="font-semibold">{providerName}</h4>
                                        <p><strong>模型:</strong> {config.model}</p>
                                        <p><strong>URL:</strong> {config.base_url}</p>
                                        <p><strong>API Key:</strong> {truncateString(config.api_key, 20)}</p>
                                    </div>
                                ))
                            ) : (
                                <p>LLM配置未设置</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
                <BottomNav
                    prevLink='/llmconfig'
                    nextLink=''
                    onClickNext={handleNextClick}
                    currStep={4}
                    disabled={false}
                    className='my-8'
                    variant="final"
                />
            </div>
        </div>
    );
};
