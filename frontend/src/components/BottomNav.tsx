import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import React, { HTMLAttributes } from 'react';
import { ProgressBar } from './ProgressBar';

interface BottomNavProps extends HTMLAttributes<HTMLDivElement> {
    prevLink: string;
    nextLink: string;
    currStep: number;
    disabled: boolean;
}

export const BottomNav: React.FC<BottomNavProps> = ({ prevLink, nextLink, currStep, disabled, ...props }) => {
    return (
        <div {...props}>
            <div className="flex justify-between">
                <a href={prevLink}>
                    <Button
                        className="text-xl h-16 py-4 px-8 font-bold text-indigo-600 border-2 border-indigo-600 rounded-xl transition-all duration-300 hover:bg-indigo-600 hover:text-white flex items-center justify-center  hover:scale-105"
                        variant="outline"
                    >
                        <ChevronLeft size={24} className="mr-2" /> 上一步
                    </Button>
                </a>
                <a href={disabled ? "#" : nextLink} className={`${disabled ? 'cursor-not-allowed' : ''}`}>
                    <Button
                        className={`text-xl h-16 py-4 px-8 font-bold text-white rounded-xl transition-all duration-300 flex items-center justify-center ${disabled
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 hover:scale-105'
                            }`}
                        disabled={disabled}
                    >
                        下一步 <ChevronRight size={24} className="ml-2" />
                    </Button>
                </a>
            </div>
            <ProgressBar currentStep={currStep} className="mx-auto mt-12" />
        </div>
    );
};
