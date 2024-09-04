import React, { createContext, useState, useContext } from 'react';
import { useLocalStorage } from "@uidotdev/usehooks";
import { apis } from './lib/api';

interface SimContext {
    currSimCode: string;
    allTemplates: apis.TemplateListItem[] | null;
    currentTemplate: apis.Template | null;
}

interface SimContextPair {
    data: SimContext;
    setData: (value: SimContext) => void;
}

const SimContext = createContext<SimContextPair | undefined>(undefined);

export const SimContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [get, set] = useLocalStorage<SimContext>('simContext', {
        currSimCode: "",
        allTemplates: [],
        currentTemplate: null
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