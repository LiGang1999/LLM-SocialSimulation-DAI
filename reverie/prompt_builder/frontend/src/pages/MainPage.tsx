import React, { useEffect, useState, useCallback } from 'react';
import {
    Template,
    TemplateDetails,
    Params,
    GeneratedPrompts,
    LLMParams,
    fetchPromptTemplates,
    fetchPromptTemplate,
    generatePrompt,
    generateResponse
} from '../api';

const MainPage: React.FC = () => {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [templateDetails, setTemplateDetails] = useState<TemplateDetails>({
        params: [],
        system_prompt: '',
        user_prompt: ''
    });
    const [params, setParams] = useState<Params>({});
    const [systemPrompt, setSystemPrompt] = useState<string>('');
    const [userPrompt, setUserPrompt] = useState<string>('');
    const [generatedPrompts, setGeneratedPrompts] = useState<GeneratedPrompts>({
        system: '',
        user: ''
    });
    const [response, setResponse] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [llmParams, setLlmParams] = useState<LLMParams>({
        base_url: 'https://api.openai.com/v1/completions',
        api_key: '',
        model: 'gpt-3.5-turbo',
        max_tokens: 150,
        top_p: 1.0,
        temperature: 1.0
    });

    useEffect(() => {
        const getTemplates = async () => {
            try {
                const fetchedTemplates = await fetchPromptTemplates();
                setTemplates(fetchedTemplates);
            } catch (err) {
                setError('Failed to fetch templates');
                console.error(err);
            }
        };
        getTemplates();
    }, []);

    useEffect(() => {
        const getTemplateDetails = async () => {
            if (selectedTemplate) {
                try {
                    const details = await fetchPromptTemplate(selectedTemplate);
                    setTemplateDetails(details);
                    setParams(details.params.reduce((acc, param) => {
                        acc[param] = '';
                        return acc;
                    }, {} as Params));
                    setSystemPrompt(details.system_prompt);
                    setUserPrompt(details.user_prompt);
                } catch (err) {
                    setError('Failed to fetch template details');
                    console.error(err);
                }
            }
        };
        getTemplateDetails();
    }, [selectedTemplate]);

    const handleGenerate = async () => {
        setLoading(true);
        setError(null);
        try {
            const prompts = await generatePrompt(systemPrompt, userPrompt, params);
            setGeneratedPrompts(prompts);

            const generatedResponse = await generateResponse(systemPrompt, userPrompt, params, llmParams);
            setResponse(generatedResponse);
        } catch (err) {
            setError('An error occurred while generating the response');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleParamChange = useCallback((key: string, value: string) => {
        setParams(prev => ({
            ...prev,
            [key]: value
        }));
    }, []);

    const addParam = useCallback(() => {
        const newParamKey = prompt('Enter new parameter name:');
        if (newParamKey) {
            setParams(prev => ({
                ...prev,
                [newParamKey]: ''
            }));
        }
    }, []);

    const removeParam = useCallback((key: string) => {
        setParams(prev => {
            const newParams = { ...prev };
            delete newParams[key];
            return newParams;
        });
    }, []);

    const handleLLMParamChange = useCallback((key: keyof LLMParams, value: string | number) => {
        setLlmParams(prev => ({
            ...prev,
            [key]: value
        }));
    }, []);

    return (
        <div className="min-h-screen bg-white">
            <div className="mx-auto py-6 px-4">
                {error && (
                    <div className="mb-4 border text-red-500 border-black px-4 py-3" role="alert">
                        <strong className="font-bold">Error:</strong>
                        <span className="block sm:inline"> {error}</span>
                    </div>
                )}
                {loading && (
                    <div className="mb-4 border border-black px-4 py-3" role="alert">
                        <span className="block sm:inline">Loading...</span>
                    </div>
                )}
                <div className="border border-black">
                    <div className="px-4 py-5">
                        <div className="grid grid-cols-2 gap-6">
                            {/* Left Column */}
                            <div className="space-y-6">
                                {/* Prompt Template Selector */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">Prompt Template</label>
                                    <select
                                        value={selectedTemplate}
                                        onChange={e => setSelectedTemplate(e.target.value)}
                                        className="mt-1 block w-full pl-3 bg-white pr-10 py-2 text-base border border-black focus:outline-none focus:border-black sm:text-sm"
                                        disabled={templates.length === 0}
                                        style={{ borderRadius: 0 }}
                                    >
                                        <option value="">Select a template</option>
                                        {templates.map(template => (
                                            <option key={template} value={template}>{template}</option>
                                        ))}
                                    </select>
                                </div>

                                {/* Parameter List */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">Parameters</label>
                                    <button
                                        onClick={addParam}
                                        className="mb-2 px-3 py-1 bg-black text-white hover:bg-blue-800 hover:text-white text-sm font-medium"
                                        style={{ borderRadius: 0 }}
                                    >
                                        Add Parameter
                                    </button>
                                    <div className="space-y-2">
                                        {Object.entries(params).map(([key, value]) => (
                                            <div key={key} className="flex items-center">
                                                <span className="w-1/4 text-sm">{key}</span>
                                                <input
                                                    type="text"
                                                    value={value}
                                                    onChange={e => handleParamChange(key, e.target.value)}
                                                    className="w-2/3 p-2 border border-black focus:outline-none focus:border-black"
                                                />
                                                <button
                                                    onClick={() => removeParam(key)}
                                                    className="w-1/12 ml-2 px-2 py-1 bg-black text-white"
                                                >
                                                    X
                                                </button>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* System Prompt Input */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">System Prompt</label>
                                    <textarea
                                        value={systemPrompt}
                                        onChange={e => setSystemPrompt(e.target.value)}
                                        className="mt-1 p-1 block w-full sm:text-sm border border-black focus:outline-none focus:border-black bg-white"
                                        rows={4}
                                    ></textarea>
                                </div>

                                {/* User Prompt Input */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">User Prompt</label>
                                    <textarea
                                        value={userPrompt}
                                        onChange={e => setUserPrompt(e.target.value)}
                                        className="mt-1 p-1 block w-full sm:text-sm border border-black focus:outline-none focus:border-black bg-white"
                                        rows={4}
                                    ></textarea>
                                </div>
                                {/* Generate Button */}
                                <button
                                    onClick={handleGenerate}
                                    className="w-full mt-4 inline-flex justify-center items-center px-4 py-2 border border-black text-sm font-medium text-white bg-black hover:bg-blue-800 hover:text-white focus:outline-none"
                                    style={{ borderRadius: 0 }}
                                >
                                    Generate
                                </button>
                            </div>

                            {/* Right Column */}
                            <div className="space-y-6">
                                {/* Generated Prompts */}
                                <div className="border border-black p-4 mb-4">
                                    <h2 className="text-lg font-medium mb-2">Generated Prompts</h2>
                                    <div className="mb-4">
                                        <h3 className="text-sm font-medium">System Prompt</h3>
                                        <p className="mt-1 text-sm whitespace-pre-wrap">{generatedPrompts.system}</p>
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-medium">User Prompt</h3>
                                        <p className="mt-1 text-sm whitespace-pre-wrap">{generatedPrompts.user}</p>
                                    </div>
                                </div>

                                {/* Response Display */}
                                <div className="border border-black p-4">
                                    <h2 className="text-lg font-medium mb-2">Response</h2>
                                    {loading ? (
                                        <p className="text-sm">Loading...</p>
                                    ) : (
                                        <p className="text-sm whitespace-pre-wrap">{response}</p>
                                    )}
                                </div>

                                {/* LLM Config Form */}
                                <div className="border border-black px-4 py-5">
                                    <h2 className="text-lg font-medium mb-4">LLM Configuration</h2>
                                    <div className="grid grid-cols-2 gap-4">
                                        {(Object.keys(llmParams) as Array<keyof LLMParams>).map(key => (
                                            <div key={key}>
                                                <label htmlFor={key} className="block text-sm font-medium">{key}</label>
                                                <input
                                                    type="text"
                                                    id={key}
                                                    value={llmParams[key]}
                                                    onChange={e => handleLLMParamChange(key, e.target.value)}
                                                    className="mt-1 bg-white p-1 focus:outline-none focus:border-black block w-full shadow-sm sm:text-sm border border-black"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                </div>


                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MainPage;