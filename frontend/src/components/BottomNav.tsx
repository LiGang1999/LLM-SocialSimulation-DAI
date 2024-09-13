import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import React, { HTMLAttributes } from 'react';
import { ProgressBar } from './ProgressBar';

interface BottomNavProps extends HTMLAttributes<HTMLDivElement> {
    prevLink: string;
    nextLink: string;
    currStep: number;
    disabled: boolean;
    onClickPrev?: () => void;
    onClickNext?: () => void;
    variant?: 'default' | 'final';
}

export const BottomNav: React.FC<BottomNavProps> = ({
    prevLink,
    nextLink,
    currStep,
    disabled,
    onClickPrev,
    onClickNext,
    variant = 'default',
    ...props
}) => {
    const handlePrevClick = () => {
        if (onClickPrev) {
            onClickPrev();
        } else if (prevLink) {
            window.location.href = prevLink;
        }
    };

    const handleNextClick = () => {
        if (onClickNext && !disabled) {
            onClickNext();
        } else if (nextLink && !disabled) {
            window.location.href = nextLink;
        }
    };

    const nextButtonClass = variant === 'final'
        ? `text-2xl h-20 py-6 px-16 font-bold text-white rounded-full transition-all duration-300 flex items-center justify-center ${disabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 shadow-lg hover:shadow-xl hover:scale-105'
        }`
        : `text-xl h-16 py-4 px-8 font-bold text-white rounded-xl transition-all duration-300 flex items-center justify-center ${disabled
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-400 to-blue-500 hover:from-purple-600 hover:to-blue-600 hover:scale-105'
        }`;

    return (
        <div {...props}>
            {variant === 'default' ? (
                <div className="flex justify-between">
                    <Button
                        className="text-xl h-16 py-4 px-8 font-bold text-indigo-600 border-2 border-indigo-600 rounded-xl transition-all duration-300 hover:bg-indigo-600 hover:text-white flex items-center justify-center hover:scale-105"
                        variant="outline"
                        onClick={handlePrevClick}
                    >
                        <ChevronLeft size={24} className="mr-2" /> 上一步
                    </Button>
                    <Button
                        className={nextButtonClass}
                        disabled={disabled}
                        onClick={handleNextClick}
                    >
                        下一步 <ChevronRight size={24} className="ml-2" />
                    </Button>
                </div>
            ) : (
                <div className="flex flex-col items-center">
                    <Button
                        className={nextButtonClass}
                        disabled={disabled}
                        onClick={handleNextClick}
                    >
                        开始仿真
                    </Button>
                    <Button
                        className="mt-4 text-lg font-semibold text-indigo-500 hover:text-indigo-800 transition-colors duration-300"
                        variant="link"
                        onClick={handlePrevClick}
                    >
                        <ChevronLeft size={20} className="mr-1" /> 返回上一步
                    </Button>
                </div>
            )}
            {/* <ProgressBar currentStep={currStep} orientation='vertical' className="mx-auto mt-12" /> */}
        </div>
    );
};