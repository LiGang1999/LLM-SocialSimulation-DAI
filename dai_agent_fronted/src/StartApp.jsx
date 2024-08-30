import React from 'react';
import './App.css';

// Shared Tailwind class strings
const buttonClasses = "py-2 px-4 rounded-lg mr-4";
const cardClasses = "bg-white p-4 rounded-lg shadow-md";
const textClasses = "text-lg font-semibold mb-2";

const Header = () => (
    <header className="bg-gray-100 p-6">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">基于LLM的通用社会仿真平台</h1>
        <p className="text-gray-600 mb-6">Developed by DAI Lab, Zhejiang University.</p>
    </header>
);

const ButtonGroup = () => (
    <div className="mb-6">
        <button className={`bg-blue-500 text-white ${buttonClasses}`}>立即开始</button>
        <a href="https://github.com" className={`bg-gray-200 text-gray-700 ${buttonClasses}`}>github</a>
        <a href="mailto:contact@example.com" className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg">联系我们</a>
    </div>
);

const Card = ({ title, items }) => (
    <div className={cardClasses}>
        <h2 className={textClasses}>{title}</h2>
        <ul className="list-disc list-inside mt-2">
            {items.map((item, index) => (
                <li key={index}>{item}</li>
            ))}
        </ul>
    </div>
);

const CardGrid = () => (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card title="多智能体系统" items={["基于语言模型", "多种交互模式", "多场景适用性"]} />
        <Card title="丰富的案例与场景" items={["线上仿真案例", "线下仿真案例", "多场景适用性"]} />
        <Card title="用户友好" items={["用户界面直观", "操作流程简化"]} />
    </div>
);

const Footer = () => (
    <footer className="mt-10 text-center text-gray-600">
        © 2024 DAI Lab, Zhejiang University. All rights reserved.
    </footer>
);

const StartApp = () => (
    <div className="p-8 max-w-6xl mx-auto">
        <Header />
        <ButtonGroup />
        <CardGrid />
        <Footer />
    </div>
);

export default StartApp;