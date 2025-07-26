import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';

import '../models/agent.dart';
import '../models/call.dart';
import '../models/message.dart';

class ApiService {
  static const String baseUrl =
      'http://localhost:8000'; // Change for production
  late final Dio _dio;

  ApiService() {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // Add interceptors for logging and error handling
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  // Agent endpoints
  Future<List<Agent>> getAgents(String userId) async {
    try {
      final response =
          await _dio.get('/agents', queryParameters: {'user_id': userId});

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Agent.fromJson(json)).toList();
      } else {
        throw ApiException('Failed to fetch agents', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Agent> getAgent(String agentId, String userId) async {
    try {
      final response = await _dio
          .get('/agents/$agentId', queryParameters: {'user_id': userId});

      if (response.statusCode == 200) {
        return Agent.fromJson(response.data);
      } else {
        throw ApiException('Failed to fetch agent', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Call endpoints
  Future<Call> startCall(String userId, String agentId,
      {String callType = 'voice'}) async {
    try {
      final response = await _dio.post('/calls/start', data: {
        'user_id': userId,
        'agent_id': agentId,
        'call_type': callType,
      });

      if (response.statusCode == 200) {
        return Call.fromJson(response.data);
      } else {
        throw ApiException('Failed to start call', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<Message> sendMessage(String callId, String userId, String content,
      {String messageType = 'text'}) async {
    try {
      final response = await _dio.post('/calls/$callId/message', data: {
        'user_id': userId,
        'content': content,
        'message_type': messageType,
      });

      if (response.statusCode == 200) {
        return Message.fromJson(response.data);
      } else {
        throw ApiException('Failed to send message', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Voice message sending - simplified for web compatibility
  Future<Message> sendVoiceMessage(String callId, String audioPath) async {
    try {
      // For web, we'll send voice messages as text for now
      // In a real implementation, you'd handle audio upload differently
      if (kIsWeb) {
        // Web fallback - send as text message
        return await sendMessage(callId, 'user_001',
            'Voice message (web transcription not implemented)');
      }

      // Mobile implementation
      final formData = FormData.fromMap({
        'audio': await MultipartFile.fromFile(
          audioPath,
          filename: 'recording.wav',
        ),
      });

      final response = await _dio.post('/calls/$callId/voice', data: formData);

      if (response.statusCode == 200) {
        return Message.fromJson(response.data);
      } else {
        throw ApiException('Failed to send voice message', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> endCall(String callId) async {
    try {
      final response = await _dio.put('/calls/$callId/end');

      if (response.statusCode != 200) {
        throw ApiException('Failed to end call', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  // History endpoints
  Future<List<AgentHistory>> getAgentHistory(String userId) async {
    try {
      final response = await _dio.get('/history/$userId/agents');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => AgentHistory.fromJson(json)).toList();
      } else {
        throw ApiException(
            'Failed to fetch agent history', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<CallHistory>> getCallHistory(String userId, String agentId,
      {String? date}) async {
    try {
      final queryParams = <String, dynamic>{'user_id': userId};
      if (date != null) queryParams['date'] = date;

      final response = await _dio.get('/history/$userId/agents/$agentId/calls',
          queryParameters: queryParams);

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => CallHistory.fromJson(json)).toList();
      } else {
        throw ApiException('Failed to fetch call history', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<List<Message>> getCallMessages(String userId, String callId) async {
    try {
      final response =
          await _dio.get('/history/$userId/calls/$callId/messages');

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Message.fromJson(json)).toList();
      } else {
        throw ApiException(
            'Failed to fetch call messages', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteCall(String userId, String callId) async {
    try {
      final response = await _dio.delete('/history/$userId/calls/$callId');

      if (response.statusCode != 200) {
        throw ApiException('Failed to delete call', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  Future<void> deleteAgentHistory(String userId, String agentId) async {
    try {
      final response = await _dio.delete('/history/$userId/agents/$agentId');

      if (response.statusCode != 200) {
        throw ApiException(
            'Failed to delete agent history', response.statusCode);
      }
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Audio streaming
  String getAudioUrl(String callId, String audioId) {
    return '$baseUrl/calls/$callId/audio/$audioId';
  }

  // Health check
  Future<bool> checkHealth() async {
    try {
      final response = await _dio.get('/health');
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  // Error handling
  ApiException _handleError(dynamic error) {
    if (error is DioException) {
      switch (error.type) {
        case DioExceptionType.connectionTimeout:
        case DioExceptionType.sendTimeout:
        case DioExceptionType.receiveTimeout:
          return const ApiException('Connection timeout', 408);
        case DioExceptionType.badResponse:
          final statusCode = error.response?.statusCode ?? 500;
          final message = error.response?.data?['detail'] ?? 'Server error';
          return ApiException(message, statusCode);
        case DioExceptionType.cancel:
          return const ApiException('Request cancelled', 499);
        default:
          return const ApiException('Network error', 500);
      }
    }

    return ApiException('Unknown error: ${error.toString()}', 500);
  }
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  const ApiException(this.message, [this.statusCode]);

  @override
  String toString() => 'ApiException: $message (${statusCode ?? 'Unknown'})';
}
