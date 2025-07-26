import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'package:flutter/foundation.dart';

enum WebSocketState {
  connecting,
  connected,
  disconnected,
  error,
}

enum MessageType {
  audio,
  text,
  control,
  connection,
  processing,
  transcription,
  response,
  audioResponse,
  error,
  callEnded,
  callPaused,
  callResumed,
}

class WebSocketMessage {
  final MessageType type;
  final String? content;
  final String? userId;
  final String? agentId;
  final String? callId;
  final String? messageId;
  final String? emotion;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  WebSocketMessage({
    required this.type,
    this.content,
    this.userId,
    this.agentId,
    this.callId,
    this.messageId,
    this.emotion,
    DateTime? timestamp,
    this.metadata,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() {
    return {
      'type': type.name,
      'content': content,
      'user_id': userId,
      'agent_id': agentId,
      'call_id': callId,
      'message_id': messageId,
      'emotion': emotion,
      'timestamp': timestamp.toIso8601String(),
      if (metadata != null) ...metadata!,
    };
  }

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: MessageType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => MessageType.text,
      ),
      content: json['content'],
      userId: json['user_id'],
      agentId: json['agent_id'],
      callId: json['call_id'],
      messageId: json['message_id'] ?? json['id'],
      emotion: json['emotion'],
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'])
          : DateTime.now(),
      metadata: json,
    );
  }
}

class VoiceWebSocketService {
  static const String _baseUrl =
      'ws://localhost:8000'; // Replace with actual URL

  WebSocketChannel? _channel;
  WebSocketState _state = WebSocketState.disconnected;

  // Stream controllers
  final _stateController = StreamController<WebSocketState>.broadcast();
  final _messageController = StreamController<WebSocketMessage>.broadcast();
  final _transcriptionController = StreamController<String>.broadcast();
  final _responseController = StreamController<String>.broadcast();
  final _audioController = StreamController<Uint8List>.broadcast();
  final _errorController = StreamController<String>.broadcast();
  final _processingController = StreamController<String>.broadcast();

  // Getters for streams
  Stream<WebSocketState> get stateStream => _stateController.stream;
  Stream<WebSocketMessage> get messageStream => _messageController.stream;
  Stream<String> get transcriptionStream => _transcriptionController.stream;
  Stream<String> get responseStream => _responseController.stream;
  Stream<Uint8List> get audioStream => _audioController.stream;
  Stream<String> get errorStream => _errorController.stream;
  Stream<String> get processingStream => _processingController.stream;

  WebSocketState get state => _state;
  bool get isConnected => _state == WebSocketState.connected;

  Timer? _heartbeatTimer;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  static const Duration _heartbeatInterval = Duration(seconds: 30);
  static const Duration _reconnectDelay = Duration(seconds: 5);

  // Message queue for when disconnected
  final List<WebSocketMessage> _messageQueue = [];

  Future<void> connect(String callId, String userId) async {
    try {
      _setState(WebSocketState.connecting);

      final uri = Uri.parse('$_baseUrl/ws/call/$callId?user_id=$userId');
      _channel = WebSocketChannel.connect(uri);

      await _channel!.ready;
      _setState(WebSocketState.connected);
      _reconnectAttempts = 0;

      // Start listening to messages
      _listen();

      // Start heartbeat
      _startHeartbeat();

      // Send queued messages
      await _sendQueuedMessages();

      debugPrint('WebSocket connected to call: $callId');
    } catch (e) {
      debugPrint('WebSocket connection error: $e');
      _setState(WebSocketState.error);
      _handleConnectionError(callId, userId);
    }
  }

  void _listen() {
    _channel?.stream.listen(
      (data) {
        try {
          final Map<String, dynamic> json = jsonDecode(data);
          final message = WebSocketMessage.fromJson(json);

          _messageController.add(message);
          _handleMessage(message);
        } catch (e) {
          debugPrint('Error parsing WebSocket message: $e');
          _errorController.add('Failed to parse message');
        }
      },
      onError: (error) {
        debugPrint('WebSocket stream error: $error');
        _setState(WebSocketState.error);
        _errorController.add(error.toString());
      },
      onDone: () {
        debugPrint('WebSocket connection closed');
        _setState(WebSocketState.disconnected);
        _handleDisconnection();
      },
    );
  }

  void _handleMessage(WebSocketMessage message) {
    switch (message.type) {
      case MessageType.connection:
        debugPrint('Connection confirmed: ${message.content}');
        break;

      case MessageType.transcription:
        if (message.content != null) {
          _transcriptionController.add(message.content!);
        }
        break;

      case MessageType.response:
        if (message.content != null) {
          _responseController.add(message.content!);
        }
        break;

      case MessageType.audioResponse:
        if (message.content != null) {
          try {
            final audioBytes = base64Decode(message.content!);
            _audioController.add(audioBytes);
          } catch (e) {
            debugPrint('Error decoding audio: $e');
          }
        }
        break;

      case MessageType.processing:
        final stage = message.metadata?['stage'] ?? 'processing';
        _processingController.add(stage);
        break;

      case MessageType.error:
        if (message.content != null) {
          _errorController.add(message.content!);
        }
        break;

      case MessageType.callEnded:
        disconnect();
        break;

      default:
        debugPrint('Unhandled message type: ${message.type}');
    }
  }

  Future<void> sendVoiceMessage(
    Uint8List audioData,
    String userId,
    String agentId,
    String callId,
  ) async {
    final base64Audio = base64Encode(audioData);
    final message = WebSocketMessage(
      type: MessageType.audio,
      content: base64Audio,
      userId: userId,
      agentId: agentId,
      callId: callId,
    );

    await _sendMessage(message);
  }

  Future<void> sendTextMessage(
    String text,
    String userId,
    String agentId,
    String callId,
  ) async {
    final message = WebSocketMessage(
      type: MessageType.text,
      content: text,
      userId: userId,
      agentId: agentId,
      callId: callId,
    );

    await _sendMessage(message);
  }

  Future<void> sendControlMessage(
    String action,
    String userId,
    String callId,
  ) async {
    final message = WebSocketMessage(
      type: MessageType.control,
      content: action,
      userId: userId,
      callId: callId,
    );

    await _sendMessage(message);
  }

  Future<void> _sendMessage(WebSocketMessage message) async {
    if (_state == WebSocketState.connected && _channel != null) {
      try {
        final jsonData = jsonEncode(message.toJson());
        _channel!.sink.add(jsonData);
      } catch (e) {
        debugPrint('Error sending message: $e');
        _errorController.add('Failed to send message');

        // Queue message for retry
        _messageQueue.add(message);
      }
    } else {
      // Queue message for when connected
      _messageQueue.add(message);
      debugPrint('Message queued (not connected): ${message.type}');
    }
  }

  Future<void> _sendQueuedMessages() async {
    if (_messageQueue.isNotEmpty) {
      final messages = List<WebSocketMessage>.from(_messageQueue);
      _messageQueue.clear();

      for (final message in messages) {
        await _sendMessage(message);
        // Small delay between messages
        await Future.delayed(const Duration(milliseconds: 100));
      }
    }
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = Timer.periodic(_heartbeatInterval, (timer) {
      if (_state == WebSocketState.connected) {
        try {
          _channel?.sink.add(jsonEncode({'type': 'ping'}));
        } catch (e) {
          debugPrint('Heartbeat failed: $e');
        }
      }
    });
  }

  void _handleConnectionError(String callId, String userId) {
    if (_reconnectAttempts < _maxReconnectAttempts) {
      _reconnectAttempts++;
      debugPrint(
          'Attempting reconnection $_reconnectAttempts/$_maxReconnectAttempts');

      _reconnectTimer?.cancel();
      _reconnectTimer = Timer(_reconnectDelay, () {
        connect(callId, userId);
      });
    } else {
      debugPrint('Max reconnection attempts reached');
      _errorController
          .add('Connection failed after $_maxReconnectAttempts attempts');
    }
  }

  void _handleDisconnection() {
    _heartbeatTimer?.cancel();

    // Try to reconnect if not manually disconnected
    if (_state != WebSocketState.disconnected) {
      _setState(WebSocketState.disconnected);
    }
  }

  void _setState(WebSocketState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(_state);
      debugPrint('WebSocket state changed to: $_state');
    }
  }

  Future<void> disconnect() async {
    debugPrint('Disconnecting WebSocket...');

    _setState(WebSocketState.disconnected);
    _heartbeatTimer?.cancel();
    _reconnectTimer?.cancel();

    try {
      await _channel?.sink.close(status.goingAway);
    } catch (e) {
      debugPrint('Error closing WebSocket: $e');
    }

    _channel = null;
    _messageQueue.clear();
  }

  void dispose() {
    disconnect();
    _stateController.close();
    _messageController.close();
    _transcriptionController.close();
    _responseController.close();
    _audioController.close();
    _errorController.close();
    _processingController.close();
  }

  // Utility methods for specific actions
  Future<void> pauseCall(String userId, String callId) async {
    await sendControlMessage('pause', userId, callId);
  }

  Future<void> resumeCall(String userId, String callId) async {
    await sendControlMessage('resume', userId, callId);
  }

  Future<void> endCall(String userId, String callId) async {
    await sendControlMessage('end_call', userId, callId);
  }
}
