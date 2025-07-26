import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/models/agent.dart';
import '../../../../core/services/api_service.dart';

// Providers
final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

final agentsProvider =
    StateNotifierProvider<AgentsNotifier, AsyncValue<List<Agent>>>(
  (ref) => AgentsNotifier(ref.read(apiServiceProvider)),
);

// State Notifier
class AgentsNotifier extends StateNotifier<AsyncValue<List<Agent>>> {
  final ApiService _apiService;

  AgentsNotifier(this._apiService) : super(const AsyncValue.loading());

  Future<void> loadAgents(String userId) async {
    state = const AsyncValue.loading();

    try {
      final agents = await _apiService.getAgents(userId);
      state = AsyncValue.data(agents);
    } catch (error, stackTrace) {
      state = AsyncValue.error(error, stackTrace);
    }
  }

  Future<void> refreshAgents(String userId) async {
    try {
      final agents = await _apiService.getAgents(userId);
      state = AsyncValue.data(agents);
    } catch (error, stackTrace) {
      // If refresh fails, show error
      state = AsyncValue.error(error, stackTrace);
    }
  }

  void updateAgent(Agent updatedAgent) {
    state.whenData((agents) {
      final updatedAgents = agents.map((agent) {
        return agent.id == updatedAgent.id ? updatedAgent : agent;
      }).toList();

      state = AsyncValue.data(updatedAgents);
    });
  }

  Agent? getAgentById(String agentId) {
    return state.value?.firstWhere(
      (agent) => agent.id == agentId,
      orElse: () => throw StateError('Agent not found'),
    );
  }
}
