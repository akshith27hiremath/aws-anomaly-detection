import { motion } from "framer-motion";
import { Network, Cpu } from "lucide-react";

export function NeuralNetworkVisual() {
  const nodes = {
    input: 4,
    hidden1: 6,
    hidden2: 6,
    output: 3,
  };

  return (
    <div className="h-full backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6 flex flex-col">
      {/* Header */}
      <div className="mb-4">
        <div className="flex items-center gap-2 mb-1">
          <Network className="w-5 h-5 text-white" />
          <h3 className="text-white">Neural Network</h3>
        </div>
        <p className="text-white/50 text-sm">Live processing visualization</p>
      </div>

      {/* Network Visualization */}
      <div className="flex-1 relative flex items-center justify-center">
        <svg className="w-full h-full" viewBox="0 0 200 300">
          {/* Connections - Input to Hidden1 */}
          {[...Array(nodes.input)].map((_, i) => 
            [...Array(nodes.hidden1)].map((_, j) => (
              <motion.line
                key={`i-h1-${i}-${j}`}
                x1="30"
                y1={50 + i * 60}
                x2="80"
                y2={30 + j * 45}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ 
                  pathLength: 1, 
                  opacity: [0.1, 0.3, 0.1],
                }}
                transition={{ 
                  pathLength: { duration: 1.5, delay: (i + j) * 0.1 },
                  opacity: { duration: 2, repeat: Infinity, delay: (i + j) * 0.1 }
                }}
              />
            ))
          )}

          {/* Connections - Hidden1 to Hidden2 */}
          {[...Array(nodes.hidden1)].map((_, i) => 
            [...Array(nodes.hidden2)].map((_, j) => (
              <motion.line
                key={`h1-h2-${i}-${j}`}
                x1="80"
                y1={30 + i * 45}
                x2="120"
                y2={30 + j * 45}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.1, 0.3, 0.1] }}
                transition={{ duration: 2, repeat: Infinity, delay: 1 + (i + j) * 0.1 }}
              />
            ))
          )}

          {/* Connections - Hidden2 to Output */}
          {[...Array(nodes.hidden2)].map((_, i) => 
            [...Array(nodes.output)].map((_, j) => (
              <motion.line
                key={`h2-o-${i}-${j}`}
                x1="120"
                y1={30 + i * 45}
                x2="170"
                y2={90 + j * 60}
                stroke="rgba(255,255,255,0.1)"
                strokeWidth="1"
                initial={{ opacity: 0 }}
                animate={{ opacity: [0.1, 0.3, 0.1] }}
                transition={{ duration: 2, repeat: Infinity, delay: 2 + (i + j) * 0.1 }}
              />
            ))
          )}

          {/* Input Layer */}
          {[...Array(nodes.input)].map((_, i) => (
            <motion.circle
              key={`input-${i}`}
              cx="30"
              cy={50 + i * 60}
              r="6"
              fill="rgba(59, 130, 246, 0.6)"
              stroke="rgba(255,255,255,0.5)"
              strokeWidth="1"
              initial={{ scale: 0 }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ 
                scale: { duration: 2, repeat: Infinity, delay: i * 0.2 }
              }}
            />
          ))}

          {/* Hidden Layer 1 */}
          {[...Array(nodes.hidden1)].map((_, i) => (
            <motion.circle
              key={`hidden1-${i}`}
              cx="80"
              cy={30 + i * 45}
              r="5"
              fill="rgba(168, 85, 247, 0.6)"
              stroke="rgba(255,255,255,0.5)"
              strokeWidth="1"
              initial={{ scale: 0 }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ 
                scale: { duration: 2, repeat: Infinity, delay: 0.5 + i * 0.15 }
              }}
            />
          ))}

          {/* Hidden Layer 2 */}
          {[...Array(nodes.hidden2)].map((_, i) => (
            <motion.circle
              key={`hidden2-${i}`}
              cx="120"
              cy={30 + i * 45}
              r="5"
              fill="rgba(168, 85, 247, 0.6)"
              stroke="rgba(255,255,255,0.5)"
              strokeWidth="1"
              initial={{ scale: 0 }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ 
                scale: { duration: 2, repeat: Infinity, delay: 1 + i * 0.15 }
              }}
            />
          ))}

          {/* Output Layer */}
          {[...Array(nodes.output)].map((_, i) => (
            <motion.circle
              key={`output-${i}`}
              cx="170"
              cy={90 + i * 60}
              r="7"
              fill="rgba(34, 197, 94, 0.6)"
              stroke="rgba(255,255,255,0.5)"
              strokeWidth="1"
              initial={{ scale: 0 }}
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ 
                scale: { duration: 2, repeat: Infinity, delay: 1.5 + i * 0.2 }
              }}
            />
          ))}
        </svg>
      </div>

      {/* Stats */}
      <div className="space-y-2 mt-4">
        {[
          { label: "Processing Speed", value: "2.4ms" },
          { label: "Active Layers", value: "4" },
          { label: "Parameters", value: "1.2M" },
        ].map((stat, index) => (
          <div key={index} className="flex items-center justify-between backdrop-blur-sm bg-white/5 border border-white/10 rounded-lg p-2">
            <span className="text-white/60 text-xs">{stat.label}</span>
            <span className="text-white text-xs">{stat.value}</span>
          </div>
        ))}
      </div>

      {/* Processing indicator */}
      <motion.div
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 2, repeat: Infinity }}
        className="mt-4 flex items-center justify-center gap-2 text-white/60 text-xs"
      >
        <Cpu className="w-3 h-3" />
        <span>Processing data stream...</span>
      </motion.div>
    </div>
  );
}
