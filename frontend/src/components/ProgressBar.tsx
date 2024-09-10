import React, { HTMLAttributes } from 'react';
import classNames from 'classnames';

interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
    currentStep: number;
    orientation?: 'horizontal' | 'vertical';
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
    currentStep,
    orientation = 'horizontal',
    className,
    ...props
}) => {
    const steps: string[] = ['选择模板', '方案设计', '智能体配置', '参数配置', '开始仿真'];

    const isVertical = orientation === 'vertical';

    return (
        <div
            {...props}
            className={classNames(
                `flex ${isVertical ? 'flex-col h-full' : 'flex-col'}`,
                className
            )}
        >
            <div className={`relative ${isVertical ? 'h-full' : 'mb-2'}`}>
                <div
                    className={`absolute ${isVertical
                        ? 'left-3 top-0 bottom-0 w-1.5'
                        : 'left-0 right-0 h-1.5 top-0 translate-y-[9px]'
                        } bg-gray-200`}
                >
                    <div
                        className={`${isVertical ? 'w-full' : 'h-full'} bg-blue-500 transition-all duration-300 ease-out`}
                        style={isVertical
                            ? { height: `${(currentStep / (steps.length - 1)) * 100}%` }
                            : { width: `${(currentStep / (steps.length - 1)) * 100}%` }
                        }
                    ></div>
                </div>
                <div className={`flex ${isVertical ? 'flex-col justify-between h-full' : 'justify-between'}`}>
                    {steps.map((step, index) => (
                        <div key={index} className={`flex ${isVertical ? 'items-center' : 'flex-col items-center'}`}>
                            <div className={`relative ${isVertical ? 'mr-4' : ''}`}>
                                <div
                                    className={`w-6 h-6 rounded-full
                    ${index < currentStep ? 'bg-blue-600' :
                                            index === currentStep ? 'bg-blue-500' : 'bg-gray-300'}`}
                                >
                                    {index < currentStep && (
                                        <svg className="w-4 h-4 text-white absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                        </svg>
                                    )}
                                </div>
                            </div>
                            <div className={`${isVertical ? 'text-left' : 'text-center mt-2'}`}>
                                <span className="text-sm text-gray-600">{step}</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};