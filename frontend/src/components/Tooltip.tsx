import React, { useState, useEffect, useRef, RefObject, useCallback } from 'react';
import { InfoIcon } from 'lucide-react';

interface TooltipProps {
    message: string;
    isVisible: boolean;
    anchorRef: RefObject<HTMLElement>;
    onClose?: () => void;
}

export const Tooltip: React.FC<TooltipProps> = ({
    message,
    isVisible,
    anchorRef,
    onClose,
}) => {
    const tooltipRef = useRef<HTMLDivElement>(null);

    const updatePosition = useCallback(() => {
        if (anchorRef.current && tooltipRef.current && isVisible) {
            const anchorRect = anchorRef.current.getBoundingClientRect();
            const tooltipRect = tooltipRef.current.getBoundingClientRect();

            let top = anchorRect.top + anchorRect.height / 2 - tooltipRect.height / 2;
            let left = anchorRect.right + 10;

            tooltipRef.current.style.top = `${top}px`;
            tooltipRef.current.style.left = `${left}px`;
        }
    }, [isVisible, anchorRef]);


    const handleClickOutside = useCallback(
        (event: MouseEvent) => {
            if (
                anchorRef.current &&
                !anchorRef.current.contains(event.target as Node)
            ) {
                if (onClose && typeof onClose === 'function') {
                    onClose();
                } else {
                    console.warn(
                        'Tooltip: onClose prop is not provided or not a function'
                    );
                }
            }
        },
        [anchorRef, onClose]
    );

    useEffect(() => {
        if (isVisible) {
            document.addEventListener('click', handleClickOutside);
            window.addEventListener('resize', updatePosition);
            updatePosition();
        } else {
            document.removeEventListener('click', handleClickOutside);
            window.removeEventListener('resize', updatePosition);
        }
        return () => {
            document.removeEventListener('click', handleClickOutside);
            window.removeEventListener('resize', updatePosition);
        };
    }, [isVisible, handleClickOutside, updatePosition]);

    if (!isVisible) return null;

    return (
        <div
            ref={tooltipRef}
            className="fixed z-50 max-w-xs"
        >
            <div className="relative bg-gray-700 bg-opacity-75 text-white text-sm p-2 rounded-lg">
                <svg
                    className="absolute left-0 top-1/2 transform -translate-x-full -translate-y-1/2"
                    width="8"
                    height="16"
                    viewBox="0 0 8 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    <path
                        d="M0 8L8 0V16L0 8Z"
                        fill="rgba(55, 65, 81, 0.75)"
                    />
                </svg>
                {message}
            </div>
        </div>
    );
};

interface InfoTooltipProps {
    message: string;
}

export const InfoTooltip: React.FC<InfoTooltipProps> = ({ message }) => {
    const [showTooltip, setShowTooltip] = useState(false);
    const infoRef = useRef(null);

    return (
        <div className="relative">
            <InfoIcon
                ref={infoRef}
                className="w-4 h-4 text-gray-500 cursor-pointer"
                onClick={() => setShowTooltip(!showTooltip)}
            />
            <Tooltip
                message={message}
                isVisible={showTooltip}
                anchorRef={infoRef}
                onClose={() => setShowTooltip(false)}
            />
        </div>
    );
};
