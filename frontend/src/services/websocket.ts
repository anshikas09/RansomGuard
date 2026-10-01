type WebSocketCallback = (event: any) => void;

class WebSocketService {
  private socket: WebSocket | null = null;
  private listeners: Map<string, WebSocketCallback[]> = new Map();
  private reconnectInterval: number = 5000;
  private isConnected: boolean = false;

  public connect() {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
    
    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnected = true;
        console.log('[WebSocket] Connected to RansomGuard WebSocket server');
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const eventType = data.type;
          
          if (this.listeners.has(eventType)) {
            this.listeners.get(eventType)?.forEach((cb) => cb(data.data));
          }
          if (this.listeners.has('*')) {
            this.listeners.get('*')?.forEach((cb) => cb(data));
          }
        } catch (e) {
          console.error('[WebSocket] Message parse error:', e);
        }
      };

      this.socket.onclose = () => {
        this.isConnected = false;
        console.log('[WebSocket] Disconnected. Reconnecting in 5s...');
        setTimeout(() => this.connect(), this.reconnectInterval);
      };

      this.socket.onerror = (err) => {
        console.warn('[WebSocket] Error encountered:', err);
      };
    } catch (e) {
      console.error('[WebSocket] Connection failed:', e);
    }
  }

  public subscribe(eventType: string, callback: WebSocketCallback) {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, []);
    }
    this.listeners.get(eventType)?.push(callback);
  }

  public unsubscribe(eventType: string, callback: WebSocketCallback) {
    if (this.listeners.has(eventType)) {
      const list = this.listeners.get(eventType) || [];
      this.listeners.set(
        eventType,
        list.filter((cb) => cb !== callback)
      );
    }
  }
}

export const wsService = new WebSocketService();
