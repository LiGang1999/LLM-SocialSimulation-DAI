import React from 'react';
import { ArrowDown } from 'lucide-react';
import { Button } from "@/components/ui/button";

export interface SimulationGuideProps {
    onClose: () => void;
    simRounds: number;
    buttonPosition: { top: number; left: number; width: number; height: number };
}

export const SimulationGuide: React.FC<SimulationGuideProps> = ({ onClose, simRounds, buttonPosition }) => {
    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50">
            <div
                className="bg-white p-6 rounded-lg w-80 absolute"
                style={{
                    top: `${buttonPosition.top - 200}px`,
                    left: `${buttonPosition.left + buttonPosition.width / 2 - 160}px`,
                }}
            >
                <h2 className="text-xl font-bold mb-4">开始你的模拟</h2>
                <p>点击下方的"模拟{simRounds}轮"按钮开始你的模拟。</p>
                <div className="absolute bottom-[-40px] left-1/2 transform -translate-x-1/2">
                    <ArrowDown className="text-white h-8 w-8" />
                </div>
                <Button onClick={onClose} className="mt-4">
                    我知道了
                </Button>
            </div>
            <div className="absolute inset-0 z-30" onClick={onClose}></div>
        </div>
    );
};

export default SimulationGuide;