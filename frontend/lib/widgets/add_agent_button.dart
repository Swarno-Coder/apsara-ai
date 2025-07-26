import 'package:flutter/material.dart';

class AddAgentButton extends StatelessWidget {
  final VoidCallback onPressed;
  final bool isCompact;

  const AddAgentButton({
    super.key,
    required this.onPressed,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context) {
    if (isCompact) {
      return IconButton(
        onPressed: onPressed,
        icon: Icon(
          Icons.add_circle_outline,
          color: Theme.of(context).primaryColor,
        ),
        tooltip: 'Add New Agent',
      );
    }

    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: const Icon(Icons.add),
      label: const Text('Add AI Agent'),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(
          horizontal: 24,
          vertical: 12,
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
      ),
    );
  }
}
