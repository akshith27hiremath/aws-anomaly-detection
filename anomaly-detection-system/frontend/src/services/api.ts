/**
 * API Service for Anomaly Detection System
 * Handles all HTTP and WebSocket communications with the backend
 */

const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
}

export interface AnomalyReport {
  anomaly_id: string;
  source: string;
  metric: string;
  timestamp: string;
  value: number | null;
  consensus_score: number;
  severity: string;
  severity_score: number;
  detection_count: number;
  detecting_agents: string[];
  detection_methods: string[];
  explanation: string;
  narrative: string;
  counterfactuals: any[];
  individual_detections: any[];
  created_at: string;
}

export interface AnalysisResponse {
  status: string;
  timestamp: string;
  anomaly_count: number;
  high_severity_count: number;
  reports: AnomalyReport[];
}

export interface DataPoint {
  source: string;
  metric: string;
  value: number;
  timestamp: string;
  metadata: any;
}

export interface DataSourcesResponse {
  crypto: DataPoint[];
  weather: DataPoint[];
  github: DataPoint[];
}

export interface StatisticsResponse {
  historical_data_points: number;
  latest_analysis_time: string | null;
  total_anomalies_detected: number;
  websocket_connections: number;
  data_sources: string[];
}

export interface KnowledgeGraphNode {
  id: string;
  timestamp: string;
  source: string;
  metric: string;
  value: number | null;
  confidence: number;
  severity: string;
  methods: string[];
  metadata: any;
}

export interface KnowledgeGraphEdge {
  source: string;
  target: string;
  type: string;
  confidence: number;
  created_at: string;
  metadata: any;
}

export interface KnowledgeGraphResponse {
  nodes: KnowledgeGraphNode[];
  edges: KnowledgeGraphEdge[];
}

/**
 * Fetch health status from backend
 */
export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch latest anomaly analysis
 */
export async function fetchAnalysis(): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analysis`);
  if (!response.ok) {
    throw new Error(`Analysis fetch failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch current data from all sources
 */
export async function fetchDataSources(): Promise<DataSourcesResponse> {
  const response = await fetch(`${API_BASE_URL}/data-sources`);
  if (!response.ok) {
    throw new Error(`Data sources fetch failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch system statistics
 */
export async function fetchStatistics(): Promise<StatisticsResponse> {
  const response = await fetch(`${API_BASE_URL}/statistics`);
  if (!response.ok) {
    throw new Error(`Statistics fetch failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Fetch knowledge graph data
 */
export async function fetchKnowledgeGraph(): Promise<KnowledgeGraphResponse> {
  const response = await fetch(`${API_BASE_URL}/knowledge-graph`);
  if (!response.ok) {
    throw new Error(`Knowledge graph fetch failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * Trigger manual analysis
 */
export async function triggerAnalysis(): Promise<AnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error(`Manual analysis failed: ${response.statusText}`);
  }
  return response.json();
}

/**
 * WebSocket connection manager for real-time updates
 */
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 3000;
  private pingInterval: NodeJS.Timeout | null = null;
  private onMessageCallback: ((data: any) => void) | null = null;
  private onStatusChangeCallback: ((connected: boolean) => void) | null = null;

  /**
   * Connect to WebSocket server
   */
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected');
      return;
    }

    console.log('Connecting to WebSocket...');
    this.ws = new WebSocket(WS_URL);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.onStatusChangeCallback?.(true);

      // Start ping interval to keep connection alive
      this.startPing();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle pong responses
        if (data === 'pong') {
          return;
        }

        // Pass data to callback
        this.onMessageCallback?.(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.onStatusChangeCallback?.(false);
      this.stopPing();

      // Attempt to reconnect
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        console.log(`Reconnecting... (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        setTimeout(() => this.connect(), this.reconnectDelay);
      } else {
        console.error('Max reconnection attempts reached');
      }
    };
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    this.stopPing();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Send a message to the server
   */
  send(message: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(message);
    } else {
      console.error('WebSocket is not connected');
    }
  }

  /**
   * Start sending periodic ping messages
   */
  private startPing() {
    this.pingInterval = setInterval(() => {
      this.send('ping');
    }, 30000); // Ping every 30 seconds
  }

  /**
   * Stop sending ping messages
   */
  private stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  /**
   * Register callback for incoming messages
   */
  onMessage(callback: (data: any) => void) {
    this.onMessageCallback = callback;
  }

  /**
   * Register callback for connection status changes
   */
  onStatusChange(callback: (connected: boolean) => void) {
    this.onStatusChangeCallback = callback;
  }

  /**
   * Check if WebSocket is currently connected
   */
  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export const wsManager = new WebSocketManager();
