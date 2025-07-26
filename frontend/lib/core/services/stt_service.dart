import 'package:record/record.dart';
import 'package:flutter/foundation.dart';

class STTService {
  static final STTService _instance = STTService._internal();
  factory STTService() => _instance;
  STTService._internal();

  final AudioRecorder _audioRecorder = AudioRecorder();
  bool _isRecording = false;
  bool _isInitialized = false;

  bool get isRecording => _isRecording;
  bool get isInitialized => _isInitialized;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Check if recorder has permission
      final bool hasPermission = await _audioRecorder.hasPermission();
      if (!hasPermission) {
        if (kIsWeb) {
          print('Microphone permission may need to be granted in browser');
          // On web, we'll try to start recording anyway
          // The browser will prompt for permission
        } else {
          throw Exception('Microphone permission not granted');
        }
      }

      _isInitialized = true;
      print('STT Service initialized successfully');
    } catch (e) {
      print('Error initializing STT service: $e');
      // Don't rethrow on web - allow the service to work with limited functionality
      if (!kIsWeb) {
        rethrow;
      }
      _isInitialized = true; // Allow to proceed on web
    }
  }

  Future<void> startRecording() async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isRecording) return;

    try {
      // Configure recording settings for web compatibility
      final config = RecordConfig(
        encoder: kIsWeb ? AudioEncoder.wav : AudioEncoder.wav,
        sampleRate: kIsWeb ? 16000 : 16000,
        bitRate: kIsWeb ? 16000 : 128000, // Lower bitrate for web
      );

      // Start recording with a web-compatible path
      final String path =
          kIsWeb ? 'audio_recording.wav' : 'audio_recording.wav';
      await _audioRecorder.start(config, path: path);
      _isRecording = true;
      print('Recording started');
    } catch (e) {
      print('Error starting recording: $e');
      _isRecording = false;

      // On web, provide more helpful error message
      if (kIsWeb) {
        throw Exception(
            'Could not start recording. Please allow microphone access in your browser and try again.');
      } else {
        rethrow;
      }
    }
  }

  Future<String?> stopRecording() async {
    if (!_isRecording) return null;

    try {
      final String? path = await _audioRecorder.stop();
      _isRecording = false;
      print('Recording stopped: $path');
      return path;
    } catch (e) {
      print('Error stopping recording: $e');
      _isRecording = false;
      rethrow;
    }
  }

  Future<void> cancelRecording() async {
    if (!_isRecording) return;

    try {
      await _audioRecorder.cancel();
      _isRecording = false;
      print('Recording cancelled');
    } catch (e) {
      print('Error cancelling recording: $e');
      _isRecording = false;
    }
  }

  // Simulated transcription - replace with real STT service
  Future<String> transcribeAudio(String? audioPath) async {
    try {
      if (audioPath == null) {
        throw Exception('No audio file to transcribe');
      }

      // Simulate transcription processing
      await Future.delayed(const Duration(milliseconds: 1500));

      // Return varied simulated transcriptions for testing
      final List<String> sampleTranscriptions = [
        "Hello, how are you doing today?",
        "I'm feeling great and wanted to talk to you",
        "Can you tell me about your day?",
        "I love spending time chatting with you",
        "What's your favorite thing to do?",
        "You're such a good listener",
        "I had an interesting day today",
        "Thanks for being here with me",
      ];

      final random =
          DateTime.now().millisecondsSinceEpoch % sampleTranscriptions.length;
      final transcription = sampleTranscriptions[random];

      print('Transcribed: $transcription');
      return transcription;
    } catch (e) {
      print('Transcription error: $e');
      return "I'd like to chat with you";
    }
  }

  void dispose() {
    _audioRecorder.dispose();
    _isInitialized = false;
    _isRecording = false;
  }
}
