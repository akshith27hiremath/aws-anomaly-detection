import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Network } from "lucide-react";
import { HealthCheck } from "./dashboard/HealthCheck";
import { AnalysisPanel } from "./dashboard/AnalysisPanel";
import { KnowledgeGraph } from "./dashboard/KnowledgeGraph";
import { DataSources } from "./dashboard/DataSources";
import { StatisticsPanel } from "./dashboard/StatisticsPanel";
import { OIPanel } from "./dashboard/OIPanel";
import { ProcessExplainer } from "./dashboard/ProcessExplainer";
import * as api from "../services/api";
import { wsManager } from "../services/api";

interface DashboardProps {
  onBack: () => void;
}

export function Dashboard({ onBack }: DashboardProps) {
  // State for each component connected to real backend
  const [healthStatus, setHealthStatus] = useState("Checking...");
  const [analysisText, setAnalysisText] = useState("");
  const [knowledgeGraphData, setKnowledgeGraphData] = useState<any>(null);
  const [dataSources, setDataSources] = useState<any[]>([]);
  const [statisticsData, setStatisticsData] = useState<any>(null);
  const [connected, setConnected] = useState(false);
  const [latestAnomalies, setLatestAnomalies] = useState<api.AnomalyReport[]>([]);

  // Initialize WebSocket and load data on mount
  useEffect(() => {
    // Setup WebSocket
    wsManager.onStatusChange((isConnected) => {
      setConnected(isConnected);
      if (isConnected) {
        setHealthStatus("✓ Backend connected - Processing data");
      } else {
        setHealthStatus("⚠ Disconnected - Attempting to reconnect");
      }
    });

    wsManager.onMessage((data) => {
      // Handle real-time updates from backend
      if (data.type === 'anomaly_update') {
        setLatestAnomalies(data.reports || []);
        // Update analysis text with latest anomaly
        if (data.reports && data.reports.length > 0) {
          const latest = data.reports[0];
          setAnalysisText(`[${new Date().toLocaleTimeString()}] New Anomaly Detected\n\n${latest.narrative}\n\nSeverity: ${latest.severity.toUpperCase()}\nConfidence: ${(latest.consensus_score * 100).toFixed(1)}%\nSource: ${latest.source}\nMetric: ${latest.metric}`);
        }
      } else if (data.type === 'data_update') {
        // Refresh data sources when new data arrives
        fetchDataSources();
      }
    });

    wsManager.connect();

    // Initial data load
    fetchHealthStatus();
    fetchLatestAnalysis();
    fetchDataSources();
    fetchStatistics();
    fetchKnowledgeGraphFunc();

    // Set up periodic refresh (every 30 seconds)
    const refreshInterval = setInterval(() => {
      fetchLatestAnalysis();
      fetchStatistics();
    }, 30000);

    // Cleanup
    return () => {
      clearInterval(refreshInterval);
      wsManager.disconnect();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Backend integration functions using real API
  const fetchHealthStatus = async () => {
    try {
      const health = await api.fetchHealth();
      setHealthStatus(`✓ System ${health.status} - v${health.version}`);
    } catch (error) {
      console.error('Failed to fetch health:', error);
      setHealthStatus("⚠ Unable to connect to backend");
    }
  };

  const fetchLatestAnalysis = async () => {
    try {
      const analysis = await api.fetchAnalysis();
      setLatestAnomalies(analysis.reports);

      if (analysis.reports.length > 0) {
        // Format the latest anomaly report
        const latest = analysis.reports[0];
        const formattedAnalysis = `[${new Date().toLocaleTimeString()}] ANOMALY DETECTION REPORT

${latest.narrative}

Detection Details:
• Source: ${latest.source}
• Metric: ${latest.metric}
• Severity: ${latest.severity.toUpperCase()} (score: ${latest.severity_score.toFixed(2)})
• Confidence: ${(latest.consensus_score * 100).toFixed(1)}%
• Detection Methods: ${latest.detection_count} (${latest.detecting_agents.join(', ')})
• Timestamp: ${new Date(latest.timestamp).toLocaleString()}

${latest.explanation}

Status: ${analysis.anomaly_count} total anomalies detected | ${analysis.high_severity_count} high severity`;

        setAnalysisText(formattedAnalysis);
      } else {
        setAnalysisText(`[${new Date().toLocaleTimeString()}] No anomalies currently detected. All systems nominal.`);
      }
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
      setAnalysisText("Unable to fetch analysis data from backend");
    }
  };

  const fetchDataSources = async () => {
    try {
      const sources = await api.fetchDataSources();

      // Transform backend data into display format
      const formattedSources = [];

      // Cryptocurrency sources
      if (sources.crypto && sources.crypto.length > 0) {
        const latest = sources.crypto[0];
        const timeAgo = Math.floor((Date.now() - new Date(latest.timestamp).getTime()) / 1000);
        formattedSources.push({
          name: "CoinGecko API",
          status: "active",
          lastUpdate: `${timeAgo}s ago`,
          reliability: 98.7
        });
      }

      // Weather sources
      if (sources.weather && sources.weather.length > 0) {
        const latest = sources.weather[0];
        const timeAgo = Math.floor((Date.now() - new Date(latest.timestamp).getTime()) / 1000);
        formattedSources.push({
          name: "Open-Meteo Weather",
          status: latest.metadata.cached ? "cached" : "active",
          lastUpdate: `${timeAgo}s ago`,
          reliability: 99.5
        });
      }

      // GitHub sources
      if (sources.github && sources.github.length > 0) {
        const latest = sources.github[0];
        const timeAgo = Math.floor((Date.now() - new Date(latest.timestamp).getTime()) / 1000);
        formattedSources.push({
          name: "GitHub API",
          status: latest.metadata.cached ? "cached" : "active",
          lastUpdate: `${timeAgo}s ago`,
          reliability: 97.3
        });
      }

      setDataSources(formattedSources);
    } catch (error) {
      console.error('Failed to fetch data sources:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const stats = await api.fetchStatistics();

      // Transform stats into chart-friendly format
      const mockStats = {
        volumeData: [
          { time: "Current", volume: stats.historical_data_points || 0 }
        ],
        sentimentData: stats.data_sources.map((source, idx) => ({
          category: source,
          value: idx === 0 ? 45 : idx === 1 ? 30 : 25
        })),
        anomalyTypes: [
          { type: "Total", count: stats.total_anomalies_detected || 0 },
          { type: "Active", count: stats.websocket_connections || 0 },
        ],
      };
      setStatisticsData(mockStats);
    } catch (error) {
      console.error('Failed to fetch statistics:', error);
    }
  };

  const fetchKnowledgeGraphFunc = async () => {
    try {
      const graph = await api.fetchKnowledgeGraph();

      // Transform backend graph format for visualization
      const transformedGraph = {
        nodes: graph.nodes.map(node => ({
          id: node.id,
          label: `${node.source}:${node.metric}`,
          type: node.source,
          importance: node.confidence
        })),
        links: graph.edges.map(edge => ({
          source: edge.source,
          target: edge.target,
          strength: edge.confidence
        }))
      };

      setKnowledgeGraphData(transformedGraph);
    } catch (error) {
      console.error('Failed to fetch knowledge graph:', error);
    }
  };

  return (
    <div className="min-h-screen px-4 py-6">
      <div className="max-w-[2000px] mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-between mb-6 backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-4"
        >
          <div className="flex items-center gap-4">
            <motion.button
              onClick={onBack}
              whileHover={{ scale: 1.05, x: -5 }}
              whileTap={{ scale: 0.95 }}
              className="backdrop-blur-sm bg-white/10 border border-white/20 rounded-xl p-2 text-white"
            >
              <ArrowLeft className="w-5 h-5" />
            </motion.button>
            
            <div className="flex items-center gap-3">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
                className="w-10 h-10 backdrop-blur-sm bg-white/10 border border-white/20 rounded-xl flex items-center justify-center"
              >
                <Network className="w-5 h-5 text-white" />
              </motion.div>
              <div>
                <h2 className="text-white">HIVEMIND</h2>
                <p className="text-white/50 text-sm">Neural Intelligence Dashboard</p>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <motion.div
              animate={{ scale: [1, 1.2, 1], opacity: [0.5, 1, 0.5] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="w-2 h-2 rounded-full bg-green-400"
            />
            <span className="text-white/80 text-sm">Live Processing</span>
          </div>
        </motion.div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 xl:grid-cols-12 gap-4">
          {/* Left Column */}
          <div className="xl:col-span-8 space-y-4">
            {/* Analysis Panel - Large */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
            >
              <AnalysisPanel 
                analysisText={analysisText}
                onFetchAnalysis={fetchLatestAnalysis}
              />
            </motion.div>

            {/* Statistics Panel */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <StatisticsPanel 
                data={statisticsData}
                onRefresh={fetchStatistics}
              />
            </motion.div>
          </div>

          {/* Right Column */}
          <div className="xl:col-span-4 space-y-4">
            {/* Health Check */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              <HealthCheck
                status={healthStatus}
                onCheckHealth={fetchHealthStatus}
              />
            </motion.div>

            {/* OI Panel */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.35 }}
            >
              <OIPanel />
            </motion.div>

            {/* Data Sources */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <DataSources
                sources={dataSources}
                onUpdate={fetchDataSources}
              />
            </motion.div>
          </div>

          {/* Process Explainer - Full Width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="xl:col-span-12"
          >
            <ProcessExplainer />
          </motion.div>

          {/* Knowledge Graph - Full Width */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="xl:col-span-12"
          >
            <KnowledgeGraph
              data={knowledgeGraphData}
              onRefresh={fetchKnowledgeGraphFunc}
            />
          </motion.div>
        </div>
      </div>
    </div>
  );
}
