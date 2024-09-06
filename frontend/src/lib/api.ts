import { ChatMessage } from '@/SimContext';
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
        sim_mode: string,
        step: number;
    }


    // An Agent interface contains:
    // {
    //     "curr_time": null,
    //     "curr_tile": null,
    //     "daily_plan_req": "Isabella Rodriguez opens Hobbs Cafe at 8am everyday, and works at the counter until 8pm, at which point she closes the cafe.",
    //     "name": "Isabella Rodriguez",
    //     "first_name": "Isabella",
    //     "last_name": "Rodriguez",
    //     "age": 34,
    //     "innate": "friendly, outgoing, hospitable",
    //     "learned": "Isabella Rodriguez is a cafe owner of Hobbs Cafe who loves to make people feel welcome. She is always looking for ways to make the cafe a place where people can come to relax and enjoy themselves. She is concerned with environmental issues and big global events, although she does not have professional knowledge in these areas.",
    //     "currently": "Isabella Rodriguez is participating in online discussions. Although not an expert, Isabella is expressing her concerns and personal ideas as a regular citizen who cares about the environment and country and is seeking to understand the impact of these events.",
    //     "lifestyle": "Isabella Rodriguez goes to bed around 11pm, awakes up around 6am.",
    //     "living_area": "the Ville:Isabella Rodriguez's apartment:main room",
    //     "daily_req": [],
    //     "f_daily_schedule": [],
    //     "f_daily_schedule_hourly_org": [],
    //     "act_address": null,
    //     "act_start_time": null,
    //     "act_duration": null,
    //     "act_description": null,
    //     "act_pronunciatio": null,
    //     "act_event": [
    //       "Isabella Rodriguez",
    //       null,
    //       null
    //     ],
    //     "act_obj_description": null,
    //     "act_obj_pronunciatio": null,
    //     "act_obj_event": [
    //       null,
    //       null,
    //       null
    //     ],
    //     "chatting_with": null,
    //     "chat": null,
    //     "chatting_with_buffer": {},
    //     "chatting_end_time": null,
    //     "act_path_set": false,
    //     "planned_path": []
    //   }
    export interface Agent {
        curr_time?: number;
        curr_tile?: string;
        daily_plan_req: string;
        name: string;
        first_name: string;
        last_name: string;
        age: number;
        innate: string;
        learned: string;
        currently?: string;
        lifestyle?: string;
        living_area?: string;
        daily_req: string[];
        f_daily_schedule: string[];
        f_daily_schedule_hourly_org: string[];
        act_address?: string;
        act_start_time?: string;
        act_duration?: string;
        act_description?: string;
        act_pronunciatio?: string;
        act_event: [string, string?, string?];
        act_obj_description?: string;
        act_obj_pronunciatio?: string;
        act_obj_event: [string?, string?, string?];
        chatting_with?: string;
        chat?: string;
        chatting_with_buffer: Record<string, string>;
        chatting_end_time?: string;
        act_path_set: boolean;
        planned_path: string[];
        avatar?: string;
        plan?: string[];
        memory?: string[];
        bibliography?: string;
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
                    curr_time: undefined,
                    curr_tile: undefined,
                    daily_plan_req: persona.daily_plan_req,
                    name: persona.name,
                    first_name: persona.first_name,
                    last_name: persona.last_name,
                    age: persona.age,
                    innate: persona.innate,
                    learned: persona.learned,
                    currently: persona.currently,
                    lifestyle: persona.lifestyle,
                    living_area: persona.living_area,
                    daily_req: [],
                    f_daily_schedule: [],
                    f_daily_schedule_hourly_org: [],
                    act_address: undefined,
                    act_start_time: undefined,
                    act_duration: undefined,
                    act_description: undefined,
                    act_pronunciatio: undefined,
                    act_event: [persona.name, undefined, undefined],
                    act_obj_description: undefined,
                    act_obj_pronunciatio: undefined,
                    act_obj_event: [undefined, undefined, undefined],
                    chatting_with: undefined,
                    chat: undefined,
                    chatting_with_buffer: {},
                    chatting_end_time: undefined,
                    act_path_set: false,
                    planned_path: [],
                    // Additional fields from your original mapping
                    // avatar: persona.avatar,
                    // plan: persona.plan,
                    // memory: persona.memory,
                    // bibliography: persona.bibliography,
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



    // get the information for all agents, briefly
    export const agentsInfo = async (sim_code: string): Promise<Agent[]> => {
        try {
            const response = await api.get('/personas_info/', {
                params: { sim_code }
            });
            return response.data;
        } catch (error) {
            console.error("Error fetching agents info:", error);
            throw error;
        }
    };

    // get the information for a single agent, in detail
    export const agentDetail = async (sim_code: string, agent_name: string): Promise<Agent> => {
        try {
            const response = await api.get('/persona_detail/', {
                params: { sim_code, agent_name }
            });
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

    export const privateChat = async (
        sim_code: string,
        person: string,
        type: 'analysis' | 'whisper',
        history: ChatMessage[],
        content: string
    ): Promise<any> => {
        try {
            // Convert ChatMessage[] to the required history format
            const formattedHistory: [string, string][] = history.map(msg => [
                msg.role === 'agent' ? person : 'Interviewer',
                msg.content
            ]);

            const response = await api.post('/chat/', {
                sim_code,
                agent_name: person,
                type,
                history: formattedHistory,
                content
            });
            return response.data;
        } catch (error) {
            console.error("Error sending private chat:", error);
            throw error;
        }
    }

    export const publishEvent = async (eventData: EventConfig): Promise<any> => {
        try {
            const response = await api.post('/publish_events/', eventData);
            return response.data;
        } catch (error) {
            console.error("Error publishing event:", error);
            throw error;
        }
    };


    export const queryStatus = async (): Promise<'running' | 'stopped' | 'started'> => {
        try {
            const response = await api.get('/status/');
            return response.data.status;
        } catch (error) {
            console.error("Error querying status:", error);
            throw error;
        }
    }

    export const chatSocket = () => {
        return new WebSocket(`ws://${apiBaseUrl}:${apiPort}/ws/chat`);
    }

    export const logSocket = () => {
        return new WebSocket(`ws://${apiBaseUrl}:${apiPort}/ws/log`);
    }


}

