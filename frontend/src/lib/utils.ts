import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import axios from 'axios'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;
export const apiPort = import.meta.env.VITE_API_PORT;

export const api = axios.create({
  baseURL: `${apiBaseUrl}:${apiPort}`,
})

export namespace apis {

  interface EventConfig {
    name: string;
    policy: string;
    websearch: boolean;
    description: string;
  }

  interface AgentConfig {
    firstName: string;
    lastName: string;
    age: number;
    avatar: string;
    dailyPlan: string;
    innate: string;
    learned: string;
  }

  interface AgentStatus {

  }

  interface Agent {

  }

  interface LLMConfig {
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

  interface Template {
    simName: string;
    events: EventConfig[];
    agents: AgentConfig[];
    llm: LLMConfig;
  }

  interface TemplateListItem {
    name: string;
    image: string;
    points: number;
    description: string;
  }

  export const fetchTemplate = async (templateName: string): Promise<Template> => {
    try {
      const response = await api.get<{ meta: any, events: any[], personas: Record<string, any> }>('/env_info/', { params: { env_name: templateName } });
      const { meta, events, personas } = response.data;
      return {
        simName: templateName,
        events: events.map(event => ({
          name: event.name,
          policy: event.policy,
          websearch: event.websearch,
          description: event.description,
        })),
        agents: Object.values(personas).map(persona => ({
          firstName: persona.first_name,
          lastName: persona.last_name,
          age: persona.age,
          avatar: persona.avatar,
          dailyPlan: persona.daily_plan_req,
          innate: persona.innate,
          learned: persona.learned,
        })),
        llm: meta.llm_config,
      };
    } catch (error) {
      console.error("Error fetching template:", error);
      throw error;
    }
  };

  export const fetchTemplates = async (): Promise<TemplateListItem[]> => {
    try {
      const response = await api.get<{ envs: TemplateListItem[] }>('/list_envs/');
      return response.data.envs;
    } catch (error) {
      console.error("Error fetching templates:", error);
      throw error;
    }
  };

  export const startSim = async (template: string, config: any): Promise<any> => {
    try {
      const response = await api.post('/start/', { template, config });
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

  export const agentsInfo = async (): Promise<AgentStatus[]> => {
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
