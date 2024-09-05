import React from 'react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useSimContext } from '@/SimContext';

const truncateString = (str: string, num: number) => {
    if (str.length <= num) {
        return str;
    }
    return str.slice(0, num) + '...';
};

export const ConfirmPage = () => {
    const ctx = useSimContext();

    if (!ctx || !ctx.data.currentTemplate) {
        return <div>Loading...</div>;
    }

    const { currentTemplate, llmConfig } = ctx.data;

    const displayedAgents = currentTemplate.personas.slice(0, 4);
    const hasMoreAgents = currentTemplate.personas.length > 4;

    return (
        <div className="flex flex-col min-h-screen">
            <Navbar />
            <div className="container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-left text-black-800">开始仿真</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full">
                    <Card>
                        <CardHeader>
                            <CardTitle>模板信息</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <h3 className="font-semibold">{currentTemplate.meta.name}</h3>
                            <img src="/api/placeholder/300/200" alt="模板图片" className="my-2 rounded-md" />
                            <ul className="list-disc list-inside">
                                {currentTemplate.meta.bullets.map((bullet, index) => (
                                    <li key={index}>{bullet}</li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>智能体配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>智能体数量: {currentTemplate.personas.length}</p>
                            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                                {displayedAgents.map((agent, index) => (
                                    <div key={index} className="flex items-center mb-2">
                                        <Avatar className="mr-2">
                                            <AvatarImage src={agent.avatar} alt={agent.name} />
                                            <AvatarFallback>{agent.firstName[0]}</AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-semibold">{agent.firstName} {agent.lastName}</p>
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

                    <Card>
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

                    <Card>
                        <CardHeader>
                            <CardTitle>模型参数配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {llmConfig ? (
                                <>
                                    <p><strong>模型类型:</strong> {llmConfig.type}</p>
                                    <p><strong>模型URL:</strong> {llmConfig.baseUrl}</p>
                                    <p><strong>引擎:</strong> {llmConfig.engine}</p>
                                    <p><strong>最大Token数量:</strong> {llmConfig.maxTokens}</p>
                                </>
                            ) : (
                                <p>LLM配置未设置</p>
                            )}
                        </CardContent>
                    </Card>
                </div>
                <BottomNav
                    prevLink='/llmconfig'
                    nextLink=''
                    onClickNext={() => {
                        console.log("next clicked!");
                    }}
                    currStep={4}
                    disabled={false}
                    className='mt-16'
                />
            </div>
        </div>
    );
};