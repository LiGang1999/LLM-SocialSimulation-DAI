import axios, { AxiosResponse } from 'axios';

// Types
export type Template = string;
export type TemplateDetails = {
    parameters: string[];
    system_prompt: string;
    user_prompt: string;
    example: string;
};
export type Params = { [key: string]: string };
export type GeneratedPrompts = {
    system: string;
    user: string;
};
export type LLMParams = {
    base_url: string;
    api_key: string;
    model: string;
    max_tokens: number;
    top_p: number;
    temperature: number;
};

// Base URL for API calls
const API_BASE_URL = '/api'; // Adjust this to your backend URL

// Create an axios instance with the base URL
const api = axios.create({
    baseURL: API_BASE_URL,
});

// Generic error handler
const handleApiError = (error: any): never => {
    if (axios.isAxiosError(error)) {
        throw new Error(error.response?.data?.detail || error.message);
    }
    throw error;
};

// Individual API functions

export const fetchPromptTemplates = async (): Promise<Template[]> => {
    try {
        const response: AxiosResponse<{ templates: Template[] }> = await api.get('/prompt_templates');
        return response.data.templates;
    } catch (error) {
        return handleApiError(error);
    }
};

export const fetchPromptTemplate = async (templateName: string): Promise<TemplateDetails> => {
    try {
        const response: AxiosResponse<TemplateDetails> = await api.get(`/prompt_template/${templateName}`);
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const generatePrompt = async (
    systemPrompt: string,
    userPrompt: string,
    parameters: Params,
    exampleOutput: string,
): Promise<GeneratedPrompts> => {
    try {
        const response: AxiosResponse<GeneratedPrompts> = await api.post('/generate_prompt', {
            system_prompt: systemPrompt,
            user_prompt: userPrompt,
            parameters,
            example: exampleOutput
        });
        return response.data;
    } catch (error) {
        return handleApiError(error);
    }
};

export const generateResponse = async (
    systemPrompt: string,
    userPrompt: string,
    parameters: Params,
    llmParams: LLMParams,
    exampleOutput: string,
): Promise<string> => {
    try {
        const response: AxiosResponse<{ content: string }> = await api.post('/generate_response', {
            system_prompt: systemPrompt,
            user_prompt: userPrompt,
            parameters,
            llm_params: llmParams,
            example: exampleOutput
        });
        return response.data.content;
    } catch (error) {
        return handleApiError(error);
    }
};