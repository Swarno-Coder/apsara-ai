class AppConfig {
  // Backend Configuration
  static const String backendUrl = 'ws://localhost:8000/ws';
  static const String backendHttpUrl = 'http://localhost:8000';

  // Firebase Configuration
  static const String firebaseProjectId = 'your-firebase-project-id';

  // Audio Configuration
  static const int sampleRate = 16000;
  static const int chunkSize = 1024;
  static const Duration maxRecordingDuration = Duration(seconds: 30);

  // Chat Configuration
  static const int maxChatHistory = 50;
  static const Duration typingDelay = Duration(milliseconds: 500);

  // Agent Configuration
  static const String defaultAgentId = 'friendly_assistant';

  // UI Configuration
  static const Duration animationDuration = Duration(milliseconds: 300);
  static const double borderRadius = 12.0;
  static const double padding = 16.0;
}
