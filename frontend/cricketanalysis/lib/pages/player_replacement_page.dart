import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';
import 'package:go_router/go_router.dart';

import '../bloc/player_replacement/player_replacement_bloc.dart';
import '../bloc/players/players_bloc.dart';
import '../models/player_replacement.dart';

const _accentColor = Color(0xFFC63A2E);

class PlayerReplacementPage extends StatefulWidget {
  const PlayerReplacementPage({super.key});

  @override
  State<PlayerReplacementPage> createState() => _PlayerReplacementPageState();
}

class _PlayerReplacementPageState extends State<PlayerReplacementPage> {
  final TextEditingController _playerController = TextEditingController();
  final TextEditingController _nationalityController = TextEditingController();
  final TextEditingController _topNController = TextEditingController(text: '10');
  final List<String> _excludePlayers = [];
  bool _considerForm = true;

  @override
  void dispose() {
    _playerController.dispose();
    _nationalityController.dispose();
    _topNController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width <= 900;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          // Header
          Container(
            height: 64,
            decoration: const BoxDecoration(
              color: Colors.white,
              border: Border(
                bottom: BorderSide(color: Colors.black12, width: 1),
              ),
            ),
            child: Center(
              child: Container(
                constraints: const BoxConstraints(maxWidth: 1400),
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Row(
                  children: [
                    if (isMobile)
                      IconButton(
                        icon: const Icon(Icons.arrow_back, color: Colors.black87),
                        onPressed: () {
                          if (context.canPop()) {
                            context.pop();
                          } else {
                            context.go('/');
                          }
                        },
                      ),
                    if (isMobile) const SizedBox(width: 8),
                    Image.asset("assets/image-removebg-preview.png", height: 60,),
                    SizedBox(width: 20,),
                    const Text(
                      '12th Man',
                      style: TextStyle(
                        color: Colors.black87,
                        fontWeight: FontWeight.w600,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          Expanded(
            child: BlocBuilder<PlayersBloc, PlayersState>(
              builder: (context, playersState) {
                if (playersState is PlayersLoaded) {
                  if (isMobile) {
                    return SingleChildScrollView(
                      child: Padding(
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          children: [
                            _buildSelectionPanel(playersState, isMobile: true),
                            const SizedBox(height: 40),
                            const Divider(),
                            const SizedBox(height: 20),
                            SizedBox(
                              height: 600, // Fixed height for results on mobile to allow scrolling inside or use PrimaryScrollController
                              child: _buildResultsPanel(),
                            ),
                          ],
                        ),
                      ),
                    );
                  } else {
                    return Center(
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 1400),
                        padding: const EdgeInsets.all(40),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(
                              width: 400,
                              child: _buildSelectionPanel(playersState),
                            ),
                            const SizedBox(width: 40),
                            Expanded(
                              child: _buildResultsPanel(),
                            ),
                          ],
                        ),
                      ),
                    );
                  }
                } else if (playersState is PlayersError) {
                  return Center(
                    child: Text(
                      playersState.message,
                      style: const TextStyle(color: _accentColor),
                    ),
                  );
                }
                return const Center(child: CircularProgressIndicator(color: _accentColor));
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSelectionPanel(PlayersLoaded playersState, {bool isMobile = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      mainAxisSize: isMobile ? MainAxisSize.min : MainAxisSize.max,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Find Replacement',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
                color: Colors.black87,
              ),
            ),
             if (isMobile)
              IconButton(onPressed: (){}, icon: Icon(Icons.expand_more)) // Optional: Could minimize
          ],
        ),
        const SizedBox(height: 24),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _playerController.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Player to Replace',
                labelStyle: const TextStyle(color: Colors.black54),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(4),
                  borderSide: const BorderSide(color: Colors.black12),
                ),
                enabledBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(4),
                  borderSide: const BorderSide(color: Colors.black12),
                ),
                focusedBorder: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(4),
                  borderSide: const BorderSide(color: _accentColor, width: 1.5),
                ),
                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
              ),
              onChanged: (value) => _playerController.text = value,
            );
          },
           suggestionsCallback: (pattern) => playersState.players
               .where((player) => player.player.toLowerCase().contains(pattern.toLowerCase()))
               .map((player) => player.player)
               .toList(),
           itemBuilder: (context, suggestion) => ListTile(
             dense: true,
             title: Text(suggestion, style: const TextStyle(fontSize: 14)),
           ),
           onSelected: (suggestion) {
             setState(() {
               _playerController.text = suggestion;
             });
           },
         ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: TextField(
                controller: _nationalityController,
                decoration: InputDecoration(
                  labelText: 'Nationality',
                  labelStyle: const TextStyle(color: Colors.black54),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: Colors.black12),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: Colors.black12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: _accentColor, width: 1.5),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                ),
              ),
            ),
            const SizedBox(width: 12),
            SizedBox(
              width: 100,
              child: TextField(
                controller: _topNController,
                decoration: InputDecoration(
                  labelText: 'Top N',
                  labelStyle: const TextStyle(color: Colors.black54),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: Colors.black12),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: Colors.black12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(4),
                    borderSide: const BorderSide(color: _accentColor, width: 1.5),
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                ),
                keyboardType: TextInputType.number,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Checkbox(
              value: _considerForm,
              onChanged: (value) => setState(() => _considerForm = value ?? true),
              activeColor: _accentColor,
            ),
            const Text(
              'Consider Form',
              style: TextStyle(fontSize: 14, color: Colors.black87),
            ),
          ],
        ),
        const SizedBox(height: 24),
        const Text(
          'Exclude Players',
          style: TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w500,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 12),
        _buildExcludePlayersField(),
        if (isMobile) const SizedBox(height: 24) else const Spacer(),
        ElevatedButton(
          onPressed: _findReplacement,
          style: ElevatedButton.styleFrom(
            backgroundColor: _accentColor,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          child: const Text('Find Replacements', style: TextStyle(fontSize: 15)),
        ),
      ],
    );
  }

  Widget _buildResultsPanel() {
    return BlocBuilder<PlayerReplacementBloc, PlayerReplacementState>(
      builder: (context, state) {
        if (state is PlayerReplacementInitial) {
          return const Center(
            child: Text(
              'Search for replacements to view results',
              style: TextStyle(fontSize: 15, color: Colors.black38),
            ),
          );
        }
        if (state is PlayerReplacementLoading) {
          return const Center(child: CircularProgressIndicator(color: _accentColor));
        }
        if (state is PlayerReplacementError) {
          return Center(
            child: Text(
              _cleanError(state.message),
              style: const TextStyle(color: _accentColor),
            ),
          );
        }
        if (state is PlayerReplacementLoaded) {
          return _buildResultsList(state.response);
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildResultsList(PlayerReplacementResponse response) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${response.replacements.length} Results',
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 24),
        Expanded(
          child: ListView.separated(
            itemCount: response.replacements.length,
            separatorBuilder: (context, index) => const Divider(height: 1, color: Colors.black12),
            itemBuilder: (context, index) => _buildPlayerCard(response.replacements[index], index),
          ),
        ),
      ],
    );
  }

  Widget _buildPlayerCard(ReplacementPlayer replacement, int index) {
    return InkWell(
      onTap: () => _showPlayerDetailsDialog(context, replacement),
      hoverColor: Colors.black.withOpacity(0.02),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 20),
        child: Row(
          children: [
            SizedBox(
              width: 40,
              child: Text(
                '${index + 1}',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w500,
                  color: Colors.black38,
                ),
              ),
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    replacement.player,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Text(
                    '${replacement.role} · ${replacement.nationality}',
                    style: const TextStyle(
                      fontSize: 13,
                      color: Colors.black54,
                    ),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  replacement.finalValue.toStringAsFixed(3),
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w600,
                    color: Colors.black87,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${(replacement.similarityScore * 100).toStringAsFixed(1)}% match',
                  style: const TextStyle(
                    fontSize: 13,
                    color: Colors.black54,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExcludePlayersField() {
    return Column(
      children: [
        TypeAheadField<String>(
          builder: (context, controller, focusNode) => TextField(
            controller: controller,
            focusNode: focusNode,
            decoration: InputDecoration(
              hintText: 'Add player to exclude',
              hintStyle: const TextStyle(color: Colors.black38),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(4),
                borderSide: const BorderSide(color: Colors.black12),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(4),
                borderSide: const BorderSide(color: Colors.black12),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(4),
                borderSide: const BorderSide(color: _accentColor, width: 1.5),
              ),
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
            ),
          ),
          suggestionsCallback: (pattern) {
            final state = context.read<PlayersBloc>().state;
            if (state is PlayersLoaded) {
              return state.players
                  .where((player) => player.player.toLowerCase().contains(pattern.toLowerCase()))
                  .map((player) => player.player)
                  .where((name) => !_excludePlayers.contains(name))
                  .toList();
            }
            return [];
          },
          itemBuilder: (context, suggestion) => ListTile(
            dense: true,
            title: Text(suggestion, style: const TextStyle(fontSize: 14)),
          ),
          onSelected: (suggestion) {
            setState(() => _excludePlayers.add(suggestion));
          },
        ),
        if (_excludePlayers.isNotEmpty) ...[
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _excludePlayers.map((player) => Chip(
              label: Text(player, style: const TextStyle(fontSize: 13)),
              deleteIcon: const Icon(Icons.close, size: 16),
              onDeleted: () => setState(() => _excludePlayers.remove(player)),
              backgroundColor: Colors.black12,
            )).toList(),
          ),
        ],
      ],
    );
  }

  void _showPlayerDetailsDialog(BuildContext context, ReplacementPlayer replacement) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        backgroundColor: Colors.white,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(4),
        ),
        child: Container(
          constraints: const BoxConstraints(maxWidth: 600),
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          replacement.player,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${replacement.role} · ${replacement.nationality}',
                          style: const TextStyle(
                            fontSize: 15,
                            color: Colors.black54,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.close, color: Colors.black54),
                  ),
                ],
              ),
              const SizedBox(height: 32),
              _buildDetailRow('Final Value', replacement.finalValue.toStringAsFixed(4)),
              _buildDetailRow('Similarity Score', '${(replacement.similarityScore * 100).toStringAsFixed(1)}%'),
              _buildDetailRow('Career Value', replacement.careerValue.toStringAsFixed(4)),
              _buildDetailRow('Confidence', '${(replacement.confidence * 100).toStringAsFixed(0)}%'),
               _buildDetailRow('Days Since Last Match', '${replacement.daysSinceLastMatch}'),
               if (replacement.explanation.isNotEmpty) ...[
                 const SizedBox(height: 24),
                 const Text(
                   'Explanation',
                   style: TextStyle(
                     fontSize: 15,
                     fontWeight: FontWeight.w600,
                     color: _accentColor,
                   ),
                 ),
                 const SizedBox(height: 12),
                 Text(
                   replacement.explanation,
                   style: const TextStyle(
                     fontSize: 14,
                     color: Colors.black87,
                     height: 1.5,
                   ),
                 ),
               ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.black54,
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: Colors.black87,
            ),
          ),
        ],
      ),
    );
  }

  void _findReplacement() {
    if (_playerController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select a player'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }
    final request = PlayerReplacementRequest(
      player: _playerController.text.trim(),
      nationalityFilter: _nationalityController.text.trim().isEmpty ? null : _nationalityController.text.trim(),
      excludePlayers: _excludePlayers,
      topN: int.tryParse(_topNController.text) ?? 10,
      considerForm: _considerForm,
    );
    context.read<PlayerReplacementBloc>().add(FindPlayerReplacement(request));
  }

  String _cleanError(String message) {
    return message.replaceFirst(RegExp(r'^Exception:\\s*'), '');
  }
}
