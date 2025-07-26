import 'package:flutter/foundation.dart';
import '../models/chat_models.dart';
import '../services/websocket_service.dart';
import '../services/audio_service.dart';
import 'dart:convert';

class ChatProvider with ChangeNotifier {
  final WebSocketService _webSocketService = WebSocketService();
  final AudioService _audioService = AudioService();

  List<Agent> _agents = [];
  Agent? _currentAgent;
  final List<Message> _messages = [];
  bool _isConnected = false;
  bool _isRecording = false;
  bool _isProcessing = false;
  String _error = '';

  // Getters
  List<Agent> get agents => _agents;
  Agent? get currentAgent => _currentAgent;
  List<Message> get messages => _messages;
  bool get isConnected => _isConnected;
  bool get isRecording => _isRecording;
  bool get isProcessing => _isProcessing;
  String get error => _error;

  ChatProvider() {
    _init();
  }

  // Initialize services
  Future<void> _init() async {
    // Initialize audio service
    await _audioService.initialize();

    // Listen to WebSocket connection status
    _webSocketService.connectionStream.listen((connected) {
      _isConnected = connected;
      notifyListeners();

      if (connected) {
        _requestAgents();
      }
    });

    // Listen to WebSocket messages
    _webSocketService.messageStream.listen(_handleWebSocketMessage);

    // Listen to audio data for streaming
    _audioService.audioDataStream.listen((audioData) {
      if (_isRecording && _currentAgent != null) {
        _webSocketService.sendAudioChunk(audioData, _currentAgent!.id);
      }
    });
  }

  // Connect to WebSocket
  Future<void> connect({String? token}) async {
    try {
      await _webSocketService.connect(token: token);
    } catch (e) {
      _setError('Failed to connect: $e');
    }
  }

  // Disconnect from WebSocket
  Future<void> disconnect() async {
    await _webSocketService.disconnect();
  }

  // Send text message
  void sendTextMessage(String content) {
    if (_currentAgent == null) {
      _setError('No agent selected');
      return;
    }

    // Add user message to chat
    final userMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: content,
      sender: 'user',
      timestamp: DateTime.now(),
      type: MessageType.text,
    );

    _messages.add(userMessage);
    notifyListeners();

    // Send to WebSocket
    _webSocketService.sendTextMessage(content, _currentAgent!.id);
    _setProcessing(true);
  }

  // Start voice recording
  Future<void> startVoiceRecording() async {
    if (_currentAgent == null) {
      _setError('No agent selected');
      return;
    }

    try {
      final success =
          await _audioService.startRecording(streamToWebSocket: true);
      if (success) {
        _isRecording = true;
        notifyListeners();

        // Notify server about audio stream start
        _webSocketService.startAudioStream(_currentAgent!.id);
      } else {
        _setError('Failed to start recording');
      }
    } catch (e) {
      _setError('Recording error: $e');
    }
  }

  // Stop voice recording
  Future<void> stopVoiceRecording() async {
    try {
      final recordingPath = await _audioService.stopRecording();
      _isRecording = false;
      notifyListeners();

      // Notify server about audio stream stop
      _webSocketService.stopAudioStream();

      if (recordingPath != null) {
        // Add audio message to chat
        final audioMessage = Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: '[Voice Message]',
          sender: 'user',
          timestamp: DateTime.now(),
          type: MessageType.audio,
          audioUrl: recordingPath,
        );

        _messages.add(audioMessage);
        notifyListeners();
        _setProcessing(true);
      }
    } catch (e) {
      _setError('Stop recording error: $e');
      _isRecording = false;
      notifyListeners();
    }
  }

  // Play audio message
  Future<void> playAudioMessage(String audioUrl) async {
    try {
      await _audioService.playAudio(audioUrl);
    } catch (e) {
      _setError('Audio playback error: $e');
    }
  }

  // Switch agent
  void switchAgent(String agentId) {
    final agent = _agents.firstWhere(
      (a) => a.id == agentId,
      orElse: () => _agents.first,
    );

    _currentAgent = agent;
    _webSocketService.switchAgent(agentId);
    notifyListeners();

    // Add system message about agent switch
    final systemMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      content: 'Switched to ${agent.name}',
      sender: 'system',
      timestamp: DateTime.now(),
      type: MessageType.system,
    );

    _messages.add(systemMessage);
    notifyListeners();
  }

  // Clear chat messages
  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }

  // Request available agents
  void _requestAgents() {
    _webSocketService.requestAgents();
  }

  // Handle WebSocket messages
  void _handleWebSocketMessage(Map<String, dynamic> message) {
    final type = message['type'] as String?;

    switch (type) {
      case 'agents_list':
        _handleAgentsList(message);
        break;
      case 'agent_response':
        _handleAgentResponse(message);
        break;
      case 'audio_response':
        _handleAudioResponse(message);
        break;
      case 'emotion_detected':
        _handleEmotionDetected(message);
        break;
      case 'error':
        _setError(message['message'] ?? 'Unknown error');
        break;
      case 'pong':
        // Handle ping response
        break;
      default:
        print('Unknown message type: $type');
    }
  }

  // Handle agents list
  void _handleAgentsList(Map<String, dynamic> message) {
    final agentsData = message['agents'] as List<dynamic>?;
    if (agentsData != null) {
      _agents = agentsData
          .map((data) => Agent.fromJson(data as Map<String, dynamic>))
          .toList();

      // Set first agent as current if none selected
      if (_currentAgent == null && _agents.isNotEmpty) {
        _currentAgent = _agents.first;
      }

      notifyListeners();
    }
  }

  // Handle agent response
  void _handleAgentResponse(Map<String, dynamic> message) {
    final content = message['content'] as String?;
    final agentId = message['agent_id'] as String?;

    if (content != null && agentId != null) {
      final agent = _agents.firstWhere(
        (a) => a.id == agentId,
        orElse: () => Agent(
            id: agentId,
            name: 'Unknown',
            description: '',
            personality: '',
            capabilities: []),
      );

      final agentMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        content: content,
        sender: agent.name,
        timestamp: DateTime.now(),
        type: MessageType.text,
        emotion: message['emotion'] as String?,
        metadata: message['metadata'] as Map<String, dynamic>?,
      );

      _messages.add(agentMessage);
      _setProcessing(false);
      notifyListeners();
    }
  }

  // Handle audio response
  void _handleAudioResponse(Map<String, dynamic> message) {
    final audioData = message['audio_data'] as String?;
    final agentId = message['agent_id'] as String?;

    if (audioData != null && agentId != null) {
      try {
        final audioBytes = base64Decode(audioData);

        // Play audio response
        _audioService.playAudioFromBytes(audioBytes);

        // Add audio message to chat
        final agent = _agents.firstWhere(
          (a) => a.id == agentId,
          orElse: () => Agent(
              id: agentId,
              name: 'Unknown',
              description: '',
              personality: '',
              capabilities: []),
        );

        final audioMessage = Message(
          id: DateTime.now().millisecondsSinceEpoch.toString(),
          content: message['content'] as String? ?? '[Audio Response]',
          sender: agent.name,
          timestamp: DateTime.now(),
          type: MessageType.audio,
          emotion: message['emotion'] as String?,
        );

        _messages.add(audioMessage);
        _setProcessing(false);
        notifyListeners();
      } catch (e) {
        _setError('Error playing audio response: $e');
      }
    }
  }

  // Handle emotion detection
  void _handleEmotionDetected(Map<String, dynamic> message) {
    final emotion = message['emotion'] as String?;
    final confidence = message['confidence'] as double?;

    if (emotion != null) {
      // Update last user message with detected emotion
      if (_messages.isNotEmpty && _messages.last.sender == 'user') {
        final lastMessage = _messages.removeLast();
        final updatedMessage = lastMessage.copyWith(
          emotion: emotion,
          metadata: {
            ...lastMessage.metadata ?? {},
            'emotion_confidence': confidence,
          },
        );
        _messages.add(updatedMessage);
        notifyListeners();
      }
    }
  }

  // Helper methods
  void _setProcessing(bool processing) {
    _isProcessing = processing;
    notifyListeners();
  }

  void _setError(String error) {
    _error = error;
    _isProcessing = false;
    notifyListeners();
  }

  void _clearError() {
    _error = '';
    notifyListeners();
  }

  @override
  void dispose() {
    _webSocketService.dispose();
    _audioService.dispose();
    super.dispose();
  }
}
