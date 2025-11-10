import { motion } from "framer-motion";
import { Network, RefreshCw } from "lucide-react";
import { useState, useEffect } from "react";

interface Node {
  id: string;
  label: string;
  type: string;
  importance: number;
}

interface Link {
  source: string;
  target: string;
  strength: number;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

interface KnowledgeGraphProps {
  data: GraphData | null;
  onRefresh: () => void;
}

export function KnowledgeGraph({ data, onRefresh }: KnowledgeGraphProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [nodePositions, setNodePositions] = useState<Map<string, { x: number; y: number }>>(new Map());

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await onRefresh();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  // Calculate positions for nodes (simple circular layout)
  useEffect(() => {
    if (!data) return;

    const positions = new Map();
    const centerX = 400;
    const centerY = 250;
    const radius = 150;

    data.nodes.forEach((node, index) => {
      const angle = (index / data.nodes.length) * 2 * Math.PI;
      // Vary radius based on importance
      const r = radius * (0.7 + node.importance * 0.3);
      positions.set(node.id, {
        x: centerX + r * Math.cos(angle),
        y: centerY + r * Math.sin(angle),
      });
    });

    setNodePositions(positions);
  }, [data]);

  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      asset: "rgba(255, 255, 255, 0.9)",
      entity: "rgba(255, 255, 255, 0.7)",
      exchange: "rgba(200, 200, 200, 0.8)",
      event: "rgba(180, 180, 180, 0.8)",
      source: "rgba(160, 160, 160, 0.8)",
      pattern: "rgba(140, 140, 140, 0.8)",
    };
    return colors[type] || "rgba(255, 255, 255, 0.6)";
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Network className="w-5 h-5 text-white" />
          <div>
            <h3 className="text-white">Knowledge Graph</h3>
            <p className="text-white/50 text-xs">Entity Relationships & Connections</p>
          </div>
        </div>
        
        <motion.button
          onClick={handleRefresh}
          disabled={isRefreshing}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 rounded-lg backdrop-blur-sm bg-white/10 border border-white/20 text-white text-sm flex items-center gap-2 transition-all hover:bg-white/15"
        >
          <motion.div
            animate={isRefreshing ? { rotate: 360 } : {}}
            transition={{ duration: 0.5, ease: "linear" }}
          >
            <RefreshCw className="w-4 h-4" />
          </motion.div>
          Refresh
        </motion.button>
      </div>

      {/* Graph Visualization */}
      <div className="backdrop-blur-sm bg-black/20 border border-white/10 rounded-xl p-4 overflow-hidden">
        {data ? (
          <div className="relative w-full h-[500px]">
            <svg className="w-full h-full" viewBox="0 0 800 500">
              {/* Draw connections first (so they're behind nodes) */}
              {data.links.map((link, index) => {
                const sourcePos = nodePositions.get(link.source);
                const targetPos = nodePositions.get(link.target);
                if (!sourcePos || !targetPos) return null;

                return (
                  <motion.line
                    key={`link-${index}`}
                    x1={sourcePos.x}
                    y1={sourcePos.y}
                    x2={targetPos.x}
                    y2={targetPos.y}
                    stroke="rgba(255, 255, 255, 0.2)"
                    strokeWidth={link.strength * 2}
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={{ 
                      pathLength: 1, 
                      opacity: [0.2, 0.4, 0.2],
                    }}
                    transition={{ 
                      pathLength: { duration: 1, delay: index * 0.05 },
                      opacity: { duration: 3, repeat: Infinity, delay: index * 0.2 }
                    }}
                  />
                );
              })}

              {/* Draw nodes */}
              {data.nodes.map((node, index) => {
                const pos = nodePositions.get(node.id);
                if (!pos) return null;

                const radius = 20 + node.importance * 20;

                return (
                  <g key={`node-${node.id}`}>
                    {/* Node glow */}
                    <motion.circle
                      cx={pos.x}
                      cy={pos.y}
                      r={radius + 10}
                      fill={getNodeColor(node.type)}
                      opacity={0.2}
                      initial={{ scale: 0 }}
                      animate={{ 
                        scale: [1, 1.2, 1],
                        opacity: [0.1, 0.3, 0.1]
                      }}
                      transition={{ 
                        scale: { duration: 0.5, delay: index * 0.1 },
                        opacity: { duration: 2, repeat: Infinity, delay: index * 0.3 }
                      }}
                    />
                    
                    {/* Node circle */}
                    <motion.circle
                      cx={pos.x}
                      cy={pos.y}
                      r={radius}
                      fill={getNodeColor(node.type)}
                      stroke="rgba(255, 255, 255, 0.5)"
                      strokeWidth="2"
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.5, delay: index * 0.1 }}
                      whileHover={{ scale: 1.2 }}
                      style={{ cursor: "pointer" }}
                    />

                    {/* Node label */}
                    <motion.text
                      x={pos.x}
                      y={pos.y + radius + 20}
                      textAnchor="middle"
                      fill="white"
                      fontSize="12"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 0.8 }}
                      transition={{ delay: index * 0.1 + 0.3 }}
                    >
                      {node.label}
                    </motion.text>
                  </g>
                );
              })}
            </svg>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-[500px] text-white/40">
            <Network className="w-12 h-12 mb-3 opacity-50" />
            <p>No graph data available</p>
            <p className="text-xs mt-2">Click "Refresh" to load entity relationships</p>
          </div>
        )}
      </div>

      {/* Legend */}
      {data && (
        <div className="mt-4 flex flex-wrap gap-3">
          {Array.from(new Set(data.nodes.map(n => n.type))).map((type) => (
            <div key={type} className="flex items-center gap-2 backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg px-3 py-1.5">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getNodeColor(type) }}
              />
              <span className="text-white/70 text-xs capitalize">{type}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
