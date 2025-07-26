import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../models/chat_models.dart';
import '../widgets/history_agent_item.dart';
import 'history_detail_screen.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  String _selectedFilter = 'All';
  final List<String> _filterOptions = [
    'All',
    'Today',
    'This Week',
    'This Month'
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<ChatProvider>(
        builder: (context, chatProvider, child) {
          final groupedHistory = _groupHistoryByAgent(chatProvider.messages);

          if (groupedHistory.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.history,
                    size: 80,
                    color: Colors.grey[600],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No Conversation History',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Start chatting with AI agents to see your history here',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            );
          }

          return Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Chat History',
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                    ),
                    PopupMenuButton<String>(
                      onSelected: (value) {
                        setState(() {
                          _selectedFilter = value;
                        });
                      },
                      icon: Icon(
                        Icons.filter_list,
                        color: Theme.of(context).primaryColor,
                      ),
                      itemBuilder: (context) => _filterOptions
                          .map((option) => PopupMenuItem(
                                value: option,
                                child: Text(option),
                              ))
                          .toList(),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: ListView.builder(
                    itemCount: groupedHistory.length,
                    itemBuilder: (context, index) {
                      final agentId = groupedHistory.keys.elementAt(index);
                      final messages = groupedHistory[agentId]!;
                      final agent = chatProvider.agents.firstWhere(
                        (a) => a.id == agentId,
                        orElse: () => Agent(
                          id: agentId,
                          name: 'Unknown Agent',
                          description: '',
                          personality: '',
                          capabilities: [],
                        ),
                      );

                      return HistoryAgentItem(
                        agent: agent,
                        messages: messages,
                        onTap: () =>
                            _navigateToHistoryDetail(context, agent, messages),
                      );
                    },
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Map<String, List<Message>> _groupHistoryByAgent(List<Message> messages) {
    final Map<String, List<Message>> grouped = {};

    for (final message in messages) {
      final agentId = message.sender == 'user' ? 'user' : message.sender;
      if (!grouped.containsKey(agentId)) {
        grouped[agentId] = [];
      }
      grouped[agentId]!.add(message);
    }

    // Filter by date if needed
    if (_selectedFilter != 'All') {
      final now = DateTime.now();
      DateTime cutoffDate;

      switch (_selectedFilter) {
        case 'Today':
          cutoffDate = DateTime(now.year, now.month, now.day);
          break;
        case 'This Week':
          cutoffDate = now.subtract(Duration(days: now.weekday - 1));
          break;
        case 'This Month':
          cutoffDate = DateTime(now.year, now.month, 1);
          break;
        default:
          cutoffDate = DateTime(1970);
      }

      grouped.removeWhere((key, messages) {
        messages
            .removeWhere((message) => message.timestamp.isBefore(cutoffDate));
        return messages.isEmpty;
      });
    }

    // Sort by most recent message
    final sortedEntries = grouped.entries.toList()
      ..sort((a, b) {
        final lastMessageA = a.value.isNotEmpty
            ? a.value.reduce((curr, next) =>
                curr.timestamp.isAfter(next.timestamp) ? curr : next)
            : Message(
                id: '',
                content: '',
                sender: '',
                timestamp: DateTime(1970),
                type: MessageType.text,
              );
        final lastMessageB = b.value.isNotEmpty
            ? b.value.reduce((curr, next) =>
                curr.timestamp.isAfter(next.timestamp) ? curr : next)
            : Message(
                id: '',
                content: '',
                sender: '',
                timestamp: DateTime(1970),
                type: MessageType.text,
              );
        return lastMessageB.timestamp.compareTo(lastMessageA.timestamp);
      });

    return Map.fromEntries(sortedEntries);
  }

  void _navigateToHistoryDetail(
      BuildContext context, Agent agent, List<Message> messages) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => HistoryDetailScreen(
          agent: agent,
          messages: messages,
        ),
      ),
    );
  }
}
