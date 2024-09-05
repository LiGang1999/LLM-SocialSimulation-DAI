import axios from 'axios'

export const apiBaseUrl = await import.meta.env.VITE_SERVER_IP;
export const apiPort = await import.meta.env.VITE_BACK_PORT;

export const api = axios.create({
    baseURL: `http://${apiBaseUrl}:${apiPort}`,
});


export namespace apis {

    export interface EventConfig {
        name: string;
        policy: string;
        websearch: string;
        description: string;
    }

    export interface AgentConfig {
        firstName: string;
        lastName: string;
        age: number;
        avatar: string;
        dailyPlan: string;
        innate: string;
        learned: string;
    }

    export interface Meta {
        template_sim_code: string;
        name: string;
        bullets: string[];
        description: string;
        start_date: string;
        curr_time: string;
        sec_per_step: number;
        maze_name: string;
        persona_names: string[];
        sim_mode: string[],
        step: number;
    }

    export interface Agent {
        name: string;
        firstName: string;
        lastName: string;
        age: number;
        dailyPlanReq: string;
        innate: any;
        learned: any;
        currently: string | undefined;
        lifestyle: string | undefined;
        livingArea: string | undefined;
        plan: string[] | undefined;
        memory: string[] | undefined;
        bibliography: string | undefined;
    }

    export interface LLMConfig {
        type: string;
        baseUrl: string;
        key: string;
        engine: string;
        temperature: number;
        maxTokens: number;
        topP: number;
        freqPenalty: number;
        presPenalty: number;
        stream: boolean;
    }

    export interface Event {
        name: string;
        policy: string;
        websearch: string;
        description: string;
    }


    export interface Template {
        simCode: string;
        events: Event[];
        personas: Agent[];
        meta: Meta;
    }

    export interface TemplateListItem {
        template_sim_code: string;
        name: string;
        bullets: string[];
        description: string;
        start_date: string;
        curr_time: string;
        sec_per_step: number;
        maze_name: string;
        persona_names: string[];
        step: number;
        sim_mode: string;
    }

    export const fetchTemplate = async (templateName: string): Promise<Template> => {
        try {
            const response = await api.get<{ meta: any, events: any[], personas: Record<string, any> }>('/fetch_template/', { params: { sim_code: templateName } });
            const { meta, events, personas } = response.data;
            return {
                simCode: templateName,
                events: events.map(event => ({
                    name: event.name,
                    policy: event.policy,
                    websearch: event.websearch,
                    description: event.description,
                })),
                personas: Object.values(personas).map(persona => ({
                    name: persona.name,
                    firstName: persona.first_name,
                    lastName: persona.last_name,
                    age: persona.age,
                    avatar: persona.avatar,
                    dailyPlanReq: persona.daily_plan_req,
                    innate: persona.innate,
                    learned: persona.learned,
                    currently: persona.currently,
                    lifestyle: persona.lifestyle,
                    livingArea: persona.living_area,
                    plan: persona.plan,
                    memory: persona.memory,
                    bibliography: persona.bibliography,
                })),
                meta,
            };
        } catch (error) {
            console.error("Error fetching template:", error);
            throw error;
        }
    };

    export const fetchTemplates = async (): Promise<TemplateListItem[]> => {
        try {
            const response = await api.get<{ envs: TemplateListItem[] }>('/fetch_templates/');
            return response.data.envs;
        } catch (error) {
            console.error("Error fetching templates:", error);
            throw error;
        }
    };

    export const startSim = async (
        simCode: string,
        template: apis.Template,
        llmConfig: apis.LLMConfig,
        initialRounds: number
    ): Promise<any> => {
        try {
            const response = await api.post('/start/', {
                simCode,
                template,
                llmConfig,
                initialRounds
            });
            return response.data;
        } catch (error) {
            console.error("Error starting simulation:", error);
            throw error;
        }
    };

    export const runSim = async (count: number): Promise<any> => {
        try {
            const response = await api.get('/run/', { params: { count } });
            return response.data;
        } catch (error) {
            console.error("Error running simulation:", error);
            throw error;
        }
    };

    export const updateEnv = async (updateData: any): Promise<any> => {
        try {
            const response = await api.post('/update_env/', updateData);
            return response.data;
        } catch (error) {
            console.error("Error updating environment:", error);
            throw error;
        }
    };

    export const agentsInfo = async (): Promise<Agent[]> => {
        try {
            const response = await api.get('/agents_info/');
            return response.data;
        } catch (error) {
            console.error("Error fetching agents info:", error);
            throw error;
        }
    };

    export const agentDetail = async (agentId: string): Promise<Agent[]> => {
        try {
            const response = await api.get(`/agent_detail/${agentId}/`);
            return response.data;
        } catch (error) {
            console.error("Error fetching agent detail:", error);
            throw error;
        }
    };

    export const sendCommand = async (command: string): Promise<any> => {
        try {
            const response = await api.get('/command/', { params: { command } });
            return response.data;
        } catch (error) {
            console.error("Error sending command:", error);
            throw error;
        }
    };

    export const publishEvent = async (eventData: EventConfig): Promise<any> => {
        try {
            const response = await api.post('/publish_events/', eventData);
            return response.data;
        } catch (error) {
            console.error("Error publishing event:", error);
            throw error;
        }
    };

}

