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
import { InfoIcon } from 'lucide-react';
import { useRef } from 'react';
import { Tooltip } from '@/components/Tooltip';

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

    const infoIconRef = useRef(null);  // 创建 ref
    const [showTooltip, setShowTooltip] = useState(false);
    const maxTokensRef = useRef(null);
    const topPRef = useRef(null);
    const freqPenaltyRef = useRef(null);
    const presPenaltyRef = useRef(null);
    const configTypeRef = useRef(null);
    const apiBaseRef = useRef(null);
    const apiKeyRef = useRef(null);
    const engineRef = useRef(null);


    const [showMaxTokensTooltip, setShowMaxTokensTooltip] = useState(false);
    const [showTopPTooltip, setShowTopPTooltip] = useState(false);
    const [showFreqPenaltyTooltip, setShowFreqPenaltyTooltip] = useState(false);
    const [showPresPenaltyTooltip, setShowPresPenaltyTooltip] = useState(false);
    const streamingRef = useRef(null);
    const [showStreamingTooltip, setShowStreamingTooltip] = useState(false);
    const [showConfigTypeTooltip, setShowConfigTypeTooltip] = useState(false);
    const [showApiBaseTooltip, setShowApiBaseTooltip] = useState(false);
    const [showApiKeyTooltip, setShowApiKeyTooltip] = useState(false);
    const [showEngineTooltip, setShowEngineTooltip] = useState(false);



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
                <h2 className="text-5xl font-bold my-12 text-gray-900"><span className="font-mono">Step 4.</span>仿真参数配置</h2>

                <div className="  mb-8">
                    <div className="flex items-center mb-4">
                        <InfoIcon className="w-6 h-6 text-blue-500 mr-2" />
                        <h3 className="text-xl font-semibold text-gray-800">什么是仿真模板？</h3>
                    </div>
                    <p className="text-gray-700 leading-relaxed">
                        仿真模板是预先配置好的社会情境和参数集合，集成了大型语言模型（LLM）技术。每个模板都代表一个独特的社交场景，如公共事件讨论、市长竞选或社区互动。这些模板预设了智能体数量、环境特征和互动规则，让您可以快速开始探索复杂的社会动态。选择一个模板，即可启动一个由AI驱动的、高度逼真的社会仿真实验。
                    </p>

                </div>

                <Card className="w-full mx-auto">
                    <CardContent className="space-y-6 my-4">



                        <div className="space-y-4">
                            <div className="relative">
                                <div className="flex items-center space-x-1">
                                    <Label htmlFor="configType" className="flex items-center">
                                        配置类型
                                    </Label>
                                    <div className="relative">
                                        <InfoIcon
                                            ref={configTypeRef}
                                            className="w-4 h-4 text-gray-500 cursor-pointer"
                                            onClick={() => setShowConfigTypeTooltip(!showConfigTypeTooltip)}
                                        />
                                        <Tooltip
                                            message="选择预设配置或自定义设置。默认配置适用于大多数场景，自定义允许更精细的控制。"
                                            isVisible={showConfigTypeTooltip}
                                            anchorRef={configTypeRef}
                                        />
                                    </div>
                                </div>
                            </div>
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
                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="apiBase" className="flex items-center">
                                            API 基础地址
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={apiBaseRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowApiBaseTooltip(!showApiBaseTooltip)}
                                            />
                                            <Tooltip
                                                message="指定API服务器的地址。通常不需要更改，除非使用自定义或代理服务器。"
                                                isVisible={showApiBaseTooltip}
                                                anchorRef={apiBaseRef}
                                            />
                                        </div>
                                    </div>
                                </div>
                                <Input
                                    id="apiBase"
                                    value={config.baseUrl}
                                    onChange={(e) => updateConfig('baseUrl', e.target.value)}
                                    placeholder="https://api.openai.com/v1"
                                />
                            </div>

                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="apiKey" className="flex items-center">
                                            API 密钥
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={apiKeyRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowApiKeyTooltip(!showApiKeyTooltip)}
                                            />
                                            <Tooltip
                                                message="您的个人访问令牌，用于认证和访问AI服务。请保密处理。"
                                                isVisible={showApiKeyTooltip}
                                                anchorRef={apiKeyRef}
                                            />
                                        </div>
                                    </div>
                                </div>
                                <Input
                                    id="apiKey"
                                    type="password"
                                    value={config.key}
                                    onChange={(e) => updateConfig('key', e.target.value)}
                                    placeholder="您的 API 密钥"
                                />
                            </div>

                            <div className="space-y-4">
                                <div className="relative">
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="engine" className="flex items-center">
                                            引擎
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={engineRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowEngineTooltip(!showEngineTooltip)}
                                            />
                                            <Tooltip
                                                message="选择用于生成文本的AI模型。不同的引擎可能在能力、速度和特定任务的表现上有所不同。"
                                                isVisible={showEngineTooltip}
                                                anchorRef={engineRef}
                                            />
                                        </div>
                                    </div>
                                </div>
                                <Input
                                    id="engine"
                                    value={config.engine}
                                    onChange={(e) => updateConfig('engine', e.target.value)}
                                    placeholder="例如：gpt-3.5-turbo"
                                />
                            </div>




                            <div className="space-y-6"> {/* Increased space-y to 6 for more vertical spacing */}
                                <div className="relative"> {/* Added relative positioning */}
                                    <div className="flex items-center space-x-1">
                                        <Label htmlFor="temperature" className="flex items-center">
                                            温度：{config.temperature.toFixed(1)}
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={infoIconRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowTooltip(!showTooltip)}
                                            />
                                            <Tooltip
                                                message="温度控制生成文本的随机性。"
                                                isVisible={showTooltip}
                                                anchorRef={infoIconRef}
                                            />
                                        </div>
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
                                            最大令牌数：{config.maxTokens}
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={maxTokensRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowMaxTokensTooltip(!showMaxTokensTooltip)}
                                            />
                                            <Tooltip
                                                message="控制生成文本的最大长度。较高的值允许更长的输出，但可能增加处理时间。"
                                                isVisible={showMaxTokensTooltip}
                                                anchorRef={maxTokensRef}
                                            />
                                        </div>
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
                                            Top P：{config.topP.toFixed(2)}
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={topPRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowTopPTooltip(!showTopPTooltip)}
                                            />
                                            <Tooltip
                                                message="控制输出的多样性。较低的值使输出更加集中和确定，较高的值增加创意性和多样性。"
                                                isVisible={showTopPTooltip}
                                                anchorRef={topPRef}
                                            />
                                        </div>
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
                                            频率惩罚：{config.freqPenalty.toFixed(2)}
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={freqPenaltyRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowFreqPenaltyTooltip(!showFreqPenaltyTooltip)}
                                            />
                                            <Tooltip
                                                message="降低模型重复使用相同词语的倾向。较高的值会鼓励使用更多样化的词汇。"
                                                isVisible={showFreqPenaltyTooltip}
                                                anchorRef={freqPenaltyRef}
                                            />
                                        </div>
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
                                            存在惩罚：{config.presPenalty.toFixed(2)}
                                        </Label>
                                        <div className="relative">
                                            <InfoIcon
                                                ref={presPenaltyRef}
                                                className="w-4 h-4 text-gray-500 cursor-pointer"
                                                onClick={() => setShowPresPenaltyTooltip(!showPresPenaltyTooltip)}
                                            />
                                            <Tooltip
                                                message="降低模型重复讨论相同主题的倾向。较高的值会鼓励模型探索新的话题。"
                                                isVisible={showPresPenaltyTooltip}
                                                anchorRef={presPenaltyRef}
                                            />
                                        </div>
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
                                        />
                                        <Label htmlFor="streamEnabled" className="flex items-center space-x-1">
                                            <span>启用流式传输</span>
                                            <div className="relative">
                                                <InfoIcon
                                                    ref={streamingRef}
                                                    className="w-4 h-4 text-gray-500 cursor-pointer"
                                                    onClick={() => setShowStreamingTooltip(!showStreamingTooltip)}
                                                />
                                                <Tooltip
                                                    message="允许实时接收生成的文本。这可以提供更快的响应，但可能增加网络负载。"
                                                    isVisible={showStreamingTooltip}
                                                    anchorRef={streamingRef}
                                                />
                                            </div>
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