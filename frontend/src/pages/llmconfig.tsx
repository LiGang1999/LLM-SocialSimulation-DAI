import { useState, useEffect, useCallback } from 'react';
import { RefreshCw } from 'lucide-react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import * as Collapsible from '@radix-ui/react-collapsible';
import { ChevronDown } from 'lucide-react';
import '@/App.css'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';
import { toast } from 'sonner';
import DescriptionCard from '@/components/DescriptionCard';

import backgroundImage from '@/assets/Untitled.png'

type LLMConfig = apis.LLMConfig;
type ProviderConfigs = Record<string, LLMConfig>;

export const ConfigPage = () => {
    const ctx = useSimContext();
    const [providers, setProviders] = useState<ProviderConfigs>({});
    const [openCollapsibles, setOpenCollapsibles] = useState<Record<string, boolean>>({});
    const [isFetching, setIsFetching] = useState(false);

    const fetchUserProviders = useCallback(async () => {
        setIsFetching(true);
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
            ctx.setData({ ...ctx.data, llmProviders: providersData });
            // Initialize all collapsible sections to be closed
            const initialOpenState = Object.keys(providersData).reduce((acc, key) => {
                acc[key] = false;
                return acc;
            }, {} as Record<string, boolean>);
            setOpenCollapsibles(initialOpenState);
        } catch (err) {
            console.error("Failed to fetch user providers:", err);
        } finally {
            setIsFetching(false);
        }
    }, [ctx]);

    useEffect(() => {
        if (ctx.data.llmProviders && Object.keys(ctx.data.llmProviders).length > 0) {
            setProviders(ctx.data.llmProviders);
            const initialOpenState = Object.keys(ctx.data.llmProviders).reduce((acc, key) => {
                acc[key] = false;
                return acc;
            }, {} as Record<string, boolean>);
            setOpenCollapsibles(initialOpenState);
        } else {
            fetchUserProviders();
        }
    }, [fetchUserProviders]);

    const updateProviderConfig = (usage: string, key: keyof LLMConfig, value: any) => {
        const newProviders = {
            ...providers,
            [usage]: {
                ...providers[usage],
                [key]: value
            }
        };
        setProviders(newProviders);
        ctx.setData({ ...ctx.data, llmProviders: newProviders });
    };

    const toggleCollapsible = (usage: string) => {
        setOpenCollapsibles(prev => ({ ...prev, [usage]: !prev[usage] }));
    };

    const isConfigValid = () => {
        const requiredProviders = ['chat', 'embedding', 'completion'];
        for (const usage of requiredProviders) {
            const provider = providers[usage];
            if (!provider || !provider.base_url || !provider.model) {
                return false;
            }
        }
        return true;
    };

    const handleSaveChanges = async (usage: string) => {
        try {
            const providerConfig = providers[usage];
            await apis.updateUserProviders({ [usage]: providerConfig });
            toast.success(`${usage} provider configuration updated successfully!`);
        } catch (err) {
            console.error(`Failed to update ${usage} provider configuration:`, err);
            toast.error(`Failed to update ${usage} provider configuration`);
        }
    };

    return (
        <div className="flex flex-col min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar className="border-white border-b-[1px] border-opacity-40 bg-white bg-opacity-40 backdrop-filter backdrop-blur-lg dark:border-b-slate-700 dark:bg-background" />
            <main className="flex-grow w-full container mx-auto">
                <div className="flex items-center my-12">
                    <h2 className="text-5xl font-bold text-gray-900"><span className="font-mono">Step 4.</span>仿真参数配置</h2>
                    <Button onClick={fetchUserProviders} disabled={isFetching} className="ml-4">
                        <RefreshCw className={`mr-2 h-4 w-4 ${isFetching ? 'animate-spin' : ''}`} />
                        刷新
                    </Button>
                </div>

                <DescriptionCard
                    title="配置您的专属AI模型"
                    description="为了让仿真实验顺利进行，我们需要您提供一些关于您希望使用的AI模型的信息。这个AI模型将扮演仿真世界中智能体的“大脑”，负责它们的对话、思考和行动。请您按照下方的指引，填写您的AI服务提供商的相关信息。如果您不确定这些信息是什么，可以查阅您的AI服务提供商提供的文档，或者联系他们的客服获取帮助。"
                />

                <div className="space-y-8">
                    {Object.entries(providers).map(([usage, config]) => (
                        <Card key={usage} className="w-full bg-opacity-70 bg-white mx-auto">
                            <CardHeader className="flex flex-row items-center justify-between">
                                <CardTitle className="capitalize">{usage} Provider</CardTitle>
                                <Button onClick={() => handleSaveChanges(usage)}>保存到用户配置</Button>
                            </CardHeader>
                            <CardContent className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                                    <div className="space-y-4">
                                        <Label htmlFor={`apiBase-${usage}`} >API 服务地址 (Base URL)</Label>
                                        <Input
                                            id={`apiBase-${usage}`}
                                            value={config.base_url}
                                            onChange={(e) => updateProviderConfig(usage, 'base_url', e.target.value)}
                                            placeholder="例如: https://api.openai.com/v1"
                                            required
                                            className={!config.base_url ? 'border-red-500' : ''}
                                        />
                                        {!config.base_url && <p className="text-red-500 text-xs mt-1">此字段为必填项</p>}
                                    </div>
                                    <div className="space-y-4">
                                        <Label htmlFor={`apiKey-${usage}`} >API 密钥 (API Key)</Label>
                                        <Input
                                            id={`apiKey-${usage}`}
                                            type="password"
                                            value={config.api_key}
                                            onChange={(e) => updateProviderConfig(usage, 'api_key', e.target.value)}
                                            placeholder="请输入您的 API 密钥"
                                        />
                                    </div>
                                    <div className="space-y-4">
                                        <Label htmlFor={`model-${usage}`} >模型名称 (Model)</Label>
                                        <Input
                                            id={`model-${usage}`}
                                            value={config.model}
                                            onChange={(e) => updateProviderConfig(usage, 'model', e.target.value)}
                                            placeholder="例如: gpt-4, claude-3-opus"
                                            required
                                            className={!config.model ? 'border-red-500' : ''}
                                        />
                                        {!config.model && <p className="text-red-500 text-xs mt-1">此字段为必填项</p>}
                                    </div>
                                </div>

                                <Collapsible.Root open={openCollapsibles[usage]} onOpenChange={() => toggleCollapsible(usage)}>
                                    <Collapsible.Trigger asChild>
                                        <button className="flex items-center justify-between w-full text-lg font-semibold">
                                            Advanced Settings
                                            <ChevronDown className={`transition-transform duration-200 ${openCollapsibles[usage] ? 'rotate-180' : ''}`} />
                                        </button>
                                    </Collapsible.Trigger>
                                    <Collapsible.Content className="pt-4">
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div className="space-y-4">
                                                <Label htmlFor={`temperature-${usage}`} >Temperature: {config.temperature.toFixed(2)}</Label>
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
                                                <Label htmlFor={`freqPenalty-${usage}`} >Frequency Penalty: {config.frequency_penalty.toFixed(2)}</Label>
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
                                                <Label htmlFor={`presPenalty-${usage}`} >Presence Penalty: {config.presence_penalty.toFixed(2)}</Label>
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
                                                <Label htmlFor={`maxTokens-${usage}`} >Max Tokens: {config.max_tokens}</Label>
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
                                                <Label htmlFor={`stream-${usage}`} >Stream</Label>
                                            </div>
                                        </div>
                                    </Collapsible.Content>
                                </Collapsible.Root>
                            </CardContent>
                        </Card>
                    ))}
                </div>

                <BottomNav prevLink='/agents' nextLink='/confirm' currStep={3} disabled={!isConfigValid()} className='mt-8 mb-4' />
            </main>
        </div >
    );
};
