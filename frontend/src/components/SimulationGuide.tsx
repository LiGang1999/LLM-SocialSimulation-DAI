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
                className='absolute flex-col items-center align-center flex'
                style={{
                    top: `${buttonPosition.top}px`,
                    left: `${buttonPosition.left + buttonPosition.width / 2 - 160}px`,
                    transform: 'translate(0%, -100%)',
                }}
            >
                <div className="bg-white p-6 rounded-lg w-80 mb-2">
                    <h2 className="text-xl font-bold mb-4">开始你的模拟</h2>
                    <p>点击下方的"模拟{simRounds}轮"按钮开始你的模拟。</p>

                    <Button onClick={onClose} className="mt-4">
                        我知道了
                    </Button>
                </div>
                <ArrowDown className="text-white h-8 w-8 m-2 animate-bounce" />
            </div>
        </div>
    );
};

export default SimulationGuide;