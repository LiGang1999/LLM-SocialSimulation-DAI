import React from 'react';
import { Info as InfoIcon } from 'lucide-react';

interface DescriptionCardProps {
    title: string;
    description: string;
}

const DescriptionCard: React.FC<DescriptionCardProps> = ({ title, description }) => {
    return (
        <div className="mb-8 rounded-lg p-6 bg-white bg-opacity-30">
            <div className="flex items-center mb-4">
                <InfoIcon className="w-6 h-6 text-blue-500 mr-2" />
                <h3 className="text-xl font-semibold text-gray-800">{title}</h3>
            </div>
            <p className="text-gray-700 leading-relaxed">
                {description}
            </p>
        </div>
    );
};

export default DescriptionCard;