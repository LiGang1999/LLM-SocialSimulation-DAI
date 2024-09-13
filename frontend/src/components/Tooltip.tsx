import React, { useState, useEffect, RefObject, useCallback } from 'react';

interface TooltipProps {
    message: string;
    isVisible: boolean;
    anchorRef: RefObject<HTMLElement>;
    onClose?: () => void;  // Make onClose optional
}

export const Tooltip: React.FC<TooltipProps> = ({ message, isVisible, anchorRef, onClose }) => {
    const [position, setPosition] = useState({ top: 0, left: 0 });

    const handleClickOutside = useCallback((event: MouseEvent) => {
        if (anchorRef.current && !anchorRef.current.contains(event.target as Node)) {
            // Check if onClose is provided before calling it
            if (onClose && typeof onClose === 'function') {
                onClose();
            } else {
                console.warn('Tooltip: onClose prop is not provided or not a function');
            }
        }
    }, [anchorRef, onClose]);

    useEffect(() => {
        if (isVisible) {
            document.addEventListener('click', handleClickOutside);
        } else {
            document.removeEventListener('click', handleClickOutside);
        }

        return () => {
            document.removeEventListener('click', handleClickOutside);
        };
    }, [isVisible, handleClickOutside]);

    useEffect(() => {
        if (anchorRef.current && isVisible) {
            const rect = anchorRef.current.getBoundingClientRect();
            setPosition({
                top: rect.top + window.scrollY + rect.height / 2,
                left: rect.right + 10,
            });
        }
    }, [isVisible, anchorRef]);

    if (!isVisible) return null;

    return (
        <div
            className="fixed z-50 max-w-xs"
            style={{
                top: `${position.top}px`,
                left: `${position.left}px`,
                transform: 'translateY(-50%)',
            }}
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