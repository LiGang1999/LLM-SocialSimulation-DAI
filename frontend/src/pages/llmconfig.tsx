import React, { useState, useEffect } from 'react';
import { Navbar } from "@/components/Navbar";
import { BottomNav } from "@/components/BottomNav";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import '@/App.css'
import { useSimContext } from '@/SimContext';
import { apis } from '@/lib/api';


export const ConfigPage = () => {
    const ctx = useSimContext();

    const [temperature, setTemperature] = useState(0.7);
    const [topP, setTopP] = useState(0.7);
    const [frequencyPenalty, setFrequencyPenalty] = useState(0);
    const [presencePenalty, setPresencePenalty] = useState(0);

    useEffect(() => {
        const fetchTemplates = async () => {
            try {
                if (ctx.data.currSimCode && !ctx.data.currentTemplate) {
                    // should fetch the template data!
                    const templateData = await apis.fetchTemplate(ctx.data.currSimCode);
                    ctx.setData({
                        ...ctx.data,
                        currentTemplate: templateData
                    })
                }
            } catch (err) {
                console.error("Failed to fetch template detail:", err);
            }
        }

        fetchTemplates();
    }, [])


    return (
        <div className="flex flex-col min-h-screen bg-gray-50">
            <Navbar />
            <main className="flex-grow w-full container mx-auto">
                <h1 className="text-5xl font-bold my-12 text-gray-900">仿真参数配置</h1>
                <Card className="w-full mx-auto">
                    <CardContent className="space-y-6 my-4">
                        <div className="space-y-2">
                            <Label htmlFor="configType">Configuration Type</Label>
                            <Select defaultValue="default">
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
                                <Input id="apiBase" placeholder="https://api.openai.com/v1" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="apiKey">API Key</Label>
                                <Input id="apiKey" type="password" placeholder="Your API key" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="engine">Engine</Label>
                                <Input id="engine" placeholder="e.g., gpt-3.5-turbo" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="temperature">Temperature: {temperature.toFixed(1)}</Label>
                                <Slider
                                    id="temperature"
                                    value={[temperature]}
                                    onValueChange={(value) => setTemperature(value[0])}
                                    max={1}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="maxTokens">Max Tokens</Label>
                                <Input id="maxTokens" type="number" placeholder="512" />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="topP">Top P: {topP.toFixed(1)}</Label>
                                <Slider
                                    id="topP"
                                    value={[topP]}
                                    onValueChange={(value) => setTopP(value[0])}
                                    max={1}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="frequencyPenalty">Frequency Penalty: {frequencyPenalty.toFixed(1)}</Label>
                                <Slider
                                    id="frequencyPenalty"
                                    value={[frequencyPenalty]}
                                    onValueChange={(value) => setFrequencyPenalty(value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="space-y-2">
                                <Label htmlFor="presencePenalty">Presence Penalty: {presencePenalty.toFixed(1)}</Label>
                                <Slider
                                    id="presencePenalty"
                                    value={[presencePenalty]}
                                    onValueChange={(value) => setPresencePenalty(value[0])}
                                    min={-2}
                                    max={2}
                                    step={0.1}
                                    className="w-full"
                                />
                            </div>
                            <div className="flex items-center space-x-2">
                                <Checkbox id="stream" />
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