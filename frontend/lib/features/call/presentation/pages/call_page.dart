import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/models/agent.dart';
import '../../../../core/models/message.dart';
import '../../../../core/services/call_service.dart';

class CallPage extends ConsumerStatefulWidget {
  final Agent agent;
  final String userId;

  const CallPage({
    super.key,
    required this.agent,
    required this.userId,
  });

  @override
  ConsumerState<CallPage> createState() => _CallPageState();
}

class _CallPageState extends ConsumerState<CallPage> {
  final TextEditingController _messageController = TextEditingController();
  final List<ChatMessage> _messages = [];
  bool _isInitialized = false;
  bool _isHoldingToTalk = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _startCall();
    });
  }

  Future<void> _startCall() async {
    try {
      await ref.read(activeCallProvider.notifier).startCall(
            widget.userId,
            widget.agent.id,
          );

      setState(() {
        _isInitialized = true;
        _messages.add(ChatMessage(
          content: "Hi! I'm ${widget.agent.name}. How can I help you today?",
          isFromUser: false,
          timestamp: DateTime.now(),
        ));
      });
    } catch (e) {
      setState(() {
        _messages.add(ChatMessage(
          content: "Failed to connect: $e",
          isFromUser: false,
          timestamp: DateTime.now(),
          isError: true,
        ));
      });
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final callService = ref.watch(callServiceProvider);
    final activeCall = ref.watch(activeCallProvider);

    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        leading: IconButton(
          onPressed: () async {
            await ref.read(activeCallProvider.notifier).endCall();
            Navigator.of(context).pop();
          },
          icon: const Icon(Icons.arrow_back, color: Colors.white),
        ),
        title: Row(
          children: [
            CircleAvatar(
              radius: 20,
              backgroundImage: widget.agent.avatarUrl != null
                  ? NetworkImage(widget.agent.avatarUrl!)
                  : null,
              child: widget.agent.avatarUrl == null
                  ? Text(
                      widget.agent.name.substring(0, 1).toUpperCase(),
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    )
                  : null,
            ),
            const SizedBox(width: 12),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.agent.name,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  _isInitialized ? 'Connected' : 'Connecting...',
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          // Messages
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return _buildMessageBubble(message);
              },
            ),
          ),

          // Input Section
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[900],
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(20),
                topRight: Radius.circular(20),
              ),
            ),
            child: Column(
              children: [
                // Text Input
                Row(
                  children: [
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        decoration: BoxDecoration(
                          color: Colors.grey[800],
                          borderRadius: BorderRadius.circular(25),
                        ),
                        child: TextField(
                          controller: _messageController,
                          style: const TextStyle(color: Colors.white),
                          decoration: const InputDecoration(
                            hintText: 'Type a message...',
                            hintStyle: TextStyle(color: Colors.grey),
                            border: InputBorder.none,
                          ),
                          onSubmitted: _sendTextMessage,
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: () =>
                          _sendTextMessage(_messageController.text),
                      icon: const Icon(Icons.send, color: Colors.blue),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Voice Controls
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildHoldToTalkButton(),
                    _buildRecordButton(callService),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        mainAxisAlignment: message.isFromUser
            ? MainAxisAlignment.end
            : MainAxisAlignment.start,
        children: [
          if (!message.isFromUser) ...[
            CircleAvatar(
              radius: 16,
              backgroundImage: widget.agent.avatarUrl != null
                  ? NetworkImage(widget.agent.avatarUrl!)
                  : null,
              child: widget.agent.avatarUrl == null
                  ? Text(
                      widget.agent.name.substring(0, 1).toUpperCase(),
                      style: const TextStyle(fontSize: 12),
                    )
                  : null,
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: message.isError
                    ? Colors.red[700]
                    : message.isFromUser
                        ? Colors.blue[700]
                        : Colors.grey[700],
                borderRadius: BorderRadius.circular(18),
              ),
              child: Text(
                message.content,
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ),
          if (message.isFromUser) ...[
            const SizedBox(width: 8),
            const CircleAvatar(
              radius: 16,
              child: Icon(Icons.person, size: 16),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildHoldToTalkButton() {
    return GestureDetector(
      onTapDown: (_) => _startHoldToTalk(),
      onTapUp: (_) => _stopHoldToTalk(),
      onTapCancel: () => _stopHoldToTalk(),
      child: Column(
        children: [
          Container(
            width: 60,
            height: 60,
            decoration: BoxDecoration(
              color: _isHoldingToTalk ? Colors.green[600] : Colors.grey[800],
              shape: BoxShape.circle,
              border: _isHoldingToTalk
                  ? Border.all(color: Colors.green, width: 2)
                  : null,
            ),
            child: Icon(
              Icons.mic,
              color: _isHoldingToTalk ? Colors.white : Colors.green,
              size: 24,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _isHoldingToTalk ? 'Recording...' : 'Hold to Talk',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecordButton(CallService callService) {
    return Column(
      children: [
        Container(
          width: 60,
          height: 60,
          decoration: BoxDecoration(
            color: Colors.grey[800],
            shape: BoxShape.circle,
          ),
          child: IconButton(
            onPressed:
                callService.isRecording ? _stopRecording : _startRecording,
            icon: Icon(
              callService.isRecording ? Icons.stop : Icons.mic,
              color: callService.isRecording ? Colors.red : Colors.blue,
              size: 24,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          callService.isRecording ? 'Stop' : 'Record',
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 10,
          ),
        ),
      ],
    );
  }

  Future<void> _startHoldToTalk() async {
    if (_isHoldingToTalk) return;

    setState(() {
      _isHoldingToTalk = true;
    });

    try {
      print('Starting hold-to-talk recording...');
      await ref.read(activeCallProvider.notifier).startRecording();
    } catch (e) {
      print('Error starting hold-to-talk: $e');
      setState(() {
        _isHoldingToTalk = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to start recording: $e')),
      );
    }
  }

  Future<void> _stopHoldToTalk() async {
    if (!_isHoldingToTalk) return;

    setState(() {
      _isHoldingToTalk = false;
    });

    try {
      print('Stopping hold-to-talk recording...');
      final response =
          await ref.read(activeCallProvider.notifier).stopRecordingAndSend();

      if (response != null) {
        setState(() {
          _messages.add(ChatMessage(
            content: "🎤 Voice message sent",
            isFromUser: true,
            timestamp: DateTime.now(),
          ));
          _messages.add(ChatMessage(
            content: response.content,
            isFromUser: false,
            timestamp: DateTime.now(),
          ));
        });
      }
    } catch (e) {
      print('Error stopping hold-to-talk: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to process voice message: $e')),
      );
    }
  }

  Future<void> _sendTextMessage(String text) async {
    if (text.trim().isEmpty) return;

    print('=== SENDING MESSAGE ===');
    print('Text: $text');
    print(
        'Current call: ${ref.read(activeCallProvider.notifier).currentCall?.id}');

    // Add user message
    setState(() {
      _messages.add(ChatMessage(
        content: text.trim(),
        isFromUser: true,
        timestamp: DateTime.now(),
      ));
    });

    _messageController.clear();

    try {
      // Send message and get response
      print('Calling sendTextMessage...');
      final response = await ref
          .read(activeCallProvider.notifier)
          .sendTextMessage(text.trim());
      print('Response received: ${response?.content}');

      if (response != null) {
        setState(() {
          _messages.add(ChatMessage(
            content: response.content,
            isFromUser: false,
            timestamp: DateTime.now(),
          ));
        });
      } else {
        print('Response was null');
        setState(() {
          _messages.add(ChatMessage(
            content: "No response received from agent",
            isFromUser: false,
            timestamp: DateTime.now(),
            isError: true,
          ));
        });
      }
    } catch (e) {
      print('Error sending message: $e');
      setState(() {
        _messages.add(ChatMessage(
          content: "Failed to send message: $e",
          isFromUser: false,
          timestamp: DateTime.now(),
          isError: true,
        ));
      });
    }
  }

  Future<void> _startRecording() async {
    try {
      print('Starting manual recording...');
      await ref.read(activeCallProvider.notifier).startRecording();
      setState(() {
        _messages.add(ChatMessage(
          content: "🎤 Recording... (tap Stop when done)",
          isFromUser: false,
          timestamp: DateTime.now(),
        ));
      });
    } catch (e) {
      print('Error starting recording: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to start recording: $e')),
      );
    }
  }

  Future<void> _stopRecording() async {
    try {
      print('Stopping manual recording...');
      final response =
          await ref.read(activeCallProvider.notifier).stopRecordingAndSend();

      setState(() {
        _messages.removeWhere((msg) => msg.content.contains("🎤 Recording..."));
      });

      if (response != null) {
        setState(() {
          _messages.add(ChatMessage(
            content: "Voice message sent",
            isFromUser: true,
            timestamp: DateTime.now(),
          ));
          _messages.add(ChatMessage(
            content: response.content,
            isFromUser: false,
            timestamp: DateTime.now(),
          ));
        });
      } else {
        print('No response received from recording');
        setState(() {
          _messages.add(ChatMessage(
            content: "Recording sent but no response received",
            isFromUser: false,
            timestamp: DateTime.now(),
            isError: true,
          ));
        });
      }
    } catch (e) {
      print('Error stopping recording: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to process voice message: $e')),
      );
    }
  }
}

class ChatMessage {
  final String content;
  final bool isFromUser;
  final DateTime timestamp;
  final bool isError;

  ChatMessage({
    required this.content,
    required this.isFromUser,
    required this.timestamp,
    this.isError = false,
  });
}
