import { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Slider } from "@/components/ui/slider";
import * as Collapsible from '@radix-ui/react-collapsible';
import { ChevronDown } from 'lucide-react';
import '@/App.css'
import { apis } from '@/lib/api';
import { toast } from 'sonner';

import backgroundImage from '@/assets/Untitled.png'

type LLMConfig = apis.LLMConfig;
type ProviderConfigs = Record<string, LLMConfig>;

export const ProviderConfigPage = () => {
    const [providers, setProviders] = useState<ProviderConfigs>({});
    const [openCollapsibles, setOpenCollapsibles] = useState<Record<string, boolean>>({});

    useEffect(() => {
        const fetchUserProviders = async () => {
            try {
                const userProviders = await apis.getUserProviders();
                const defaultProviders: ProviderConfigs = {
                    chat: {
                        kind: "chat",
                        base_url: "",
                        api_key: "",
                        model: "",
                        temperature: 1.0,
                        max_tokens: 4096,
                        top_p: 0.7,
                        frequency_penalty: 0.0,
                        presence_penalty: 0.0,
                        stream: false,
                    },
                    embedding: {
                        kind: "embedding",
                        base_url: "",
                        api_key: "",
                        model: "",
                        temperature: 1.0,
                        max_tokens: 4096,
                        top_p: 0.7,
                        frequency_penalty: 0.0,
                        presence_penalty: 0.0,
                        stream: false,
                    },
                    completion: {
                        kind: "completion",
                        base_url: "",
                        api_key: "",
                        model: "",
                        temperature: 1.0,
                        max_tokens: 4096,
                        top_p: 0.7,
                        frequency_penalty: 0.0,
                        presence_penalty: 0.0,
                        stream: false,
                    },
                };

                const providersData = { ...defaultProviders, ...userProviders };
                setProviders(providersData);
                // Initialize all collapsible sections to be closed
                const initialOpenState = Object.keys(providersData).reduce((acc, key) => {
                    acc[key] = false;
                    return acc;
                }, {} as Record<string, boolean>);
                setOpenCollapsibles(initialOpenState);
            } catch (err) {
                console.error("Failed to fetch user providers:", err);
                toast.error("Failed to fetch user providers");
            }
        };

        fetchUserProviders();
    }, []);

    const updateProviderConfig = (usage: string, key: keyof LLMConfig, value: any) => {
        const newProviders = {
            ...providers,
            [usage]: {
                ...providers[usage],
                [key]: value
            }
        };
        setProviders(newProviders);
    };

    const handleSaveChanges = async () => {
        try {
            await apis.updateUserProviders(providers);
            toast.success("Provider configurations updated successfully!");
        } catch (err) {
            console.error("Failed to update provider configurations:", err);
            toast.error("Failed to update provider configurations");
        }
    };

    const toggleCollapsible = (usage: string) => {
        setOpenCollapsibles(prev => ({ ...prev, [usage]: !prev[usage] }));
    };

    return (
        <div className="flex flex-col min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
            <main className="flex-grow w-full container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-gray-900">用户设置</h2>
                <p className="text-lg text-gray-600 mb-8">请配置您的聊天和嵌入服务提供商。</p>

                <div className="space-y-8">
                    {Object.entries(providers).map(([usage, config]) => (
                        <Card key={usage} className="w-full bg-opacity-70 bg-white mx-auto">
                            <CardHeader>
                                <CardTitle className="capitalize">{usage} 服务商</CardTitle>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                                    <div className="space-y-4">
                                        <Label htmlFor={`kind-${usage}`} >类型</Label>
                                        <Select value={config.kind} onValueChange={(value) => updateProviderConfig(usage, 'kind', value)}>
                                            <SelectTrigger>
                                                <SelectValue placeholder="选择类型" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="chat">聊天</SelectItem>
                                                <SelectItem value="embedding">嵌入</SelectItem>
                                                <SelectItem value="completion">补全</SelectItem>
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <div className="space-y-4">
                                        <Label htmlFor={`apiBase-${usage}`} >API 地址</Label>
                                        <Input
                                            id={`apiBase-${usage}`}
                                            value={config.base_url}
                                            onChange={(e) => updateProviderConfig(usage, 'base_url', e.target.value)}
                                            placeholder="例如: https://api.openai.com/v1"
                                        />
                                    </div>
                                    <div className="space-y-4">
                                        <Label htmlFor={`apiKey-${usage}`} >API 密钥</Label>
                                        <Input
                                            id={`apiKey-${usage}`}
                                            type="password"
                                            value={config.api_key}
                                            onChange={(e) => updateProviderConfig(usage, 'api_key', e.target.value)}
                                            placeholder="请输入您的 API 密钥"
                                        />
                                    </div>
                                    <div className="space-y-4">
                                        <Label htmlFor={`model-${usage}`} >模型</Label>
                                        <Input
                                            id={`model-${usage}`}
                                            value={config.model}
                                            onChange={(e) => updateProviderConfig(usage, 'model', e.target.value)}
                                            placeholder="例如: gpt-4, claude-3-opus"
                                        />
                                    </div>
                                </div>

                                <Collapsible.Root open={openCollapsibles[usage]} onOpenChange={() => toggleCollapsible(usage)}>
                                    <Collapsible.Trigger asChild>
                                        <button className="flex items-center justify-between w-full text-lg font-semibold">
                                            高级设置
                                            <ChevronDown className={`transition-transform duration-200 ${openCollapsibles[usage] ? 'rotate-180' : ''}`} />
                                        </button>
                                    </Collapsible.Trigger>
                                    <Collapsible.Content className="pt-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-4">
                                                <Label htmlFor={`temperature-${usage}`} >温度: {config.temperature.toFixed(2)}</Label>
                                                <Slider
                                                    id={`temperature-${usage}`}
                                                    value={[config.temperature]}
                                                    onValueChange={(value) => updateProviderConfig(usage, 'temperature', value[0])}
                                                    max={2}
                                                    step={0.01}
                                                />
                                            </div>
                                            <div className="space-y-4">
                                                <Label htmlFor={`topP-${usage}`} >Top P: {config.top_p.toFixed(2)}</Label>
                                                <Slider
                                                    id={`topP-${usage}`}
                                                    value={[config.top_p]}
                                                    onValueChange={(value) => updateProviderConfig(usage, 'top_p', value[0])}
                                                    max={1}
                                                    step={0.01}
                                                />
                                            </div>
                                            <div className="space-y-4">
                                                <Label htmlFor={`freqPenalty-${usage}`} >频率惩罚: {config.frequency_penalty.toFixed(2)}</Label>
                                                <Slider
                                                    id={`freqPenalty-${usage}`}
                                                    value={[config.frequency_penalty]}
                                                    onValueChange={(value) => updateProviderConfig(usage, 'frequency_penalty', value[0])}
                                                    min={-2}
                                                    max={2}
                                                    step={0.01}
                                                />
                                            </div>
                                            <div className="space-y-4">
                                                <Label htmlFor={`presPenalty-${usage}`} >存在惩罚: {config.presence_penalty.toFixed(2)}</Label>
                                                <Slider
                                                    id={`presPenalty-${usage}`}
                                                    value={[config.presence_penalty]}
                                                    onValueChange={(value) => updateProviderConfig(usage, 'presence_penalty', value[0])}
                                                    min={-2}
                                                    max={2}
                                                    step={0.01}
                                                />
                                            </div>
                                            <div className="space-y-4">
                                                <Label htmlFor={`maxTokens-${usage}`} >最大令牌数: {config.max_tokens}</Label>
                                                <Input
                                                    id={`maxTokens-${usage}`}
                                                    type="number"
                                                    value={config.max_tokens}
                                                    onChange={(e) => updateProviderConfig(usage, 'max_tokens', parseInt(e.target.value))}
                                                />
                                            </div>
                                            <div className="flex items-center space-x-2">
                                                <Checkbox
                                                    id={`stream-${usage}`}
                                                    checked={config.stream}
                                                    onCheckedChange={(checked) => updateProviderConfig(usage, 'stream', checked)}
                                                />
                                                <Label htmlFor={`stream-${usage}`} >流式传输</Label>
                                            </div>
                                        </div>
                                    </Collapsible.Content>
                                </Collapsible.Root>
                            </CardContent>
                        </Card>
                    ))}
                </div>
                <Button onClick={handleSaveChanges} className="mt-8 mb-4">保存更改</Button>
            </main>
        </div >
    );
};
