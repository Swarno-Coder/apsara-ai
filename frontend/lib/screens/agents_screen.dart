import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/chat_provider.dart';
import '../widgets/agent_card.dart';
import '../widgets/add_agent_button.dart';
import '../models/chat_models.dart';
import 'chat_screen.dart';
import 'add_agent_screen.dart';

class AgentsScreen extends StatefulWidget {
  const AgentsScreen({super.key});

  @override
  State<AgentsScreen> createState() => _AgentsScreenState();
}

class _AgentsScreenState extends State<AgentsScreen> {
  @override
  void initState() {
    super.initState();
    // Connect to WebSocket when screen loads
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().connect();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<ChatProvider>(
        builder: (context, chatProvider, child) {
          if (!chatProvider.isConnected) {
            return const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  CircularProgressIndicator(),
                  SizedBox(height: 16),
                  Text('Connecting to AI Assistant...'),
                ],
              ),
            );
          }

          if (chatProvider.agents.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.psychology_outlined,
                    size: 80,
                    color: Colors.grey[600],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No AI Agents Available',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Add your first AI companion to get started',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey[600],
                        ),
                  ),
                  const SizedBox(height: 24),
                  AddAgentButton(
                    onPressed: () => _navigateToAddAgent(context),
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
                      'Your AI Agents',
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                    ),
                    AddAgentButton(
                      onPressed: () => _navigateToAddAgent(context),
                      isCompact: true,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: GridView.builder(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 0.85,
                    ),
                    itemCount: chatProvider.agents.length,
                    itemBuilder: (context, index) {
                      final agent = chatProvider.agents[index];
                      return AgentCard(
                        agent: agent,
                        onTap: () => _navigateToChat(context, agent),
                        isSelected: chatProvider.currentAgent?.id == agent.id,
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

  void _navigateToChat(BuildContext context, Agent agent) {
    context.read<ChatProvider>().switchAgent(agent.id);
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ChatScreen(agent: agent),
      ),
    );
  }

  void _navigateToAddAgent(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const AddAgentScreen(),
      ),
    );
  }
}
