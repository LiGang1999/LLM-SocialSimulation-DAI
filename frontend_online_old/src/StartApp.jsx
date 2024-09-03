import './App.css';
import React, { useState, useEffect } from 'react';
import { Check, ChevronLeft, ChevronRight } from 'lucide-react';
import start1 from './assets/start1.jpg';
import start2 from './assets/start2.jpg';
import start3 from './assets/start3.jpg';

const Header = () => (
    <div className="mb-4">
        <h1 className="text-4xl font-bold mb-1">基于LLM的通用社会仿真平台</h1>
        <p className="text-sm text-gray-600 flex items-center">
            <span className="bg-orange-500 w-2 h-2 inline-block rounded-full mr-2"></span>
            Developed by DAI Lab, Zhejiang University.
        </p>
    </div>
);

const ButtonGroup = () => (
    <div className="flex space-x-4 mb-6">
        <button className="bg-green-500 text-white px-6 py-2 rounded-full">立即开始</button>
        <button className="bg-white text-blue-500 border border-blue-500 px-6 py-2 rounded-full flex items-center">
            github
            <svg className="w-3 h-3 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
        </button>
        <button className="bg-white text-blue-500 border border-blue-500 px-6 py-2 rounded-full">联系我们</button>
    </div>
);

const FeatureCard = ({ title, features }) => (
    <div className="bg-orange-50 rounded-lg p-4">
        <h3 className="font-bold mb-2">{title}</h3>
        <ul>
            {features.map((feature, index) => (
                <li key={index} className="flex items-center mb-1">
                    <Check className="text-orange-500 mr-2 flex-shrink-0" size={16} />
                    <span>{feature}</span>
                </li>
            ))}
        </ul>
    </div>
);

const FeatureGrid = () => (
    <div className="grid grid-cols-3 gap-4 mb-6">
        <FeatureCard
            title="多智能体系统"
            features={["基于大语言模型", "多种交互模式", "智能体决策机制"]}
        />
        <FeatureCard
            title="丰富的案例与场景"
            features={["线上仿真案例", "线下仿真案例", "多场景适用性"]}
        />
        <FeatureCard
            title="用户友好"
            features={["用户界面直观", "操作流程简化", "操作流程简化"]}
        />
    </div>
);

const StructureChart = () => {
    const images = [start1, start2, start3];
    const [currentIndex, setCurrentIndex] = useState(0);

    useEffect(() => {
        const timer = setInterval(() => {
            setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
        }, 5000);
        return () => clearInterval(timer);
    }, []);

    const goToPrevious = () => {
        setCurrentIndex((prevIndex) => (prevIndex - 1 + images.length) % images.length);
    };

    const goToNext = () => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % images.length);
    };

    return (
        <div className="relative h-full flex items-center justify-center bg-gray-100 rounded-lg overflow-hidden">
            <img
                src={images[currentIndex]}
                alt={`Structure Chart ${currentIndex + 1}`}
                className="max-w-full max-h-full object-contain"
            />
            <button
                onClick={goToPrevious}
                className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-50 rounded-full p-2 hover:bg-opacity-75"
            >
                <ChevronLeft size={24} />
            </button>
            <button
                onClick={goToNext}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-white bg-opacity-50 rounded-full p-2 hover:bg-opacity-75"
            >
                <ChevronRight size={24} />
            </button>
            <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
                {images.map((_, index) => (
                    <div
                        key={index}
                        className={`w-2 h-2 rounded-full ${index === currentIndex ? 'bg-blue-500' : 'bg-gray-300'}`}
                    />
                ))}
            </div>
        </div>
    );
};

const Footer = () => (
    <footer className="text-gray-600 text-xs mt-4">
        <p>[1]Guo T, et al. Large language model based multi-agents: A survey... 2024.</p>
        <p>[2]Park J S, et al. Generative agents: Interactive simulacra... 2023.</p>
        <p>[3]Wang L, et al. A survey on large language model... 2024.</p>
    </footer>
);

const StartApp = () => (
    <div className="max-w-7xl mx-auto px-4 py-8">
        <Header />
        <ButtonGroup />
        <div className="flex space-x-8">
            <div className="w-1/2">
                <FeatureGrid />
            </div>
            <div className="w-1/2">
                <StructureChart />
            </div>
        </div>
        <Footer />
    </div>
);

export default StartApp;
