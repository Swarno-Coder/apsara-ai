class Message {
  final String id;
  final String content;
  final String sender; // 'user' or agent name
  final DateTime timestamp;
  final MessageType type;
  final String? audioUrl;
  final String? emotion;
  final Map<String, dynamic>? metadata;

  Message({
    required this.id,
    required this.content,
    required this.sender,
    required this.timestamp,
    required this.type,
    this.audioUrl,
    this.emotion,
    this.metadata,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? '',
      content: json['content'] ?? '',
      sender: json['sender'] ?? '',
      timestamp: DateTime.parse(json['timestamp']),
      type: MessageType.values.firstWhere(
        (e) => e.toString().split('.').last == json['type'],
        orElse: () => MessageType.text,
      ),
      audioUrl: json['audioUrl'],
      emotion: json['emotion'],
      metadata: json['metadata']?.cast<String, dynamic>(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'content': content,
      'sender': sender,
      'timestamp': timestamp.toIso8601String(),
      'type': type.toString().split('.').last,
      'audioUrl': audioUrl,
      'emotion': emotion,
      'metadata': metadata,
    };
  }

  Message copyWith({
    String? id,
    String? content,
    String? sender,
    DateTime? timestamp,
    MessageType? type,
    String? audioUrl,
    String? emotion,
    Map<String, dynamic>? metadata,
  }) {
    return Message(
      id: id ?? this.id,
      content: content ?? this.content,
      sender: sender ?? this.sender,
      timestamp: timestamp ?? this.timestamp,
      type: type ?? this.type,
      audioUrl: audioUrl ?? this.audioUrl,
      emotion: emotion ?? this.emotion,
      metadata: metadata ?? this.metadata,
    );
  }
}

enum MessageType {
  text,
  audio,
  system,
  emotion,
}

class Agent {
  final String id;
  final String name;
  final String description;
  final String personality;
  final String? avatarUrl;
  final List<String> capabilities;
  final bool isActive;

  Agent({
    required this.id,
    required this.name,
    required this.description,
    required this.personality,
    this.avatarUrl,
    required this.capabilities,
    this.isActive = true,
  });

  factory Agent.fromJson(Map<String, dynamic> json) {
    return Agent(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      description: json['description'] ?? '',
      personality: json['personality'] ?? '',
      avatarUrl: json['avatarUrl'],
      capabilities: List<String>.from(json['capabilities'] ?? []),
      isActive: json['isActive'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'personality': personality,
      'avatarUrl': avatarUrl,
      'capabilities': capabilities,
      'isActive': isActive,
    };
  }
}

class ChatSession {
  final String id;
  final String userId;
  final String agentId;
  final String title;
  final DateTime createdAt;
  final DateTime lastMessageAt;
  final List<Message> messages;
  final bool isActive;

  ChatSession({
    required this.id,
    required this.userId,
    required this.agentId,
    required this.title,
    required this.createdAt,
    required this.lastMessageAt,
    required this.messages,
    this.isActive = true,
  });

  factory ChatSession.fromJson(Map<String, dynamic> json) {
    return ChatSession(
      id: json['id'] ?? '',
      userId: json['userId'] ?? '',
      agentId: json['agentId'] ?? '',
      title: json['title'] ?? '',
      createdAt: DateTime.parse(json['createdAt']),
      lastMessageAt: DateTime.parse(json['lastMessageAt']),
      messages: (json['messages'] as List?)
              ?.map((m) => Message.fromJson(m))
              .toList() ??
          [],
      isActive: json['isActive'] ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'agentId': agentId,
      'title': title,
      'createdAt': createdAt.toIso8601String(),
      'lastMessageAt': lastMessageAt.toIso8601String(),
      'messages': messages.map((m) => m.toJson()).toList(),
      'isActive': isActive,
    };
  }

  ChatSession copyWith({
    String? id,
    String? userId,
    String? agentId,
    String? title,
    DateTime? createdAt,
    DateTime? lastMessageAt,
    List<Message>? messages,
    bool? isActive,
  }) {
    return ChatSession(
      id: id ?? this.id,
      userId: userId ?? this.userId,
      agentId: agentId ?? this.agentId,
      title: title ?? this.title,
      createdAt: createdAt ?? this.createdAt,
      lastMessageAt: lastMessageAt ?? this.lastMessageAt,
      messages: messages ?? this.messages,
      isActive: isActive ?? this.isActive,
    );
  }
}
