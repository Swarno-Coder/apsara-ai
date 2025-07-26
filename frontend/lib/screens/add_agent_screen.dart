import 'package:flutter/material.dart';
import '../models/chat_models.dart';

class AddAgentScreen extends StatefulWidget {
  const AddAgentScreen({super.key});

  @override
  State<AddAgentScreen> createState() => _AddAgentScreenState();
}

class _AddAgentScreenState extends State<AddAgentScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _personalityController = TextEditingController();
  final _avatarUrlController = TextEditingController();

  final List<String> _capabilities = [];
  final _capabilityController = TextEditingController();

  final List<String> _predefinedCapabilities = [
    'Text Chat',
    'Voice Chat',
    'Emotional Support',
    'Task Assistance',
    'Creative Writing',
    'Code Help',
    'Language Translation',
    'Math Problem Solving',
    'Storytelling',
    'Music Recommendations',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _personalityController.dispose();
    _avatarUrlController.dispose();
    _capabilityController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Add New Agent'),
        actions: [
          TextButton(
            onPressed: _saveAgent,
            child: const Text(
              'Save',
              style: TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildAvatarSection(),
              const SizedBox(height: 24),
              _buildBasicInfoSection(),
              const SizedBox(height: 24),
              _buildCapabilitiesSection(),
              const SizedBox(height: 24),
              _buildPersonalitySection(),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAvatarSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Avatar',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            Center(
              child: CircleAvatar(
                radius: 50,
                backgroundColor:
                    Theme.of(context).primaryColor.withOpacity(0.1),
                backgroundImage: _avatarUrlController.text.isNotEmpty
                    ? NetworkImage(_avatarUrlController.text)
                    : null,
                child: _avatarUrlController.text.isEmpty
                    ? Icon(
                        Icons.psychology_rounded,
                        size: 50,
                        color: Theme.of(context).primaryColor,
                      )
                    : null,
              ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _avatarUrlController,
              decoration: const InputDecoration(
                labelText: 'Avatar URL (optional)',
                hintText: 'https://example.com/avatar.jpg',
                prefixIcon: Icon(Icons.image),
              ),
              onChanged: (value) => setState(() {}),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBasicInfoSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Basic Information',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _nameController,
              decoration: const InputDecoration(
                labelText: 'Agent Name *',
                hintText: 'e.g., Emma, Assistant, Buddy',
                prefixIcon: Icon(Icons.person),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter agent name';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _descriptionController,
              decoration: const InputDecoration(
                labelText: 'Description *',
                hintText: 'Brief description of the agent',
                prefixIcon: Icon(Icons.description),
              ),
              maxLines: 3,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please enter description';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildCapabilitiesSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Capabilities',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            Text(
              'Select capabilities or add custom ones:',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey[400],
                  ),
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _predefinedCapabilities.map((capability) {
                final isSelected = _capabilities.contains(capability);
                return FilterChip(
                  label: Text(capability),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() {
                      if (selected) {
                        _capabilities.add(capability);
                      } else {
                        _capabilities.remove(capability);
                      }
                    });
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _capabilityController,
                    decoration: const InputDecoration(
                      labelText: 'Add custom capability',
                      hintText: 'e.g., Weather Updates',
                    ),
                  ),
                ),
                IconButton(
                  onPressed: _addCustomCapability,
                  icon: const Icon(Icons.add),
                ),
              ],
            ),
            if (_capabilities.isNotEmpty) ...[
              const SizedBox(height: 12),
              Text(
                'Selected Capabilities:',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                    ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _capabilities.map((capability) {
                  return Chip(
                    label: Text(capability),
                    deleteIcon: const Icon(Icons.close, size: 18),
                    onDeleted: () {
                      setState(() {
                        _capabilities.remove(capability);
                      });
                    },
                  );
                }).toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPersonalitySection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Personality',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _personalityController,
              decoration: const InputDecoration(
                labelText: 'Personality Description *',
                hintText:
                    'e.g., Friendly, helpful, and empathetic. Loves to solve problems...',
                prefixIcon: Icon(Icons.psychology),
              ),
              maxLines: 4,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Please describe the agent personality';
                }
                return null;
              },
            ),
          ],
        ),
      ),
    );
  }

  void _addCustomCapability() {
    final capability = _capabilityController.text.trim();
    if (capability.isNotEmpty && !_capabilities.contains(capability)) {
      setState(() {
        _capabilities.add(capability);
        _capabilityController.clear();
      });
    }
  }

  void _saveAgent() {
    if (_formKey.currentState!.validate()) {
      if (_capabilities.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select at least one capability'),
          ),
        );
        return;
      }

      final agent = Agent(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        name: _nameController.text.trim(),
        description: _descriptionController.text.trim(),
        personality: _personalityController.text.trim(),
        avatarUrl: _avatarUrlController.text.trim().isNotEmpty
            ? _avatarUrlController.text.trim()
            : null,
        capabilities: _capabilities,
        isActive: true,
      );

      // TODO: Send agent to backend
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Agent "${agent.name}" created successfully!'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }
}
