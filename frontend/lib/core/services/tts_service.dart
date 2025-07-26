import 'package:just_audio/just_audio.dart';

class TTSService {
  static final TTSService _instance = TTSService._internal();
  factory TTSService() => _instance;
  TTSService._internal();

  final AudioPlayer _audioPlayer = AudioPlayer();
  bool _isInitialized = false;
  bool _isPlaying = false;

  bool get isPlaying => _isPlaying;
  bool get isInitialized => _isInitialized;

  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      _isInitialized = true;
      print('TTS Service initialized successfully');
    } catch (e) {
      print('Error initializing TTS service: $e');
      rethrow;
    }
  }

  Future<void> speak(String text) async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isPlaying) {
      await stop();
    }

    try {
      _isPlaying = true;

      // For now, we'll use text-to-speech via the backend
      // In a real implementation, you would call the backend TTS service
      print('Speaking: $text');

      // Simulate TTS delay
      await Future.delayed(const Duration(milliseconds: 500));

      // Here you would actually get audio data from backend and play it
      // For now, just simulate completion
      await Future.delayed(Duration(milliseconds: text.length * 50));

      _isPlaying = false;
      print('Finished speaking');
    } catch (e) {
      print('Error in TTS: $e');
      _isPlaying = false;
      rethrow;
    }
  }

  Future<void> stop() async {
    if (!_isPlaying) return;

    try {
      await _audioPlayer.stop();
      _isPlaying = false;
      print('TTS stopped');
    } catch (e) {
      print('Error stopping TTS: $e');
      _isPlaying = false;
    }
  }

  void dispose() {
    _audioPlayer.dispose();
    _isInitialized = false;
    _isPlaying = false;
  }
}
