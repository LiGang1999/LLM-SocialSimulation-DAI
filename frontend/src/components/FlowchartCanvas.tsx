import { useEffect, useRef, useState } from 'react';
import { AutoResizeTextarea } from './autoResizeTextArea';

interface FlowchartCanvasProps {
    planText: string;
    setPlanText: (text: string) => void;
    executeText: string;
    setExecuteText: (text: string) => void;
}

export const FlowchartCanvas = ({
    planText,
    setPlanText,
    executeText,
    setExecuteText
}: FlowchartCanvasProps) => {
    // Refs for flowchart canvas
    const canvasRef = useRef<HTMLDivElement>(null);
    const planBlockRef = useRef<HTMLDivElement>(null);
    const executeBlockRef = useRef<HTMLDivElement>(null);

    // Initial positions for blocks
    const [planPosition, setPlanPosition] = useState({ x: 100, y: 50 });
    const [executePosition, setExecutePosition] = useState({ x: 100, y: 250 });

    // State to track which block is being dragged
    const [isDragging, setIsDragging] = useState(false);
    const [activeDragElement, setActiveDragElement] = useState<'plan' | 'execute' | null>(null);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });

    // Mouse event handlers for canvas dragging
    const handleMouseDown = (e: React.MouseEvent, element: 'plan' | 'execute') => {
        e.preventDefault();

        // Calculate drag offset based on which element we're dragging
        const rect = element === 'plan'
            ? planBlockRef.current?.getBoundingClientRect()
            : executeBlockRef.current?.getBoundingClientRect();

        if (rect) {
            // Calculate offset from the mouse to the top-left corner of the element
            const offsetX = e.clientX - rect.left;
            const offsetY = e.clientY - rect.top;

            setDragOffset({ x: offsetX, y: offsetY });
            setActiveDragElement(element);
            setIsDragging(true);
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        e.preventDefault();

        if (isDragging && activeDragElement && canvasRef.current) {
            const canvasRect = canvasRef.current.getBoundingClientRect();

            // Calculate new position relative to the canvas
            const newX = e.clientX - canvasRect.left - dragOffset.x;
            const newY = e.clientY - canvasRect.top - dragOffset.y;

            // Ensure the element stays within the canvas boundaries
            const elementWidth = activeDragElement === 'plan'
                ? planBlockRef.current?.offsetWidth || 0
                : executeBlockRef.current?.offsetWidth || 0;

            const elementHeight = activeDragElement === 'plan'
                ? planBlockRef.current?.offsetHeight || 0
                : executeBlockRef.current?.offsetHeight || 0;

            const boundedX = Math.max(0, Math.min(newX, canvasRect.width - elementWidth));
            const boundedY = Math.max(0, Math.min(newY, canvasRect.height - elementHeight));

            // Update the position of the active element
            if (activeDragElement === 'plan') {
                setPlanPosition({ x: boundedX, y: boundedY });
            } else {
                setExecutePosition({ x: boundedX, y: boundedY });
            }
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setActiveDragElement(null);
    };

    // Add and remove mousemove and mouseup listeners
    useEffect(() => {
        const handleGlobalMouseMove = (e: MouseEvent) => {
            if (isDragging && activeDragElement && canvasRef.current) {
                const canvasRect = canvasRef.current.getBoundingClientRect();

                // Calculate new position relative to the canvas
                const newX = e.clientX - canvasRect.left - dragOffset.x;
                const newY = e.clientY - canvasRect.top - dragOffset.y;

                // Ensure the element stays within the canvas boundaries
                const elementWidth = activeDragElement === 'plan'
                    ? planBlockRef.current?.offsetWidth || 0
                    : executeBlockRef.current?.offsetWidth || 0;

                const elementHeight = activeDragElement === 'plan'
                    ? planBlockRef.current?.offsetHeight || 0
                    : executeBlockRef.current?.offsetHeight || 0;

                const boundedX = Math.max(0, Math.min(newX, canvasRect.width - elementWidth));
                const boundedY = Math.max(0, Math.min(newY, canvasRect.height - elementHeight));

                // Update the position of the active element
                if (activeDragElement === 'plan') {
                    setPlanPosition({ x: boundedX, y: boundedY });
                } else {
                    setExecutePosition({ x: boundedX, y: boundedY });
                }
            }
        };

        const handleGlobalMouseUp = () => {
            setIsDragging(false);
            setActiveDragElement(null);
        };

        // Add global event listeners when dragging
        if (isDragging) {
            document.addEventListener('mousemove', handleGlobalMouseMove);
            document.addEventListener('mouseup', handleGlobalMouseUp);
        }

        // Cleanup
        return () => {
            document.removeEventListener('mousemove', handleGlobalMouseMove);
            document.removeEventListener('mouseup', handleGlobalMouseUp);
        };
    }, [isDragging, activeDragElement, dragOffset]);

    return (
        <div
            ref={canvasRef}
            className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm relative mb-6"
            style={{ height: "calc(100vh - 450px)", minHeight: "300px", overflow: "hidden" }}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
        >
            {/* 计划 Block */}
            <div
                ref={planBlockRef}
                className="absolute border-2 border-blue-500 rounded-md p-3 w-[45%] bg-blue-50 cursor-move"
                style={{
                    left: `${planPosition.x}px`,
                    top: `${planPosition.y}px`,
                    zIndex: 10,
                    userSelect: 'none'
                }}
                onMouseDown={(e) => handleMouseDown(e, 'plan')}
            >
                <div className="text-center font-medium text-blue-700 mb-2">计划</div>
                <AutoResizeTextarea
                    placeholder="输入计划内容..."
                    className="w-full border-gray-300 focus:border-blue-500"
                    rows={3}
                    value={planText}
                    onChange={(e) => setPlanText(e.target.value)}
                    onMouseDown={(e) => e.stopPropagation()}
                />
            </div>

            {/* Draw arrow between blocks */}
            <svg
                className="absolute inset-0 w-full h-full"
                style={{ zIndex: 1, pointerEvents: 'none' }}
            >
                <line
                    x1={planPosition.x + (planBlockRef.current?.offsetWidth || 200) / 2}
                    y1={planPosition.y + ((planBlockRef.current?.offsetHeight || 100))}
                    x2={executePosition.x + ((executeBlockRef.current?.offsetWidth || 100) / 2)}
                    y2={executePosition.y}
                    stroke="#4F46E5"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                />
                <defs>
                    <marker
                        id="arrowhead"
                        markerWidth="10"
                        markerHeight="7"
                        refX="9"
                        refY="3.5"
                        orient="auto"
                    >
                        <polygon points="0 0, 10 3.5, 0 7" fill="#4F46E5" />
                    </marker>
                </defs>
            </svg>

            {/* 执行 Block */}
            <div
                ref={executeBlockRef}
                className="absolute border-2 border-green-500 rounded-md p-3 w-[45%] bg-green-50 cursor-move"
                style={{
                    left: `${executePosition.x}px`,
                    top: `${executePosition.y}px`,
                    zIndex: 10,
                    userSelect: 'none'
                }}
                onMouseDown={(e) => handleMouseDown(e, 'execute')}
            >
                <div className="text-center font-medium text-green-700 mb-2">执行</div>
                <AutoResizeTextarea
                    placeholder="输入执行内容..."
                    className="w-full border-gray-300 focus:border-green-500"
                    rows={3}
                    value={executeText}
                    onChange={(e) => setExecuteText(e.target.value)}
                    onMouseDown={(e) => e.stopPropagation()}
                />
            </div>
        </div>
    );
};
