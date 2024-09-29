import React, { useEffect, useState, useCallback, useRef } from 'react';
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

import CreatableSelect from 'react-select/creatable';


import { X } from 'lucide-react';



interface AutoResizeTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
    value: string;
    onChange: (e: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

const AutoResizeTextarea: React.FC<AutoResizeTextareaProps> = ({ value, onChange, className, style, ...rest }) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (textareaRef.current) {
            // Reset height to auto to calculate the correct scrollHeight
            textareaRef.current.style.height = 'auto';
            // Set the height to match the content
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }, [value]);

    return (
        <textarea
            {...rest}
            ref={textareaRef}
            value={value}
            onChange={onChange}
            className={className}
            style={{ ...style, height: 'auto', overflowY: 'hidden' }}
        ></textarea>
    );
};




interface DialogProps {
    isOpen: boolean;
    onClose: () => void;
    children: React.ReactNode;
}

const Dialog: React.FC<DialogProps> = ({ isOpen, onClose, children }) => {
    if (!isOpen) return null;

    const handleOverlayClick = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    }, [onClose]);

    return (
        <div
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={handleOverlayClick}
        >
            <div className="bg-white border border-black p-4 w-96 relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 rounded-none p-1 text-white hover:text-white hover:bg-red-800 border-none"
                    aria-label="Close"
                >
                    <X size={20} />
                </button>
                {children}
            </div>
        </div>
    );
};

interface AddParameterDialogProps {
    isOpen: boolean;
    onClose: () => void;
    onAdd: (key: string, value: string) => void;
}

export const AddParameterDialog: React.FC<AddParameterDialogProps> = ({ isOpen, onClose, onAdd }) => {
    const [key, setKey] = useState('');
    const [value, setValue] = useState('');

    const handleAdd = () => {
        if (key) {
            onAdd(key, value);
            setKey('');
            setValue('');
            onClose();
        }
    };

    return (
        <Dialog isOpen={isOpen} onClose={onClose}>
            <h2 className="text-lg font-medium mb-4">Add Parameter</h2>
            <input
                type="text"
                value={key}
                onChange={(e) => setKey(e.target.value)}
                placeholder="Parameter name"
                className="w-full mb-2 p-1 border border-black bg-white"
            />
            <input
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                placeholder="Parameter value"
                className="w-full mb-4 p-1 border border-black bg-white"
            />
            <button
                onClick={handleAdd}
                className="w-full px-4 py-1 bg-black text-white hover:bg-blue-800"
                style={{ borderRadius: 0 }}
            >
                Add
            </button>
        </Dialog>
    );
};

interface LLMConfigDialogProps {
    isOpen: boolean;
    onClose: () => void;
    llmParams: LLMParams;
    onParamChange: (key: keyof LLMParams, value: string | number) => void;
}

export const LLMConfigDialog: React.FC<LLMConfigDialogProps> = ({ isOpen, onClose, llmParams, onParamChange }) => {
    return (
        <Dialog isOpen={isOpen} onClose={onClose}>
            <h2 className="text-lg font-medium mb-4">LLM Configuration</h2>
            <div className="space-y-1">
                {(Object.keys(llmParams) as Array<keyof LLMParams>).map((key) => (
                    <div key={key}>
                        <label htmlFor={key} className="block text-sm font-medium">
                            {key}
                        </label>
                        <input
                            type="text"
                            id={key}
                            value={llmParams[key]}
                            onChange={(e) => onParamChange(key, e.target.value)}
                            className="mt-1 w-full p-1 bg-white font-mono text-sm border border-black"
                        />
                    </div>
                ))}
            </div>
        </Dialog>
    );
};

const MainPage: React.FC = () => {
    const [templates, setTemplates] = useState<Template[]>([]);
    const [selectedTemplate, setSelectedTemplate] = useState<string>('');
    const [templateDetails, setTemplateDetails] = useState<TemplateDetails>({
        parameters: [],
        system_prompt: '',
        user_prompt: '',
        example: "",
    });
    const [params, setParams] = useState<Params>({});
    const [systemPrompt, setSystemPrompt] = useState<string>('');
    const [userPrompt, setUserPrompt] = useState<string>('');
    const [exampleOutput, setExampleOuput] = useState<string>('');
    const [generatedPrompts, setGeneratedPrompts] = useState<GeneratedPrompts>({
        system: '',
        user: ''
    });
    const [response, setResponse] = useState<string>('');
    const [loading, setLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [llmParams, setLlmParams] = useState<LLMParams>({
        base_url: '',
        api_key: '',
        model: 'gpt-3.5-turbo',
        max_tokens: 150,
        top_p: 1.0,
        temperature: 1.0
    });
    const [isAddParamDialogOpen, setIsAddParamDialogOpen] = useState(false);
    const [isLLMConfigDialogOpen, setIsLLMConfigDialogOpen] = useState(false);

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
                    setParams(details.parameters.reduce((acc, param) => {
                        acc[param] = '';
                        return acc;
                    }, {} as Params));
                    setSystemPrompt(details.system_prompt);
                    setUserPrompt(details.user_prompt);
                    setExampleOuput(details.example)
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
            const prompts = await generatePrompt(systemPrompt, userPrompt, params, exampleOutput);
            setGeneratedPrompts(prompts);

            const generatedResponse = await generateResponse(systemPrompt, userPrompt, params, llmParams, exampleOutput);
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

    const handleAddParam = useCallback((key: string, value: string) => {
        setParams(prev => ({
            ...prev,
            [key]: value
        }));
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
        <div className="min-h-screen bg-white ">
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

                                    <CreatableSelect options={templates.map(template => ({ value: template, label: template }))} />
                                    {/* <select
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
                                    </select> */}
                                </div>

                                {/* Parameter List */}
                                <div className="mb-4">
                                    <div className='flex items-center align-center'>
                                        <label className="block text-sm font-medium mb-1 mr-3">Parameters</label>
                                        <button
                                            onClick={() => setIsAddParamDialogOpen(true)}
                                            className="mb-2 px-3 py-0 bg-black text-white hover:bg-blue-800 hover:text-white text-sm font-medium"
                                            style={{ borderRadius: 0 }}
                                        >
                                            Add Parameter
                                        </button>
                                    </div>

                                    <div className="space-y-1">
                                        {Object.entries(params).map(([key, value]) => (
                                            <div key={key} className="flex items-center">
                                                <span className="w-1/4 text-sm">{key}</span>
                                                <input
                                                    type="text"
                                                    value={value}
                                                    onChange={e => handleParamChange(key, e.target.value)}
                                                    className="w-2/3 px-1  font-mono text-sm border border-black focus:outline-none bg-white focus:border-black"
                                                />
                                                <button
                                                    onClick={() => removeParam(key)}
                                                    className="w-1/12 ml-2 text-sm px-0 py-0 bg-black text-white hover:bg-blue-800 hover:text-white"
                                                    style={{ borderRadius: 0 }}
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
                                    <AutoResizeTextarea
                                        value={systemPrompt}
                                        onChange={e => setSystemPrompt(e.target.value)}
                                        className="mt-1 p-1 font-mono block w-full text-xs sm:text-xs border border-black focus:outline-none focus:border-black bg-white"
                                    ></AutoResizeTextarea>
                                </div>

                                {/* User Prompt Input */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">User Prompt</label>
                                    <AutoResizeTextarea
                                        value={userPrompt}
                                        onChange={e => setUserPrompt(e.target.value)}
                                        className="mt-1 p-1  font-mono block w-full text-xs sm:text-xs border border-black focus:outline-none focus:border-black bg-white"
                                    ></AutoResizeTextarea>
                                </div>

                                {/* Example Output Input */}
                                <div className="mb-4">
                                    <label className="block text-sm font-medium mb-1">Example JSON Output</label>
                                    <AutoResizeTextarea
                                        value={exampleOutput}
                                        onChange={e => setExampleOuput(e.target.value)}
                                        className="mt-1 p-1  font-mono block w-full text-xs sm:text-xs border border-black focus:outline-none focus:border-black bg-white"
                                    ></AutoResizeTextarea>
                                </div>
                                {/* Generate Button */}
                                <button
                                    onClick={() => setIsLLMConfigDialogOpen(true)}
                                    className="w-full mt-4 inline-flex justify-center items-center px-4 py-2 border border-black text-sm font-medium text-white bg-black hover:bg-blue-800 hover:text-white focus:outline-none"
                                    style={{ borderRadius: 0 }}
                                >
                                    Open LLM Configuration
                                </button>
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
                                        <p className="mt-1 text-xs whitespace-pre-wrap font-mono">{generatedPrompts.system}</p>
                                    </div>
                                    <div className='border-b border-gray-300 mb-3'></div>
                                    <div>
                                        <h3 className="text-sm font-medium">User Prompt</h3>
                                        <p className="mt-1 text-xs font-mono whitespace-pre-wrap">{generatedPrompts.user}</p>
                                    </div>
                                </div>

                                {/* Response Display */}
                                <div className="border border-black p-4">
                                    <h2 className="text-lg font-medium mb-2">Response</h2>
                                    {loading ? (
                                        <p className="text-sm">Loading...</p>
                                    ) : (
                                        <p className="text-xs font-mono whitespace-pre-wrap">{response}</p>
                                    )}
                                </div>


                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Custom Dialogs */}
            <AddParameterDialog
                isOpen={isAddParamDialogOpen}
                onClose={() => setIsAddParamDialogOpen(false)}
                onAdd={handleAddParam}
            />

            <LLMConfigDialog
                isOpen={isLLMConfigDialogOpen}
                onClose={() => setIsLLMConfigDialogOpen(false)}
                llmParams={llmParams}
                onParamChange={handleLLMParamChange}
            />
        </div>
    );
};

export default MainPage;