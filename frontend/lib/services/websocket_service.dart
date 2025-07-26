import 'dart:convert';
import 'dart:io';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'dart:async';
import '../config/app_config.dart';
import '../models/chat_models.dart';

class WebSocketService {
  WebSocketChannel? _channel;
  final StreamController<Map<String, dynamic>> _messageController =
      StreamController<Map<String, dynamic>>.broadcast();
  final StreamController<bool> _connectionController =
      StreamController<bool>.broadcast();

  bool _isConnected = false;
  Timer? _pingTimer;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;
  static const Duration reconnectDelay = Duration(seconds: 3);

  // Streams
  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;
  Stream<bool> get connectionStream => _connectionController.stream;
  bool get isConnected => _isConnected;

  // Connect to WebSocket
  Future<void> connect({String? token}) async {
    try {
      final uri = Uri.parse('${AppConfig.websocketUrl}?token=${token ?? ''}');
      _channel = IOWebSocketChannel.connect(uri);

      // Listen to messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnection,
      );

      _isConnected = true;
      _reconnectAttempts = 0;
      _connectionController.add(true);
      _startPingTimer();

      print('WebSocket connected to: $uri');
    } catch (e) {
      print('WebSocket connection error: $e');
      _handleError(e);
    }
  }

  // Disconnect WebSocket
  Future<void> disconnect() async {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();

    if (_channel != null) {
      await _channel!.sink.close();
      _channel = null;
    }

    _isConnected = false;
    _connectionController.add(false);
    print('WebSocket disconnected');
  }

  // Send message
  void sendMessage(Map<String, dynamic> message) {
    if (_isConnected && _channel != null) {
      try {
        final jsonMessage = jsonEncode(message);
        _channel!.sink.add(jsonMessage);
        print('Sent message: $jsonMessage');
      } catch (e) {
        print('Error sending message: $e');
      }
    } else {
      print('Cannot send message: WebSocket not connected');
    }
  }

  // Send text message
  void sendTextMessage(String content, String agentId) {
    sendMessage({
      'type': 'message',
      'content': content,
      'agent_id': agentId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Send audio data
  void sendAudioChunk(List<int> audioData, String agentId) {
    sendMessage({
      'type': 'audio_chunk',
      'audio_data': base64Encode(audioData),
      'agent_id': agentId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Start audio streaming
  void startAudioStream(String agentId) {
    sendMessage({
      'type': 'start_audio',
      'agent_id': agentId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Stop audio streaming
  void stopAudioStream() {
    sendMessage({
      'type': 'stop_audio',
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Request agent list
  void requestAgents() {
    sendMessage({
      'type': 'get_agents',
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Switch agent
  void switchAgent(String agentId) {
    sendMessage({
      'type': 'switch_agent',
      'agent_id': agentId,
      'timestamp': DateTime.now().toIso8601String(),
    });
  }

  // Handle incoming messages
  void _handleMessage(dynamic data) {
    try {
      final message = jsonDecode(data) as Map<String, dynamic>;
      print('Received message: $message');
      _messageController.add(message);
    } catch (e) {
      print('Error parsing message: $e');
    }
  }

  // Handle connection errors
  void _handleError(dynamic error) {
    print('WebSocket error: $error');
    _isConnected = false;
    _connectionController.add(false);
    _attemptReconnect();
  }

  // Handle disconnection
  void _handleDisconnection() {
    print('WebSocket disconnected');
    _isConnected = false;
    _connectionController.add(false);
    _pingTimer?.cancel();
    _attemptReconnect();
  }

  // Start ping timer to keep connection alive
  void _startPingTimer() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 30), (timer) {
      if (_isConnected) {
        sendMessage({
          'type': 'ping',
          'timestamp': DateTime.now().toIso8601String(),
        });
      }
    });
  }

  // Attempt to reconnect
  void _attemptReconnect() {
    if (_reconnectAttempts >= maxReconnectAttempts) {
      print('Max reconnection attempts reached');
      return;
    }

    _reconnectAttempts++;
    print(
        'Attempting to reconnect... ($_reconnectAttempts/$maxReconnectAttempts)');

    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(reconnectDelay, () {
      connect();
    });
  }

  // Dispose resources
  void dispose() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _messageController.close();
    _connectionController.close();
    disconnect();
  }
}
