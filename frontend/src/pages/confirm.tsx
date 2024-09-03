import { Navbar } from "@/components/Navbar"

import { BottomNav } from "@/components/BottomNav"

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";


const simulationData = {
    template: {
        name: "未来城市模拟",
        image: "/api/placeholder/300/200",
        features: ["高度智能化", "可持续发展", "社会和谐"]
    },
    agents: [
        { name: "Alex", avatar: "/api/placeholder/40/40", personality: "创新者", age: 28 },
        { name: "Emma", avatar: "/api/placeholder/40/40", personality: "分析师", age: 35 },
        { name: "Liu", avatar: "/api/placeholder/40/40", personality: "协调者", age: 42 }
    ],
    events: [
        { name: "技术突破", description: "AI革命性应用" },
        { name: "社会变革", description: "新型工作模式" },
        { name: "环境挑战", description: "应对气候变化" }
    ],
    model: {
        name: "GPT-4",
        url: "https://api.openai.com/v1/chat/completions",
        maxTokens: 4096
    }
};

export const ConfirmPage = () => {
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
                            <h3 className="font-semibold">{simulationData.template.name}</h3>
                            <img src={simulationData.template.image} alt="模板图片" className="my-2 rounded-md" />
                            <ul className="list-disc list-inside">
                                {simulationData.template.features.map((feature, index) => (
                                    <li key={index}>{feature}</li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>智能体配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>智能体数量: {simulationData.agents.length}</p>
                            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                                {simulationData.agents.map((agent, index) => (
                                    <div key={index} className="flex items-center mb-2">
                                        <Avatar className="mr-2">
                                            <AvatarImage src={agent.avatar} alt={agent.name} />
                                            <AvatarFallback>{agent.name[0]}</AvatarFallback>
                                        </Avatar>
                                        <div>
                                            <p className="font-semibold">{agent.name}</p>
                                            <p className="text-sm">{agent.personality}, {agent.age}岁</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>方案设计</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p>事件数量: {simulationData.events.length}</p>
                            <ul className="list-disc list-inside mt-2">
                                {simulationData.events.map((event, index) => (
                                    <li key={index}>{event.name}: {event.description}</li>
                                ))}
                            </ul>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardHeader>
                            <CardTitle>模型参数配置</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p><strong>模型名称:</strong> {simulationData.model.name}</p>
                            <p><strong>模型URL:</strong> {simulationData.model.url}</p>
                            <p><strong>最大Token数量:</strong> {simulationData.model.maxTokens}</p>
                        </CardContent>
                    </Card>
                </div>
                <BottomNav prevLink='/llmconfig' nextLink='' onClickNext={() => {
                    console.log("next clicked!")
                }} currStep={4} disabled={false} className='mt-16'></BottomNav>
            </div>
        </div>
    )
}