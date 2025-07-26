import 'dart:io';
import 'dart:typed_data';
import 'package:flutter_sound/flutter_sound.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:async';

class AudioService {
  FlutterSoundRecorder? _recorder;
  FlutterSoundPlayer? _player;

  bool _isRecording = false;
  bool _isPlaying = false;
  bool _isInitialized = false;

  String? _currentRecordingPath;
  StreamSubscription? _recorderSubscription;
  StreamSubscription? _playerSubscription;

  final StreamController<double> _recordingLevelController =
      StreamController<double>.broadcast();
  final StreamController<Duration> _playbackPositionController =
      StreamController<Duration>.broadcast();
  final StreamController<List<int>> _audioDataController =
      StreamController<List<int>>.broadcast();

  // Streams
  Stream<double> get recordingLevelStream => _recordingLevelController.stream;
  Stream<Duration> get playbackPositionStream =>
      _playbackPositionController.stream;
  Stream<List<int>> get audioDataStream => _audioDataController.stream;

  // Getters
  bool get isRecording => _isRecording;
  bool get isPlaying => _isPlaying;
  bool get isInitialized => _isInitialized;

  // Initialize audio service
  Future<bool> initialize() async {
    try {
      _recorder = FlutterSoundRecorder();
      _player = FlutterSoundPlayer();

      // Request microphone permission
      final micPermission = await Permission.microphone.request();
      if (micPermission != PermissionStatus.granted) {
        print('Microphone permission denied');
        return false;
      }

      // Initialize recorder and player
      await _recorder!.openRecorder();
      await _player!.openPlayer();

      _isInitialized = true;
      print('Audio service initialized successfully');
      return true;
    } catch (e) {
      print('Error initializing audio service: $e');
      return false;
    }
  }

  // Start recording
  Future<bool> startRecording({
    bool streamToWebSocket = false,
    int sampleRate = 16000,
  }) async {
    if (!_isInitialized || _isRecording) {
      print('Cannot start recording: not initialized or already recording');
      return false;
    }

    try {
      // Get temporary directory for recording
      final tempDir = await getTemporaryDirectory();
      _currentRecordingPath =
          '${tempDir.path}/recording_${DateTime.now().millisecondsSinceEpoch}.wav';

      // Configure recording
      await _recorder!.startRecorder(
        toFile: _currentRecordingPath,
        codec: Codec.pcm16WAV,
        sampleRate: sampleRate,
        numChannels: 1,
      );

      _isRecording = true;

      // Listen to recording level
      _recorderSubscription = _recorder!.onProgress!.listen((event) {
        _recordingLevelController.add(event.decibels ?? 0.0);

        // If streaming to WebSocket, send audio data chunks
        if (streamToWebSocket) {
          _sendAudioChunk();
        }
      });

      print('Recording started: $_currentRecordingPath');
      return true;
    } catch (e) {
      print('Error starting recording: $e');
      _isRecording = false;
      return false;
    }
  }

  // Stop recording
  Future<String?> stopRecording() async {
    if (!_isRecording) {
      print('Not currently recording');
      return null;
    }

    try {
      await _recorder!.stopRecorder();
      _recorderSubscription?.cancel();
      _isRecording = false;

      print('Recording stopped: $_currentRecordingPath');
      return _currentRecordingPath;
    } catch (e) {
      print('Error stopping recording: $e');
      _isRecording = false;
      return null;
    }
  }

  // Play audio file
  Future<bool> playAudio(String filePath) async {
    if (!_isInitialized || _isPlaying) {
      print('Cannot play audio: not initialized or already playing');
      return false;
    }

    try {
      await _player!.startPlayer(
        fromURI: filePath,
        codec: Codec.pcm16WAV,
      );

      _isPlaying = true;

      // Listen to playback progress
      _playerSubscription = _player!.onProgress!.listen((event) {
        _playbackPositionController.add(event.position);
      });

      // Listen for playback completion
      _player!.onProgress!
          .where((event) => event.position >= event.duration)
          .listen((_) {
        stopPlayback();
      });

      print('Playing audio: $filePath');
      return true;
    } catch (e) {
      print('Error playing audio: $e');
      _isPlaying = false;
      return false;
    }
  }

  // Play audio from bytes
  Future<bool> playAudioFromBytes(Uint8List audioBytes) async {
    try {
      // Save bytes to temporary file
      final tempDir = await getTemporaryDirectory();
      final tempFile = File(
          '${tempDir.path}/temp_audio_${DateTime.now().millisecondsSinceEpoch}.wav');
      await tempFile.writeAsBytes(audioBytes);

      return await playAudio(tempFile.path);
    } catch (e) {
      print('Error playing audio from bytes: $e');
      return false;
    }
  }

  // Stop playback
  Future<void> stopPlayback() async {
    if (_isPlaying) {
      try {
        await _player!.stopPlayer();
        _playerSubscription?.cancel();
        _isPlaying = false;
        print('Playback stopped');
      } catch (e) {
        print('Error stopping playback: $e');
      }
    }
  }

  // Pause playback
  Future<void> pausePlayback() async {
    if (_isPlaying) {
      try {
        await _player!.pausePlayer();
        print('Playback paused');
      } catch (e) {
        print('Error pausing playback: $e');
      }
    }
  }

  // Resume playback
  Future<void> resumePlayback() async {
    if (!_isPlaying) {
      try {
        await _player!.resumePlayer();
        print('Playback resumed');
      } catch (e) {
        print('Error resuming playback: $e');
      }
    }
  }

  // Get recording duration
  Duration? getRecordingDuration() {
    return _recorder?.recorderState == RecorderState.isRecording
        ? _recorder!.onProgress?.value?.duration
        : null;
  }

  // Get audio file duration
  Future<Duration?> getAudioDuration(String filePath) async {
    try {
      // This is a simplified implementation
      // In a real app, you might want to use a more robust method
      final file = File(filePath);
      if (await file.exists()) {
        final stat = await file.stat();
        // Rough estimation based on file size (for WAV files)
        final sizeInBytes = stat.size;
        final durationInSeconds = sizeInBytes / (16000 * 2); // 16kHz, 16-bit
        return Duration(milliseconds: (durationInSeconds * 1000).round());
      }
    } catch (e) {
      print('Error getting audio duration: $e');
    }
    return null;
  }

  // Send audio chunk to WebSocket (placeholder)
  void _sendAudioChunk() async {
    if (_currentRecordingPath != null) {
      try {
        final file = File(_currentRecordingPath!);
        if (await file.exists()) {
          final bytes = await file.readAsBytes();
          // Take last chunk (this is simplified - in real implementation,
          // you'd want to stream real-time data)
          _audioDataController.add(bytes);
        }
      } catch (e) {
        print('Error reading audio chunk: $e');
      }
    }
  }

  // Dispose resources
  Future<void> dispose() async {
    await stopRecording();
    await stopPlayback();

    _recorderSubscription?.cancel();
    _playerSubscription?.cancel();

    _recordingLevelController.close();
    _playbackPositionController.close();
    _audioDataController.close();

    if (_isInitialized) {
      await _recorder?.closeRecorder();
      await _player?.closePlayer();
    }

    _recorder = null;
    _player = null;
    _isInitialized = false;

    print('Audio service disposed');
  }
}
