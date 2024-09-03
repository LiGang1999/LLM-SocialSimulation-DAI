import React, { HTMLAttributes } from 'react';

interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
    currentStep: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ currentStep, ...props }) => {
    const steps: string[] = ['选择模板', '方案设计', '智能体配置', '参数配置', '开始仿真'];

    return (
        <div {...props}>
            <div className="relative mx-6 mb-2">
                <div className="absolute left-0 right-0 top-1/2 h-1.5 bg-gray-200 -translate-y-1/2">
                    <div
                        className="h-full bg-blue-500 transition-all duration-300 ease-out"
                        style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
                    ></div>
                </div>
                <div className="flex justify-between">
                    {steps.map((_, index) => (
                        <div key={index} className="relative">
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
                    ))}
                </div>
            </div>
            <div className="flex justify-between px-2"> {/* Added px-2 to align text with dots */}
                {steps.map((step, index) => (
                    <div key={index} className="text-center">
                        <span className="text-sm text-gray-600">{step}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};