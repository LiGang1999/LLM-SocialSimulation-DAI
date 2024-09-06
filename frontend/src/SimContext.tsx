import React, { createContext, useState, useContext } from 'react';
import { useLocalStorage, useSessionStorage } from "@uidotdev/usehooks";
import { apis } from './lib/api';

export interface ChatMessage {
    sender: string;
    role: string;
    type: 'public' | 'private';
    content: string;
    timestamp: string;
    subject: string;
    // avatar: string;
}

export interface SimContext {
    isRunning: boolean;
    isStarted: boolean;
    templateCode: string | undefined;
    currSimCode: string | undefined;
    allTemplates: apis.TemplateListItem[] | undefined;
    currentTemplate: apis.Template | undefined;
    agents: { [agentName: string]: apis.Agent },
    llmConfig: apis.LLMConfig | undefined;
    initialRounds: number | undefined;
    publicMessages: ChatMessage[];  // Add public messages
    privateMessages: { [agentName: string]: ChatMessage[] };  // Add private messages by agent
    logs: string[] | undefined;
}

interface SimContextPair {
    data: SimContext;
    setData: (value: SimContext) => void;
}

const SimContext = createContext<SimContextPair | undefined>(undefined);

export const SimContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [get, set] = useLocalStorage<SimContext>('simContext', {
        isRunning: false,
        isStarted: false,
        currSimCode: "",
        templateCode: "",
        agents: {},
        allTemplates: [],
        currentTemplate: undefined,
        llmConfig: undefined,
        initialRounds: 0,
        publicMessages: [],
        privateMessages: {},
        logs: []
    });

    return (
        <SimContext.Provider value={{ data: get, setData: set }}>
            {children}
        </SimContext.Provider>
    );
};

export const useSimContext = () => {
    const context = useContext(SimContext);
    if (context === undefined) {
        throw new Error('useGlobalState must be used within a GlobalStateProvider');
    }
    return context;
};