import { useEffect, useRef, useState } from 'react';
import { AutoResizeTextarea } from './autoResizeTextArea';
import { apis } from "@/lib/api"

interface FlowchartCanvasProps {
    workflow: Record<string, apis.Stage>;
    onUpdate: (workflow: Record<string, apis.Stage>) => void;
}

export const FlowchartCanvas = ({
    workflow,
    onUpdate,
}: FlowchartCanvasProps) => {
    // Refs for flowchart canvas
    const canvasRef = useRef<HTMLDivElement>(null);
    const planBlockRef = useRef<HTMLDivElement>(null);
    const executeBlockRef = useRef<HTMLDivElement>(null);

    // Initial positions for blocks
    const [planPosition, setPlanPosition] = useState({ x: 50, y: 50 });
    const [executePosition, setExecutePosition] = useState({ x: 350, y: 50 });

    // State to track viewport position
    const [viewportOffset, setViewportOffset] = useState({ x: 0, y: 0 });

    // State to track which block is being dragged
    const [isDragging, setIsDragging] = useState(false);
    const [activeDragElement, setActiveDragElement] = useState<'plan' | 'execute' | 'background' | null>(null);
    const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

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

    // Handle background mouse down for viewport panning
    const handleBackgroundMouseDown = (e: React.MouseEvent) => {
        // Only handle background clicks (not on blocks)
        if (e.target === canvasRef.current) {
            e.preventDefault();
            setDragStart({ x: e.clientX, y: e.clientY });
            setActiveDragElement('background');
            setIsDragging(true);
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        e.preventDefault();

        if (isDragging && activeDragElement && canvasRef.current && activeDragElement !== 'background') {
            // Handle only block dragging in the local handler
            // Background panning is handled in the global handler to avoid double movement
            const canvasRect = canvasRef.current.getBoundingClientRect();

            // Calculate new position relative to the canvas
            // We need to subtract viewport offset because the visual position includes this transform
            const newX = e.clientX - canvasRect.left - dragOffset.x - viewportOffset.x;
            const newY = e.clientY - canvasRect.top - dragOffset.y - viewportOffset.y;

            // Update the position of the active element
            if (activeDragElement === 'plan') {
                setPlanPosition({ x: newX, y: newY });
            } else {
                setExecutePosition({ x: newX, y: newY });
            }
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
        setActiveDragElement(null);
    };

    // 重置函数 - 将视图和卡片恢复到初始位置
    const handleReset = () => {
        setPlanPosition({ x: 50, y: 50 });
        setExecutePosition({ x: 350, y: 50 });
        setViewportOffset({ x: 0, y: 0 });
    };

    // Add and remove mousemove and mouseup listeners
    useEffect(() => {
        const handleGlobalMouseMove = (e: MouseEvent) => {
            if (isDragging && activeDragElement && canvasRef.current) {
                if (activeDragElement === 'background') {
                    // Handle viewport panning
                    const deltaX = e.clientX - dragStart.x;
                    const deltaY = e.clientY - dragStart.y;
                    setViewportOffset(prev => ({
                        x: prev.x + deltaX,
                        y: prev.y + deltaY
                    }));
                    setDragStart({ x: e.clientX, y: e.clientY });
                } else {
                    // Handle block dragging
                    const canvasRect = canvasRef.current.getBoundingClientRect();

                    // Calculate new position relative to the canvas
                    // We need to subtract viewport offset because the visual position includes this transform
                    const newX = e.clientX - canvasRect.left - dragOffset.x - viewportOffset.x;
                    const newY = e.clientY - canvasRect.top - dragOffset.y - viewportOffset.y;

                    // Update the position of the active element
                    if (activeDragElement === 'plan') {
                        setPlanPosition({ x: newX, y: newY });
                    } else {
                        setExecutePosition({ x: newX, y: newY });
                    }
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
    }, [isDragging, activeDragElement, dragOffset, dragStart]);

    return (
        <div
            ref={canvasRef}
            className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm relative grow-1 flex-1 overflow-hidden"
            onMouseDown={handleBackgroundMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            style={
                {
                    backgroundImage: "radial-gradient(circle at 1px 1px, grey 1px, transparent 0)",
                    backgroundSize: "30px 30px",
                    backgroundPosition: `${10 + viewportOffset.x % 30}px ${10 + viewportOffset.y % 30}px`,
                    cursor: isDragging && activeDragElement === 'background' ? 'grabbing' : 'grab'
                }
            }
        >
            {/* 重置按钮 - 固定在右下角 */}
            <button
                className="absolute bottom-4 right-4 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-md shadow-sm z-20 w-8 h-8 flex items-center justify-center"
                onClick={handleReset}
                title="重置视图和卡片位置"
                style={{ pointerEvents: 'auto' }}
            >
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8" />
                    <path d="M3 3v5h5" />
                </svg>
            </button>
            <div
                className="absolute inset-0"
                style={{
                    transform: `translate(${viewportOffset.x}px, ${viewportOffset.y}px)`,
                    pointerEvents: 'none' // This ensures mouse events pass through to the background
                }}
            >
                {/* 计划 Block */}
                <div
                    ref={planBlockRef}
                    className="absolute border-2 border-blue-500 rounded-md p-3 w-[35%] bg-blue-50 cursor-move"
                    style={{
                        left: `${planPosition.x}px`,
                        top: `${planPosition.y}px`,
                        zIndex: 10,
                        userSelect: 'none',
                        pointerEvents: 'auto' // Re-enable pointer events for this element
                    }}
                    onMouseDown={(e) => handleMouseDown(e, 'plan')}
                >
                    <div className="text-center font-medium text-blue-700 mb-2">计划</div>
                    <AutoResizeTextarea
                        placeholder="输入计划内容..."
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['plan'].task}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['plan'].task = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                    <AutoResizeTextarea
                        placeholder="计划推理格式"
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['plan'].output_format['reasoning']}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['plan'].output_format['reasoning'] = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                    <AutoResizeTextarea
                        placeholder="计划结果格式..."
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['plan'].output_format['decision']}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['plan'].output_format['decision'] = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                </div>

                {/* Draw arrow between blocks */}
                <svg
                    className="absolute inset-0 w-[1000px] h-[1000px]"
                    style={{
                        zIndex: 1,
                        pointerEvents: 'none',
                        // width: '5000px',
                        // height: '5000px',
                        left: '-500px',
                        top: '-500px'
                    }}
                >
                    <line
                        x1={planPosition.x + (planBlockRef.current?.offsetWidth || 200) + 500}
                        y1={planPosition.y + ((planBlockRef.current?.offsetHeight || 100) / 2) + 500}
                        x2={executePosition.x + 500}
                        y2={executePosition.y + ((executeBlockRef.current?.offsetHeight || 100) / 2) + 500}
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
                    className="absolute border-2 border-green-500 rounded-md p-3 w-[35%] bg-green-50 cursor-move"
                    style={{
                        left: `${executePosition.x}px`,
                        top: `${executePosition.y}px`,
                        zIndex: 10,
                        userSelect: 'none',
                        pointerEvents: 'auto' // Re-enable pointer events for this element
                    }}
                    onMouseDown={(e) => handleMouseDown(e, 'execute')}
                >
                    <div className="text-center font-medium text-green-700 mb-2">执行</div>
                    <AutoResizeTextarea
                        placeholder="输入执行内容..."
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['execute'].task}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['execute'].task = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                    <AutoResizeTextarea
                        placeholder="执行推理格式"
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['execute'].output_format['reasoning']}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['execute'].output_format['reasoning'] = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                    <AutoResizeTextarea
                        placeholder="执行结果格式..."
                        className="w-full border-gray-300 focus:border-blue-500 text-xs"
                        rows={3}
                        value={workflow['execute'].output_format['execution']}
                        onChange={(e) => {
                            const newWorkflow = workflow;
                            newWorkflow['execute'].output_format['execution'] = e.target.value;
                            onUpdate(newWorkflow);
                        }}
                        onMouseDown={(e) => e.stopPropagation()}
                    />
                </div>
            </div>
        </div>
    );
};
