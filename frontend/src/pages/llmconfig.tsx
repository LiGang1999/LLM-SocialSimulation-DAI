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
                if (ctx.data.currSimCode && !ctx.data.currentTemplate) {
                    const templateData = await apis.fetchTemplate(ctx.data.currSimCode);
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
                <h1 className="text-5xl font-bold my-12 text-gray-900">仿真参数配置</h1>
                <Card className="w-full mx-auto">
                    <CardContent className="space-y-6 my-4">
                        <div className="space-y-2">
                            <Label htmlFor="configType">Configuration Type</Label>
                            <Select value={config.type} onValueChange={(value) => updateConfig('type', value)}>
                                <SelectTrigger id="configType">
                                    <SelectValue placeholder="Select configuration type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="default">Default</SelectItem>
                                    <SelectItem value="custom">Custom</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                            <div className="space-y-2">
                                <Label htmlFor="apiBase">API Base</Label>
                                <Input
                                    id="apiBase"
                                    value={config.baseUrl}
                                    onChange={(e) => updateConfig('baseUrl', e.target.value)}
                                    placeholder="https://api.openai.com/v1"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="apiKey">API Key</Label>
                                <Input
                                    id="apiKey"
                                    type="password"
                                    value={config.key}
                                    onChange={(e) => updateConfig('key', e.target.value)}
                                    placeholder="Your API key"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="engine">Engine</Label>
                                <Input
                                    id="engine"
                                    value={config.engine}
                                    onChange={(e) => updateConfig('engine', e.target.value)}
                                    placeholder="e.g., gpt-3.5-turbo"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="temperature">Temperature: {config.temperature.toFixed(1)}</Label>
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
                                <Label htmlFor="maxTokens">Max Tokens</Label>
                                <Input
                                    id="maxTokens"
                                    type="number"
                                    value={config.maxTokens}
                                    onChange={(e) => updateConfig('maxTokens', parseInt(e.target.value))}
                                    placeholder="512"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="topP">Top P: {config.topP.toFixed(1)}</Label>
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
                                <Label htmlFor="frequencyPenalty">Frequency Penalty: {config.freqPenalty.toFixed(1)}</Label>
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
                                <Label htmlFor="presencePenalty">Presence Penalty: {config.presPenalty.toFixed(1)}</Label>
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
                                <Label htmlFor="stream">Enable streaming</Label>
                            </div>
                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/agents' nextLink='/confirm' currStep={3} disabled={false} className='mt-8 mb-4' />
            </main>
        </div>
    );
};