import React, { useEffect, useRef, TextareaHTMLAttributes } from 'react';
import { Textarea } from './ui/textarea';

// Define the component's props, extending standard Textarea props
interface AutoResizeTextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
    value: string;
    onChange: (event: React.ChangeEvent<HTMLTextAreaElement>) => void;
}

export const AutoResizeTextarea: React.FC<AutoResizeTextareaProps> = ({ value, onChange, ...props }) => {
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            const scrollHeight = textareaRef.current.scrollHeight;
            const lineHeight = parseInt(window.getComputedStyle(textareaRef.current).lineHeight || '0');
            const minHeight = lineHeight; // Minimum height of 1 row
            textareaRef.current.style.height = `${Math.max(scrollHeight, minHeight) + 5}px`;
        }
    }, [value]);

    return (
        <Textarea
            ref={textareaRef}
            value={value}
            onChange={onChange}
            {...props}
        />
    );
};
