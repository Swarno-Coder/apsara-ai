import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../../../core/models/agent.dart';
import '../../../../core/theme/app_theme.dart';

class AgentCard extends StatelessWidget {
  final Agent agent;
  final VoidCallback onTap;

  const AgentCard({
    super.key,
    required this.agent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Agent Avatar
            Expanded(
              flex: 3,
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(20),
                  ),
                  gradient: _getPersonalityGradient(agent.personality),
                ),
                child: Stack(
                  children: [
                    // Avatar Image
                    Center(
                      child: _buildAvatar(),
                    ),

                    // Online Status
                    if (agent.isOnline)
                      Positioned(
                        top: 12,
                        right: 12,
                        child: Container(
                          width: 12,
                          height: 12,
                          decoration: BoxDecoration(
                            color: AppTheme.accentColor,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: Colors.white,
                              width: 2,
                            ),
                          ),
                        ),
                      ),

                    // Compatibility Score
                    if (agent.compatibilityScore != null)
                      Positioned(
                        top: 12,
                        left: 12,
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: Colors.black.withOpacity(0.7),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            '${(agent.compatibilityScore! * 100).round()}%',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 10,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ),

            // Agent Info
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name
                    Text(
                      agent.name,
                      style: AppTextStyles.headline3.copyWith(
                        fontSize: 18,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),

                    const SizedBox(height: 4),

                    // Personality
                    Text(
                      agent.personalityDisplayName,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: _getPersonalityColor(agent.personality),
                        fontWeight: FontWeight.w500,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),

                    const Spacer(),

                    // Stats
                    Row(
                      children: [
                        const Icon(
                          Icons.phone,
                          size: 14,
                          color: AppTheme.mediumGray,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '${agent.totalCalls}',
                          style: AppTextStyles.bodySmall,
                        ),
                        const Spacer(),
                        Text(
                          agent.compatibilityText,
                          style: AppTextStyles.bodySmall.copyWith(
                            color: _getCompatibilityColor(
                                agent.compatibilityScore),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAvatar() {
    if (agent.avatarUrl != null && agent.avatarUrl!.isNotEmpty) {
      return ClipOval(
        child: CachedNetworkImage(
          imageUrl: agent.avatarUrl!,
          width: 80,
          height: 80,
          fit: BoxFit.cover,
          placeholder: (context, url) => _buildDefaultAvatar(),
          errorWidget: (context, url, error) => _buildDefaultAvatar(),
        ),
      );
    }

    return _buildDefaultAvatar();
  }

  Widget _buildDefaultAvatar() {
    return Container(
      width: 80,
      height: 80,
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        shape: BoxShape.circle,
      ),
      child: Icon(
        _getPersonalityIcon(agent.personality),
        size: 40,
        color: Colors.white,
      ),
    );
  }

  LinearGradient _getPersonalityGradient(String personality) {
    switch (personality.toLowerCase()) {
      case 'caring':
        return const LinearGradient(
          colors: [Color(0xFFFF9A9E), Color(0xFFFECFEF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'playful':
        return const LinearGradient(
          colors: [Color(0xFFFFD93D), Color(0xFFFF6B6B)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'romantic':
        return const LinearGradient(
          colors: [Color(0xFFFF6B9D), Color(0xFFC44569)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'supportive':
        return const LinearGradient(
          colors: [Color(0xFF6AB7FF), Color(0xFF4169E1)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'intelligent':
        return const LinearGradient(
          colors: [Color(0xFF667EEA), Color(0xFF764BA2)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'funny':
        return const LinearGradient(
          colors: [Color(0xFFFFA726), Color(0xFFFF7043)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'mysterious':
        return const LinearGradient(
          colors: [Color(0xFF2C3E50), Color(0xFF4A6741)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      case 'energetic':
        return const LinearGradient(
          colors: [Color(0xFF42E695), Color(0xFF3BB2B8)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
      default:
        return const LinearGradient(
          colors: [AppTheme.primaryColor, AppTheme.secondaryColor],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        );
    }
  }

  Color _getPersonalityColor(String personality) {
    switch (personality.toLowerCase()) {
      case 'caring':
        return const Color(0xFFFF6B9D);
      case 'playful':
        return const Color(0xFFFF9500);
      case 'romantic':
        return const Color(0xFFC44569);
      case 'supportive':
        return const Color(0xFF4169E1);
      case 'intelligent':
        return const Color(0xFF764BA2);
      case 'funny':
        return const Color(0xFFFF7043);
      case 'mysterious':
        return const Color(0xFF2C3E50);
      case 'energetic':
        return const Color(0xFF42E695);
      default:
        return AppTheme.primaryColor;
    }
  }

  IconData _getPersonalityIcon(String personality) {
    switch (personality.toLowerCase()) {
      case 'caring':
        return Icons.favorite;
      case 'playful':
        return Icons.emoji_emotions;
      case 'romantic':
        return Icons.favorite_border;
      case 'supportive':
        return Icons.support;
      case 'intelligent':
        return Icons.psychology;
      case 'funny':
        return Icons.sentiment_very_satisfied;
      case 'mysterious':
        return Icons.visibility;
      case 'energetic':
        return Icons.flash_on;
      default:
        return Icons.person;
    }
  }

  Color _getCompatibilityColor(double? score) {
    if (score == null) return AppTheme.mediumGray;

    if (score >= 0.8) return AppTheme.accentColor;
    if (score >= 0.6) return const Color(0xFF10B981);
    if (score >= 0.4) return AppTheme.warningColor;
    return AppTheme.errorColor;
  }
}
