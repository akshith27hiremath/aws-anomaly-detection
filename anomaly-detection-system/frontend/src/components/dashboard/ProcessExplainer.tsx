import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown, ChevronUp, Brain, Database, Network, TrendingUp, GitBranch, Activity, Zap, Eye } from "lucide-react";

interface AgentInfo {
  name: string;
  icon: any;
  color: string;
  description: string;
  methods: string[];
  output: string;
}

export function ProcessExplainer() {
  const [expandedAgent, setExpandedAgent] = useState<string | null>(null);
  const [showFlow, setShowFlow] = useState(true);

  const agents: AgentInfo[] = [
    {
      name: "Statistical Agent",
      icon: TrendingUp,
      color: "from-blue-500 to-cyan-500",
      description: "Applies statistical methods to detect anomalies using mathematical models",
      methods: ["Z-Score Analysis", "IQR (Interquartile Range)", "Modified Z-Score", "Grubbs' Test"],
      output: "Identifies values that deviate significantly from statistical norms"
    },
    {
      name: "Temporal Agent",
      icon: Activity,
      color: "from-purple-500 to-pink-500",
      description: "Analyzes time-series patterns and seasonal variations",
      methods: ["Moving Average", "Exponential Smoothing", "Seasonal Decomposition", "Change Point Detection"],
      output: "Detects unexpected changes in trends and seasonal patterns"
    },
    {
      name: "Correlation Agent",
      icon: GitBranch,
      color: "from-green-500 to-emerald-500",
      description: "Finds relationships between different data sources",
      methods: ["Pearson Correlation", "Cross-Source Analysis", "Anomaly Correlation", "Relationship Mapping"],
      output: "Identifies correlated anomalies across multiple data streams"
    },
    {
      name: "Context Agent",
      icon: Eye,
      color: "from-orange-500 to-red-500",
      description: "Adds domain knowledge and contextual understanding",
      methods: ["Market Context", "Historical Comparison", "Domain Rules", "Metadata Analysis"],
      output: "Provides business context and domain-specific insights"
    },
    {
      name: "OI Agent",
      icon: Zap,
      color: "from-yellow-500 to-orange-500",
      description: "Specialized agent for Open Interest derivatives analysis",
      methods: ["Price-OI Divergence", "Funding Rate Analysis", "Long/Short Ratio", "Liquidation Cascade Detection"],
      output: "Detects futures market anomalies and potential manipulation"
    }
  ];

  const toggleAgent = (agentName: string) => {
    setExpandedAgent(expandedAgent === agentName ? null : agentName);
  };

  return (
    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 backdrop-blur-sm bg-gradient-to-br from-purple-500 to-blue-500 rounded-xl flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-white font-medium">System Architecture</h3>
            <p className="text-white/50 text-sm">Multi-Agent Anomaly Detection Pipeline</p>
          </div>
        </div>

        <motion.button
          onClick={() => setShowFlow(!showFlow)}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-4 py-2 backdrop-blur-sm bg-white/10 border border-white/20 rounded-lg text-white text-sm flex items-center gap-2"
        >
          {showFlow ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          {showFlow ? "Hide Flow" : "Show Flow"}
        </motion.button>
      </div>

      <AnimatePresence>
        {showFlow && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Process Flow */}
            <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4">
              <h4 className="text-white/80 text-sm font-medium mb-4">Detection Pipeline</h4>

              <div className="space-y-4">
                {/* Step 1: Data Collection */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 }}
                  className="flex items-center gap-4"
                >
                  <div className="w-8 h-8 backdrop-blur-sm bg-gradient-to-br from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Database className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium text-sm">1. Data Collection</div>
                    <div className="text-white/50 text-xs">Gather data from CoinGecko, Weather APIs, GitHub, and Binance Futures</div>
                  </div>
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="w-2 h-8 bg-gradient-to-b from-blue-500 to-purple-500 rounded-full"
                  />
                </motion.div>

                {/* Step 2: Parallel Agent Analysis */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 }}
                  className="flex items-center gap-4"
                >
                  <div className="w-8 h-8 backdrop-blur-sm bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Network className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium text-sm">2. Parallel Agent Analysis</div>
                    <div className="text-white/50 text-xs">5 specialized agents analyze data simultaneously using different methods</div>
                  </div>
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
                    className="w-2 h-8 bg-gradient-to-b from-purple-500 to-orange-500 rounded-full"
                  />
                </motion.div>

                {/* Step 3: Coordinator Synthesis */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="flex items-center gap-4"
                >
                  <div className="w-8 h-8 backdrop-blur-sm bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Brain className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium text-sm">3. Coordinator Synthesis</div>
                    <div className="text-white/50 text-xs">Aggregates findings, calculates consensus scores, builds knowledge graph</div>
                  </div>
                  <motion.div
                    animate={{ opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
                    className="w-2 h-8 bg-gradient-to-b from-orange-500 to-green-500 rounded-full"
                  />
                </motion.div>

                {/* Step 4: LLM Narrative Generation */}
                <motion.div
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.4 }}
                  className="flex items-center gap-4"
                >
                  <div className="w-8 h-8 backdrop-blur-sm bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Zap className="w-4 h-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-white font-medium text-sm">4. LLM Narrative Generation</div>
                    <div className="text-white/50 text-xs">Claude 3.5 Sonnet generates human-readable insights and recommendations</div>
                  </div>
                  <motion.div
                    animate={{ scale: [1, 1.3, 1], opacity: [0.5, 1, 0.5] }}
                    transition={{ duration: 2, repeat: Infinity, delay: 0.9 }}
                    className="w-3 h-3 bg-green-500 rounded-full flex-shrink-0"
                  />
                </motion.div>
              </div>
            </div>

            {/* Agent Details */}
            <div className="space-y-2">
              <h4 className="text-white/80 text-sm font-medium mb-3">Specialized Agents</h4>

              {agents.map((agent, index) => (
                <motion.div
                  key={agent.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 + index * 0.05 }}
                >
                  <motion.button
                    onClick={() => toggleAgent(agent.name)}
                    className="w-full backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-3 text-left transition-colors hover:bg-white/10"
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className={`w-8 h-8 bg-gradient-to-br ${agent.color} rounded-lg flex items-center justify-center`}>
                          <agent.icon className="w-4 h-4 text-white" />
                        </div>
                        <div>
                          <div className="text-white font-medium text-sm">{agent.name}</div>
                          <div className="text-white/50 text-xs">{agent.description}</div>
                        </div>
                      </div>
                      <motion.div
                        animate={{ rotate: expandedAgent === agent.name ? 180 : 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <ChevronDown className="w-4 h-4 text-white/50" />
                      </motion.div>
                    </div>
                  </motion.button>

                  <AnimatePresence>
                    {expandedAgent === agent.name && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.2 }}
                        className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4 mt-2"
                      >
                        <div className="space-y-3">
                          <div>
                            <div className="text-white/70 text-xs font-medium mb-2">Detection Methods:</div>
                            <div className="grid grid-cols-2 gap-2">
                              {agent.methods.map((method) => (
                                <div
                                  key={method}
                                  className="backdrop-blur-sm bg-white/10 border border-white/10 rounded-lg px-2 py-1 text-white/60 text-xs"
                                >
                                  {method}
                                </div>
                              ))}
                            </div>
                          </div>
                          <div>
                            <div className="text-white/70 text-xs font-medium mb-1">Output:</div>
                            <div className="text-white/50 text-xs">{agent.output}</div>
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              ))}
            </div>

            {/* Key Features */}
            <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-xl p-4">
              <h4 className="text-white/80 text-sm font-medium mb-3">Key Features</h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1">
                  <div className="text-white text-xs font-medium">Consensus Scoring</div>
                  <div className="text-white/50 text-xs">Weighted confidence from multiple agents</div>
                </div>
                <div className="space-y-1">
                  <div className="text-white text-xs font-medium">Knowledge Graph</div>
                  <div className="text-white/50 text-xs">Tracks anomaly relationships over time</div>
                </div>
                <div className="space-y-1">
                  <div className="text-white text-xs font-medium">Real-time Processing</div>
                  <div className="text-white/50 text-xs">WebSocket updates every 60 seconds</div>
                </div>
                <div className="space-y-1">
                  <div className="text-white text-xs font-medium">AI Narratives</div>
                  <div className="text-white/50 text-xs">Context-aware explanations via LLM</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
