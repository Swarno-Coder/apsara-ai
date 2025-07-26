import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/call.dart';
import '../models/message.dart';
import '../services/api_service.dart';
import '../services/stt_service.dart';
import '../services/tts_service.dart';

// Providers
final callServiceProvider = Provider<CallService>((ref) => CallService());

final activeCallProvider =
    StateNotifierProvider<ActiveCallNotifier, AsyncValue<Call?>>((ref) {
  return ActiveCallNotifier(ref.read(callServiceProvider));
});

// Call Service
class CallService {
  final ApiService _apiService = ApiService();
  final STTService _sttService = STTService();
  final TTSService _ttsService = TTSService();

  Future<Call> startCall(String userId, String agentId) async {
    try {
      // Initialize services
      await _sttService.initialize();
      await _ttsService.initialize();

      // Start call via API
      final callData = await _apiService.startCall(userId, agentId);
      return callData;
    } catch (e) {
      throw Exception('Failed to start call: $e');
    }
  }

  Future<Message> sendTextMessage(
      String callId, String userId, String content) async {
    print('CallService.sendTextMessage called');
    print('callId: $callId, userId: $userId, content: $content');

    try {
      final message = await _apiService.sendMessage(callId, userId, content);
      print('API response received: ${message.content}');
      return message;
    } catch (e) {
      print('Error in CallService.sendTextMessage: $e');
      throw Exception('Failed to send message: $e');
    }
  }

  Future<Message> sendVoiceMessage(String callId, String userId) async {
    try {
      // Start recording
      await _sttService.startRecording();

      // Note: In a real app, you'd wait for user to stop recording
      // This is just for the structure
      await Future.delayed(const Duration(seconds: 2));

      // Stop recording and get audio file
      final audioPath = await _sttService.stopRecording();

      // Transcribe audio
      final transcription = await _sttService.transcribeAudio(audioPath);

      // Send transcribed text as message
      final message =
          await _apiService.sendMessage(callId, userId, transcription);
      return message;
    } catch (e) {
      throw Exception('Failed to send voice message: $e');
    }
  }

  Future<void> playResponse(String text) async {
    try {
      await _ttsService.speak(text);
    } catch (e) {
      print('TTS Error: $e');
    }
  }

  Future<void> startRecording() async {
    await _sttService.startRecording();
  }

  Future<String?> stopRecording() async {
    return await _sttService.stopRecording();
  }

  Future<String> transcribeAudio(String? audioPath) async {
    return await _sttService.transcribeAudio(audioPath);
  }

  Future<void> endCall() async {
    try {
      await _sttService.cancelRecording();
      await _ttsService.stop();
    } catch (e) {
      print('Error ending call: $e');
    }
  }

  bool get isRecording => _sttService.isRecording;
  bool get isSpeaking => _ttsService.isPlaying;
}

// Active Call State Notifier
class ActiveCallNotifier extends StateNotifier<AsyncValue<Call?>> {
  final CallService _callService;
  Call? _currentCall;

  ActiveCallNotifier(this._callService) : super(const AsyncValue.data(null));

  Future<void> startCall(String userId, String agentId) async {
    print('ActiveCallNotifier.startCall called');
    state = const AsyncValue.loading();

    try {
      final call = await _callService.startCall(userId, agentId);
      print('Call started successfully: ${call.id}');
      _currentCall = call;
      print('Current call set: ${_currentCall?.id}');
      state = AsyncValue.data(call);
      print('State updated with call data');
    } catch (error, stackTrace) {
      print('Error starting call: $error');
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<Message?> sendTextMessage(String content) async {
    if (_currentCall == null) {
      print('ERROR: No current call when sending message');
      return null;
    }

    print('Sending text message: $content');
    print('Call ID: ${_currentCall!.id}');
    print('User ID: ${_currentCall!.userId}');

    try {
      final message = await _callService.sendTextMessage(
        _currentCall!.id,
        _currentCall!.userId,
        content,
      );

      print('Message sent successfully: ${message.content}');

      // Play TTS response if it's from agent
      if (message.isFromAgent) {
        await _callService.playResponse(message.content);
      }

      return message;
    } catch (error, stackTrace) {
      print('ERROR sending message: $error');
      print('Stack trace: $stackTrace');
      state = AsyncValue.error(error, stackTrace);
      return null;
    }
  }

  Future<void> startRecording() async {
    try {
      await _callService.startRecording();
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<Message?> stopRecordingAndSend() async {
    if (_currentCall == null) return null;

    try {
      // Stop recording and get audio path
      final audioPath = await _callService.stopRecording();

      if (audioPath != null) {
        // Transcribe audio
        final transcription = await _callService.transcribeAudio(audioPath);

        // Send transcribed message
        final message = await _callService.sendTextMessage(
          _currentCall!.id,
          _currentCall!.userId,
          transcription,
        );

        // Play TTS response if it's from agent
        if (message.isFromAgent) {
          await _callService.playResponse(message.content);
        }

        return message;
      }
      return null;
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
      return null;
    }
  }

  Future<void> endCall() async {
    try {
      await _callService.endCall();
      _currentCall = null;
      state = const AsyncValue.data(null);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  bool get isRecording => _callService.isRecording;
  bool get isSpeaking => _callService.isSpeaking;
  Call? get currentCall => _currentCall;
}
