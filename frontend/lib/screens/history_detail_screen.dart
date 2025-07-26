import 'package:flutter/material.dart';
import '../models/chat_models.dart';
import '../widgets/message_bubble.dart';

class HistoryDetailScreen extends StatefulWidget {
  final Agent agent;
  final List<Message> messages;

  const HistoryDetailScreen({
    super.key,
    required this.agent,
    required this.messages,
  });

  @override
  State<HistoryDetailScreen> createState() => _HistoryDetailScreenState();
}

class _HistoryDetailScreenState extends State<HistoryDetailScreen> {
  final ScrollController _scrollController = ScrollController();
  String _selectedFilter = 'All';
  final List<String> _filterOptions = ['All', 'Text', 'Audio', 'System'];

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final filteredMessages = _getFilteredMessages();

    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            CircleAvatar(
              radius: 16,
              backgroundColor: Theme.of(context).primaryColor.withOpacity(0.1),
              backgroundImage: widget.agent.avatarUrl != null
                  ? NetworkImage(widget.agent.avatarUrl!)
                  : null,
              child: widget.agent.avatarUrl == null
                  ? Icon(
                      Icons.psychology_rounded,
                      color: Theme.of(context).primaryColor,
                      size: 20,
                    )
                  : null,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.agent.name,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  Text(
                    'Chat History',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[400],
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() {
                _selectedFilter = value;
              });
            },
            icon: const Icon(Icons.filter_list),
            itemBuilder: (context) => _filterOptions
                .map((option) => PopupMenuItem(
                      value: option,
                      child: Row(
                        children: [
                          Icon(_getFilterIcon(option)),
                          const SizedBox(width: 8),
                          Text(option),
                        ],
                      ),
                    ))
                .toList(),
          ),
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: () => _showDeleteDialog(),
            tooltip: 'Clear History',
          ),
        ],
      ),
      body: Column(
        children: [
          _buildStatsCard(),
          Expanded(
            child: filteredMessages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: filteredMessages.length,
                    itemBuilder: (context, index) {
                      final message = filteredMessages[index];
                      return MessageBubble(
                        message: message,
                        isFromUser: message.sender == 'user',
                      );
                    },
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _scrollToBottom(),
        tooltip: 'Scroll to Bottom',
        child: const Icon(Icons.keyboard_arrow_down),
      ),
    );
  }

  Widget _buildStatsCard() {
    final totalMessages = widget.messages.length;
    final userMessages =
        widget.messages.where((m) => m.sender == 'user').length;
    final agentMessages =
        widget.messages.where((m) => m.sender == widget.agent.name).length;
    final audioMessages =
        widget.messages.where((m) => m.type == MessageType.audio).length;

    final oldestMessage = widget.messages.isNotEmpty
        ? widget.messages.reduce((curr, next) =>
            curr.timestamp.isBefore(next.timestamp) ? curr : next)
        : null;

    final newestMessage = widget.messages.isNotEmpty
        ? widget.messages.reduce((curr, next) =>
            curr.timestamp.isAfter(next.timestamp) ? curr : next)
        : null;

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Conversation Statistics',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'Total Messages',
                    totalMessages.toString(),
                    Icons.chat_bubble_outline,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Your Messages',
                    userMessages.toString(),
                    Icons.person,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Agent Messages',
                    agentMessages.toString(),
                    Icons.psychology,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'Voice Messages',
                    audioMessages.toString(),
                    Icons.mic,
                  ),
                ),
              ],
            ),
            if (oldestMessage != null && newestMessage != null) ...[
              const SizedBox(height: 12),
              const Divider(),
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'First: ${_formatDate(oldestMessage.timestamp)}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[400],
                        ),
                  ),
                  Text(
                    'Latest: ${_formatDate(newestMessage.timestamp)}',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: Colors.grey[400],
                        ),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(
          icon,
          color: Theme.of(context).primaryColor,
          size: 20,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
                color: Theme.of(context).primaryColor,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[400],
              ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.filter_list_off,
            size: 64,
            color: Colors.grey[600],
          ),
          const SizedBox(height: 16),
          Text(
            'No messages match the filter',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                  color: Colors.grey[600],
                ),
          ),
          const SizedBox(height: 8),
          Text(
            'Try selecting a different filter option',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[400],
                ),
          ),
        ],
      ),
    );
  }

  List<Message> _getFilteredMessages() {
    if (_selectedFilter == 'All') {
      return widget.messages;
    }

    return widget.messages.where((message) {
      switch (_selectedFilter) {
        case 'Text':
          return message.type == MessageType.text;
        case 'Audio':
          return message.type == MessageType.audio;
        case 'System':
          return message.type == MessageType.system;
        default:
          return true;
      }
    }).toList();
  }

  IconData _getFilterIcon(String filter) {
    switch (filter) {
      case 'Text':
        return Icons.text_fields;
      case 'Audio':
        return Icons.mic;
      case 'System':
        return Icons.settings;
      default:
        return Icons.all_inclusive;
    }
  }

  String _formatDate(DateTime dateTime) {
    final now = DateTime.now();
    final difference = now.difference(dateTime);

    if (difference.inDays == 0) {
      return 'Today ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays == 1) {
      return 'Yesterday ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
    } else if (difference.inDays < 7) {
      return '${difference.inDays}d ago';
    } else {
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    }
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  void _showDeleteDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Chat History'),
        content: Text(
          'Are you sure you want to clear all chat history with ${widget.agent.name}? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Chat history cleared'),
                  backgroundColor: Colors.green,
                ),
              );
            },
            child: const Text(
              'Clear',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}
