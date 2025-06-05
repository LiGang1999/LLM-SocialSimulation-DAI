import { useState, useEffect } from 'react';
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
import { InfoTooltip } from '@/components/Tooltip';
import DescriptionCard from '@/components/DescriptionCard';

import backgroundImage from '@/assets/Untitled.png'

const defaultConfig: apis.LLMConfig = {
    type: 'custom', // Default to custom as per new requirement
    // base_url: 'https://api.openai.com/v1',
    base_url: '',
    api_key: '',
    // engine: 'gpt-3.5-turbo',
    engine: '',
    temperature: 0.7,
    maxTokens: 512,
    topP: 0.7,
    freqPenalty: 0,
    presPenalty: 0,
    stream: false, // Streaming is temporarily unavailable
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
        <div className="flex flex-col min-h-screen" style={{ backgroundImage: `url(${backgroundImage})`, backgroundSize: '100% 100%', backgroundRepeat: 'no-repeat', backgroundAttachment: 'fixed' }}>
            <Navbar />
            <main className="flex-grow w-full container mx-auto">
                <h2 className="text-5xl font-bold my-12 text-gray-900"><span className="font-mono">Step 4.</span>仿真参数配置</h2>

                <DescriptionCard
                    title="配置您的专属AI模型"
                    description="为了让仿真实验顺利进行，我们需要您提供一些关于您希望使用的AI模型的信息。这个AI模型将扮演仿真世界中智能体的“大脑”，负责它们的对话、思考和行动。请您按照下方的指引，填写您的AI服务提供商的相关信息。如果您不确定这些信息是什么，可以查阅您的AI服务提供商提供的文档，或者联系他们的客服获取帮助。"
                />

                <Card className="w-full bg-opacity-70 bg-white mx-auto">
                    <CardContent className="space-y-6 my-4">



                        <div className="space-y-4">
                            <div className="relative">
                                <div className="flex items-center space-x-1">
                                    <Label htmlFor="configType" className="flex items-center">
                                        配置方式
                                    </Label>
                                    <InfoTooltip message='我们暂时仅支持您使用自己的AI模型服务。请在下方填写您的AI模型相关信息。' />
                                </div>
                            </div>
                            <Select value={config.type} onValueChange={(value) => updateConfig('type', value)} disabled>
                                <SelectTrigger id="configType">
                                    <SelectValue placeholder="选择配置类型" />
                                </SelectTrigger>
                                <SelectContent>
                                    {/* <SelectItem value="default">默认</SelectItem> */}
                                    <SelectItem value="custom">自定义您的AI模型</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>


                        <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="apiBase" className="flex items-center">
                                            API 服务地址 (Base URL)
                                        </Label>
                                        <InfoTooltip message="这是您的AI模型服务提供商给您的服务接口地址。例如，如果您使用OpenAI的服务，这里通常是 'https://api.openai.com/v1'。请确保填写正确，否则无法连接到AI模型。" />

                                    </div>
                                </div>
                                <Input
                                    id="apiBase"
                                    value={config.base_url}
                                    onChange={(e) => updateConfig('base_url', e.target.value)}
                                    placeholder="例如: https://api.openai.com/v1"
                                />
                            </div>

                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="apiKey" className="flex items-center">
                                            API 密钥 (API Key)
                                        </Label>

                                        <InfoTooltip message="这是您访问AI服务所需的“密码”，由您的AI模型服务提供商提供。请务必从官方渠道获取并妥善保管，不要泄露给他人。" />
                                    </div>
                                </div>
                                <Input
                                    id="apiKey"
                                    type="password"
                                    value={config.api_key}
                                    onChange={(e) => updateConfig('api_key', e.target.value)}
                                    placeholder="请输入您的 API 密钥"
                                />
                            </div>

                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="engine" className="flex items-center">
                                            模型名称 (Engine/Model)
                                        </Label>
                                        <InfoTooltip message="指定您想使用的具体AI模型名称。例如 'gpt-3.5-turbo' 或 'claude-2'。不同名称对应不同能力和特点的AI模型，请根据您的服务商提供的信息填写。" />

                                    </div>
                                </div>
                                <Input
                                    id="engine"
                                    value={config.engine}
                                    onChange={(e) => updateConfig('engine', e.target.value)}
                                    placeholder="例如: gpt-4, claude-3-opus"
                                />
                            </div>




                            <div className="space-y-6"> {/* Increased space-y to 6 for more vertical spacing */}
                                <div className="relative"> {/* Added relative positioning */}
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="temperature" className="flex items-center">
                                            模型创造力 (Temperature)：{config.temperature.toFixed(1)}
                                        </Label>
                                        <InfoTooltip message="这个参数控制AI回复的“想象力”或“创造性”。数值越高（比如 0.9），AI的回答会更大胆、更有创意，但也可能不那么准确。数值越低（比如 0.2），AI的回答会更保守、更贴近事实。一般建议保持默认值，或者在0.5到0.8之间调整。" />

                                    </div>
                                </div>
                                <Slider
                                    id="temperature"
                                    value={[config.temperature]}
                                    onValueChange={(value) => updateConfig('temperature', value[0])}
                                    max={1}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>





                            <div className="space-y-6">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="maxTokens" className="flex items-center">
                                            回复最大长度 (Max Tokens)：{config.maxTokens}
                                        </Label>
                                        <InfoTooltip message="这个参数限制AI每次回复内容的长度。“令牌”可以理解为AI处理文字的基本单位，一个汉字或一个英文单词可能算作1到3个令牌。设置一个合适的长度可以避免AI回复过长或过短。一般建议512或1024。" />
                                    </div>
                                </div>
                                <Input
                                    id="maxTokens"
                                    type="number"
                                    value={config.maxTokens}
                                    onChange={(e) => updateConfig('maxTokens', parseInt(e.target.value))}
                                    className="w-full"
                                />
                            </div>


                            <div className="space-y-6">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="topP" className="flex items-center">
                                            回复多样性 (Top P)：{config.topP.toFixed(2)}
                                        </Label>
                                        <InfoTooltip message="与“模型创造力”类似，这个参数也影响AI回复的多样性。它会从概率最高的词语中挑选回复。一般情况下，您不需要修改这个值。如果您希望AI的回答更具探索性，可以适当调高。" />
                                    </div>
                                </div>
                                <Slider
                                    id="topP"
                                    value={[config.topP]}
                                    onValueChange={(value) => updateConfig('topP', value[0])}
                                    max={1}
                                    step={0.01}
                                    className="w-full"
                                />
                            </div>


                            <div className="space-y-6">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="freqPenalty" className="flex items-center">
                                            减少重复词语 (Frequency Penalty)：{config.freqPenalty.toFixed(2)}
                                        </Label>
                                        <InfoTooltip message="这个参数用来减少AI在回复中重复使用相同词语的倾向。数值越高，AI就越倾向于使用不同的词语。如果您发现AI的回复有些啰嗦或重复，可以适当调高这个值。" />
                                    </div>
                                </div>
                                <Slider
                                    id="freqPenalty"
                                    value={[config.freqPenalty]}
                                    onValueChange={(value) => updateConfig('freqPenalty', value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.01}
                                    className="w-full"
                                />
                            </div>



                            {/* <div className="space-y-2">
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
                            </div> */}

                            <div className="space-y-6">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="presPenalty" className="flex items-center">
                                            鼓励新话题 (Presence Penalty)：{config.presPenalty.toFixed(2)}
                                        </Label>
                                        <InfoTooltip message="这个参数鼓励AI在对话中引入新的话题，而不是一直围绕已经讨论过的内容。数值越高，AI就越倾向于谈论新的东西。如果您希望AI的对话内容更丰富，可以适当调高这个值。" />
                                    </div>
                                </div>
                                <Slider
                                    id="presPenalty"
                                    value={[config.presPenalty]}
                                    onValueChange={(value) => updateConfig('presPenalty', value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.01}
                                    className="w-full"
                                />
                            </div>


                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-2">
                                        <Checkbox
                                            id="streamEnabled"
                                            checked={config.stream}
                                            onCheckedChange={(checked) => updateConfig('stream', checked)}
                                            disabled // Streaming is temporarily unavailable
                                        />
                                        <Label htmlFor="streamEnabled" className="flex items-center space-x-1 text-gray-500"> {/* Added text-gray-500 for disabled look */}
                                            <span>启用流式传输 (暂不可用)</span>
                                            <InfoTooltip message="“流式传输”能让您更快地看到AI的回复，就像打字一样逐字显示。目前这个功能暂时无法使用，我们会尽快修复。" />
                                        </Label>
                                    </div>
                                </div>
                            </div>



                        </div>
                    </CardContent>
                </Card>
                <BottomNav prevLink='/agents' nextLink='/confirm' currStep={3} disabled={false} className='mt-8 mb-4' />
            </main>
        </div >
    );
};
