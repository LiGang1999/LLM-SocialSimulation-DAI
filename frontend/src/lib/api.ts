import { ChatMessage } from '@/SimContext';
import axios from 'axios';

export const api = axios.create(({
    baseURL: `${process.env.LISTEN_PREFIX}/api`,
}))

// Setup axios interceptor to add authorization token to requests if needed
// The cookie will be automatically sent by the browser, but we keep token support
// for backwards compatibility
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Enable cookies to be sent with requests
api.defaults.withCredentials = true;

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterRequest {
    username: string;
    email: string;
    full_name: string;
    phone: string;
    institution: string;
    password: string;
}

export interface User {
    username: string;
    email?: string;
    full_name?: string;
    institution?: string;
    disabled?: boolean;
    is_admin?: boolean;
    is_sso?: boolean;
}

export interface FeedbackRequest {
    username: string;
    feedback: string;
}

export interface FeedbackAdminItem {
    id: number;
    user_username: string;
    user_email: string;
    feedback_text: string;
    timestamp: string;
}

export interface AdminTemplate {
    meta: apis.Meta;
    events: apis.Event[];
    workflow: Record<string, apis.Stage>;
    username: string;
    creation_time: number;
}


const urls = {
    login: '/login',
    logout: '/logout',
    register: '/register',
    currentUser: '/users/me',
    ssoLogin: '/ssologin',
    fetchTemplate: '/fetch_template',
    fetchTemplates: '/fetch_templates',
    deleteTemplate: '/delete_template',
    startSim: '/start',
    runSim: '/run',
    updateEnv: '/update_env',
    agentsInfo: '/personas_info',
    agentDetail: '/persona_detail',
    generateProfilesPlan: '/generate_profiles_plan',
    generateProfiles: '/generate_profiles',
    sendCommand: '/command',
    privateChat: '/chat',
    publishEvent: '/publish_events',
    queryStatus: '/status',
    getSummary: '/summary',
    submitFeedback: '/feedback',
    getFeedbacks: '/admin/feedbacks',
    getAllUserTemplates: '/admin/list_templates',
    getAllUsers: '/admin/list_users',
    userProviders: '/user_providers',
    messageSocket: (simCode: string) => {
        const token = localStorage.getItem('token');
        const uriToken = encodeURIComponent(token || "");
        return `api/ws?sim_code=${simCode}${token ? `&token=${uriToken}` : ''}`;
    }
};

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


    export interface Agent {
        name: string;
        first_name: string;
        last_name: string;
        age: number;
        innate: string;
        learned: string;
        currently: string;
        lifestyle: string;
        living_area: string;
        daily_plan_req?: string;
        bibliography?: string;
    }

    export interface LLMConfig {
        kind: 'chat' | 'embedding' | 'completion';
        base_url: string;
        api_key: string;
        model: string;
        temperature: number;
        max_tokens: number;
        top_p: number;
        frequency_penalty: number;
        presence_penalty: number;
        stream: boolean;
    }

    export interface Event {
        name: string;
        policy: string;
        websearch: string;
        description: string;
    }

    export interface Stage {
        task: string,
        output_format: Record<string, string>
    }


    export interface Template {
        simCode: string;
        events: Event[];
        personas: Agent[];
        meta: Meta;
        workflow: Record<string, Stage>
    }
    export const login = async (username: string, password: string): Promise<AuthResponse> => {
        try {
            // Login endpoint expects form data
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);

            const response = await api.post<AuthResponse>(urls.login, formData);
            return response.data;
        } catch (error) {
            console.error("Login error:", error);
            throw error;
        }
    };

    export const logout = async (): Promise<void> => {
        try {
            // We'll call this endpoint even if it doesn't exist yet, so we can add it later
            await api.post(urls.logout);
        } catch (error) {
            console.error("Logout error:", error);
        }
    };

    export const register = async (userData: RegisterRequest): Promise<User> => {
        try {
            const response = await api.post<User>(urls.register, userData);
            return response.data;
        } catch (error) {
            console.error("Registration error:", error);
            throw error;
        }
    };

    export const getCurrentUser = async (): Promise<User> => {
        try {
            const response = await api.get<User>(urls.currentUser);
            return response.data;
        } catch (error) {
            console.error("Error fetching current user:", error);
            throw error;
        }
    };

    export const ssoLogin = async (params: {
        appId: string;
        username: string;
        time: string;
        sign: string;
    }): Promise<AuthResponse> => {
        try {
            const response = await api.post<AuthResponse>(urls.ssoLogin, params);
            return response.data;
        } catch (error) {
            console.error("SSO login error:", error);
            throw error;
        }
    };

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

    function isEmptyObject(obj: Record<string, any> | any[]): boolean {
        if (Array.isArray(obj)) {
            return false;
        }
        return Object.keys(obj).length === 0;
    }

    export const fetchTemplate = async (templateName: string): Promise<Template> => {
        try {
            const response = await api.get<{ meta: any, events: any[], personas: Record<string, any>, workflow: Record<string,Stage> }>(urls.fetchTemplate, { params: { sim_code: templateName } });
            const { meta, events, personas, workflow } = response.data;
            console.log(workflow)
            return {
                simCode: templateName,
                events: isEmptyObject(events) ? [] : events.map(event => ({
                    name: event.name,
                    policy: event.policy,
                    websearch: event.websearch,
                    description: event.description,
                })),
                workflow: workflow,
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
                    act_event: [persona.name, "use", "chat"],
                    act_obj_description: undefined,
                    act_obj_pronunciatio: undefined,
                    act_obj_event: [undefined, undefined, undefined],
                    chatting_with: undefined,
                    chat: [[]],
                    chatting_with_buffer: {},
                    chatting_end_time: undefined,
                    act_path_set: false,
                    planned_path: [],

                    // New fields from Scratch class
                    vision_r: 4,
                    att_bandwidth: 3,
                    retention: 5,
                    concept_forget: 100,
                    daily_reflection_time: 60 * 3,
                    daily_reflection_size: 5,
                    overlap_reflect_th: 2,
                    kw_strg_event_reflect_th: 4,
                    kw_strg_thought_reflect_th: 4,
                    recency_w: 1,
                    relevance_w: 1,
                    importance_w: 1,
                    recency_decay: 0.99,
                    importance_trigger_max: 150,
                    importance_trigger_curr: 150, // Using importance_trigger_max as initial value
                    importance_ele_n: 0,
                    thought_count: 5,
                })),
                meta,
            };
        } catch (error) {
            console.error("Error fetching template:", error);
            throw error;
        }
    };

    export const fetchTemplates = async (): Promise<{
        public_templates: TemplateListItem[],
        user_templates: TemplateListItem[]
    }> => {
        try {
            const response = await api.get<{
                public_templates: TemplateListItem[],
                user_templates: TemplateListItem[]
            }>(urls.fetchTemplates);

            // Define priority order
            const priorityOrder = ['shbz', 'legislative_council', 'dragon_tv_demo'];

            // Sort both template arrays
            const sortTemplates = (templates: TemplateListItem[]) => {
                return templates.sort((a, b) => {
                    const aCode = a.template_sim_code;
                    const bCode = b.template_sim_code;

                    const aPriority = priorityOrder.indexOf(aCode);
                    const bPriority = priorityOrder.indexOf(bCode);

                    if (aPriority !== -1 && bPriority !== -1) {
                        return aPriority - bPriority;
                    }
                    if (aPriority !== -1) return -1;
                    if (bPriority !== -1) return 1;

                    return aCode.localeCompare(bCode);
                });
            };

            // Get public templates (should always be available)
            const publicTemplates = response.data.public_templates || [];

            // Get user templates (may be empty for unauthorized users)
            const userTemplates = response.data.user_templates || [];

            return {
                public_templates: sortTemplates(publicTemplates),
                user_templates: sortTemplates(userTemplates)
            };
        } catch (error) {
            console.error("Error fetching templates:", error);
            throw error;
        }
    };

    export const deleteTemplate = async (simCode: string): Promise<void> => {
        try {
            await api.delete(urls.deleteTemplate, { params: { sim_code: simCode } });
        } catch (error) {
            console.error("Error deleting template:", error);
            throw error;
        }
    };

    export const startSim = async (
        simCode: string,
        template: apis.Template,
        providers: Record<string, LLMConfig>,
        initialRounds: number
    ): Promise<any> => {
        try {
            const response = await api.post(urls.startSim, {
                simCode,
                template,
                providers,
                initialRounds
            });
            return response.data;
        } catch (error) {
            console.error("Error starting simulation:", error);
            throw error;
        }
    };

    export const runSim = async (count: number, simCode: string): Promise<any> => {
        try {
            const response = await api.get(urls.runSim, { params: { count, sim_code: simCode } });
            return response.data;
        } catch (error) {
            console.error("Error running simulation:", error);
            throw error;
        }
    };

    export const updateEnv = async (updateData: any, simCode: string): Promise<any> => {
        try {
            const response = await api.post(urls.updateEnv, updateData, { params: { sim_code: simCode } });
            return response.data;
        } catch (error) {
            console.error("Error updating environment:", error);
            throw error;
        }
    };

    export const agentsInfo = async (simCode: string): Promise<Agent[]> => {
        try {
            const response = await api.get(urls.agentsInfo, { params: { sim_code: simCode } });
            return response.data.personas;
        } catch (error) {
            console.error("Error fetching agents info:", error);
            throw error;
        }
    };

    export const agentDetail = async (simCode: string, agentName: string): Promise<{
        scratch: Agent,
        a_mem: Record<string, string>,
        s_mem: Record<string, string>,
    }> => {
        try {
            const response = await api.get(urls.agentDetail, { params: { sim_code: simCode, agent_name: agentName } });
            return response.data;
        } catch (error) {
            console.error("Error fetching agent detail:", error);
            throw error;
        }
    };


    export const generateProfilesPlan = async (scenario: string, request: string, agent_count: number): Promise<any> => {
        try {
            const response = await api.post(urls.generateProfilesPlan, { scenario, request, agent_count });
            return response.data;
        } catch (error) {
            console.error("Error generating profiles plan:", error);
            throw error;
        }
    }

    export const generateProfiles = async (plan: any): Promise<{ profiles: Agent[] }> => {
        try {
            const response = await api.post(urls.generateProfiles, { plan });
            return response.data;
        } catch (error) {
            console.error("Error generating profiles:", error);
            throw error;
        }
    }

    export const sendCommand = async (command: string, simCode: string): Promise<any> => {
        try {
            const response = await api.get(urls.sendCommand, { params: { command, sim_code: simCode } });
            return response.data;
        } catch (error) {
            console.error("Error sending command:", error);
            throw error;
        }
    };

    export const privateChat = async (
        simCode: string,
        person: string,
        type: 'interview' | 'whisper',
        history: ChatMessage[],
        content: string
    ): Promise<any> => {
        try {
            const formattedHistory: [string, string][] = history.map(msg => {
                const messageContent = typeof msg.content === 'string'
                    ? msg.content
                    : msg.content.execution;
                return [
                    msg.role === 'agent' ? person : 'Interviewer',
                    messageContent
                ]
            });

            const response = await api.post(urls.privateChat, {
                agent_name: person,
                type,
                history: formattedHistory,
                content
            }, { params: { sim_code: simCode } });
            return response.data;
        } catch (error) {
            console.error("Error sending private chat:", error);
            throw error;
        }
    }

    export const publishEvent = async (eventData: EventConfig, simCode: string): Promise<any> => {
        try {
            const response = await api.post(urls.publishEvent, eventData, { params: { sim_code: simCode } });
            return response.data;
        } catch (error) {
            console.error("Error publishing event:", error);
            throw error;
        }
    };

    export const queryStatus = async (simCode: string): Promise<'running' | 'stopped' | 'started' | 'terminated'> => {
        try {
            const response = await api.get(urls.queryStatus, { params: { sim_code: simCode } });
            return response.data.status;
        } catch (error) {
            console.error("Error querying status:", error);
            throw error;
        }
    }

    export const getSummary = async (simCode: string): Promise<string> => {
        try {
            const response = await api.get(urls.getSummary, { params: { sim_code: simCode } });
            return response.data.summary;
        } catch (error) {
            console.error("Error getting summary:", error);
            throw error;
        }
    }

    export const messageSocket = (simCode: string) => {
        return new WebSocket(urls.messageSocket(simCode));
    };

    export const submitFeedback = async (feedbackData: FeedbackRequest): Promise<any> => {
        try {
            const response = await api.post(urls.submitFeedback, feedbackData);
            return response.data;
        } catch (error) {
            console.error("Error submitting feedback:", error);
            throw error;
        }
    };

    export const getFeedbacks = async (): Promise<FeedbackAdminItem[]> => {
        try {
            const response = await api.get<FeedbackAdminItem[]>(urls.getFeedbacks);
            return response.data;
        } catch (error) {
            console.error("Error fetching feedbacks:", error);
            throw error;
        }
    };

    export const getAllUserTemplates = async (): Promise<AdminTemplate[]> => {
        try {
            const response = await api.get<AdminTemplate[]>(urls.getAllUserTemplates);
            return response.data;
        } catch (error) {
            console.error("Error fetching user templates:", error);
            throw error;
        }
    };

    export const getAllUsers = async (): Promise<User[]> => {
        try {
            const response = await api.get<User[]>(urls.getAllUsers);
            return response.data;
        } catch (error) {
            console.error("Error fetching users:", error);
            throw error;
        }
    };

    export const getUserProviders = async (): Promise<Record<string, LLMConfig>> => {
        try {
            const response = await api.get<Record<string, LLMConfig>>(urls.userProviders);
            return response.data;
        } catch (error) {
            console.error("Error fetching user providers:", error);
            throw error;
        }
    };

    export const updateUserProviders = async (providers: Record<string, LLMConfig>): Promise<any> => {
        try {
            const response = await api.post(urls.userProviders, providers);
            return response.data;
        } catch (error) {
            console.error("Error updating user providers:", error);
            throw error;
        }
    };
}
