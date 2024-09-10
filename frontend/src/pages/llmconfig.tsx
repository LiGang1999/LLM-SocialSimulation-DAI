import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import '@/App.css'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';

const defaultConfig: apis.LLMConfig = {
    type: 'default',
    baseUrl: 'https://api.openai.com/v1',
    key: '',
    engine: 'gpt-3.5-turbo',
    temperature: 0.7,
    maxTokens: 512,
    topP: 0.7,
    freqPenalty: 0,
    presPenalty: 0,
    stream: false,
};

export const ConfigPage = () => {
    const ctx = useSimContext();
    const [config, setConfig] = useState<apis.LLMConfig>(ctx.data.llmConfig || defaultConfig);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.templateCode && !ctx.data.currentTemplate) {
                    const templateData = await apis.fetchTemplate(ctx.data.templateCode);
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
        ctx.setData({ ...ctx.data, llmConfig: config });
    }, []);

    const updateConfig = (key: keyof apis.LLMConfig, value: any) => {
        const newConfig = { ...config, [key]: value };
        setConfig(newConfig);
        ctx.setData({ ...ctx.data, llmConfig: newConfig });
    };

    return (
        <div className="flex flex-col min-h-screen bg-gray-50">
            <Navbar />
            <main className="flex-grow w-full container mx-auto">
                <h1 className="text-5xl font-bold my-12 text-gray-900"><span className="font-mono">Step 4.</span>仿真参数配置</h1>
                <Card className="w-full mx-auto">
                    <CardContent className="space-y-6 my-4">
                        <div className="space-y-2">
                            <Label htmlFor="configType">配置类型</Label>
                            <Select value={config.type} onValueChange={(value) => updateConfig('type', value)}>
                                <SelectTrigger id="configType">
                                    <SelectValue placeholder="选择配置类型" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="default">默认</SelectItem>
                                    <SelectItem value="custom">自定义</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                            <div className="space-y-2">
                                <Label htmlFor="apiBase">API 基础地址</Label>
                                <Input
                                    id="apiBase"
                                    value={config.baseUrl}
                                    onChange={(e) => updateConfig('baseUrl', e.target.value)}
                                    placeholder="https://api.openai.com/v1"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="apiKey">API 密钥</Label>
                                <Input
                                    id="apiKey"
                                    type="password"
                                    value={config.key}
                                    onChange={(e) => updateConfig('key', e.target.value)}
                                    placeholder="您的 API 密钥"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="engine">引擎</Label>
                                <Input
                                    id="engine"
                                    value={config.engine}
                                    onChange={(e) => updateConfig('engine', e.target.value)}
                                    placeholder="例如：gpt-3.5-turbo"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="temperature">温度：{config.temperature.toFixed(1)}</Label>
                                <Slider
                                    id="temperature"
                                    value={[config.temperature]}
                                    onValueChange={(value) => updateConfig('temperature', value[0])}
                                    max={1}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="maxTokens">最大令牌数</Label>
                                <Input
                                    id="maxTokens"
                                    type="number"
                                    value={config.maxTokens}
                                    onChange={(e) => updateConfig('maxTokens', parseInt(e.target.value))}
                                    placeholder="512"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="topP">Top P：{config.topP.toFixed(1)}</Label>
                                <Slider
                                    id="topP"
                                    value={[config.topP]}
                                    onValueChange={(value) => updateConfig('topP', value[0])}
                                    max={1}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="frequencyPenalty">频率惩罚：{config.freqPenalty.toFixed(1)}</Label>
                                <Slider
                                    id="frequencyPenalty"
                                    value={[config.freqPenalty]}
                                    onValueChange={(value) => updateConfig('freqPenalty', value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="presencePenalty">存在惩罚：{config.presPenalty.toFixed(1)}</Label>
                                <Slider
                                    id="presencePenalty"
                                    value={[config.presPenalty]}
                                    onValueChange={(value) => updateConfig('presPenalty', value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox
                                    id="stream"
                                    checked={config.stream}
                                    onCheckedChange={(checked) => updateConfig('stream', checked)}
                                />
                                <Label htmlFor="stream">启用流式传输</Label>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/agents' nextLink='/confirm' currStep={3} disabled={false} className='mt-8 mb-4' />
            </main>
        </div>
    );
};