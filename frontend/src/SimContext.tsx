import React, { createContext, useState, useContext } from 'react';
import { useLocalStorage } from "@uidotdev/usehooks";


interface SimContext {
    someGlobalValue: string;
    setSomeGlobalValue: (value: string) => void;
}

const SimContext = createContext<SimContext | undefined>(undefined);

export const SimContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [someGlobalValue, setSomeGlobalValue] = useLocalStorage<string>('simContext', 'Initial Value');

    return (
        <SimContext.Provider value={{ someGlobalValue, setSomeGlobalValue }}>
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