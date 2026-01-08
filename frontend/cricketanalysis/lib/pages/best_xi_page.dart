import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/best_xi/best_xi_bloc.dart';
import '../bloc/players/players_bloc.dart';
import '../models/best_xi.dart';

const _accentColor = Color(0xFFC63A2E);

class BestXiPage extends StatefulWidget {
  const BestXiPage({super.key});

  @override
  State<BestXiPage> createState() => _BestXiPageState();
}

class _BestXiPageState extends State<BestXiPage> {
  final TextEditingController _homeController = TextEditingController();
  final TextEditingController _awayController = TextEditingController();
  final TextEditingController _venueController = TextEditingController();
  final TextEditingController _maxOverseasController = TextEditingController(text: '0');
  final TextEditingController _minBowlersController = TextEditingController(text: '4');
  final TextEditingController _minBattersController = TextEditingController(text: '5');
  final TextEditingController _minConfidenceController = TextEditingController(text: '0.3');

  final List<String> _homeSquad = [];
  final List<String> _awaySquad = [];

  @override
  void dispose() {
    _homeController.dispose();
    _awayController.dispose();
    _venueController.dispose();
    _maxOverseasController.dispose();
    _minBowlersController.dispose();
    _minBattersController.dispose();
    _minConfidenceController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
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
                constraints: const BoxConstraints(maxWidth: 1200),
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child:  Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
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
                  return Center(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 1200),
                      padding: const EdgeInsets.all(40),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          SizedBox(
                            width: 450,
                            child: _buildForm(playersState),
                          ),
                          const SizedBox(width: 40),
                          Expanded(child: _buildResults()),
                        ],
                      ),
                    ),
                  );
                } else if (playersState is PlayersError) {
                  return Center(
                    child: Text(playersState.message, style: const TextStyle(color: _accentColor)),
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

  Widget _buildForm(PlayersLoaded playersState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Best XI - Squads & Constraints',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.black87),
        ),
        const SizedBox(height: 24),
        Expanded(
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                _buildSquadSelector(
                  label: 'Home Squad',
                  controller: _homeController,
                  squad: _homeSquad,
                  playersState: playersState,
                  onAdd: (p) => setState(() => _homeSquad.add(p)),
                  onRemove: (p) => setState(() => _homeSquad.remove(p)),
                ),
                const SizedBox(height: 16),
                _buildSquadSelector(
                  label: 'Away Squad',
                  controller: _awayController,
                  squad: _awaySquad,
                  playersState: playersState,
                  onAdd: (p) => setState(() => _awaySquad.add(p)),
                  onRemove: (p) => setState(() => _awaySquad.remove(p)),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _venueController,
                  decoration: _inputDecoration('Venue (Optional)'),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _maxOverseasController,
                        decoration: _inputDecoration('Max Overseas'),
                        keyboardType: TextInputType.number,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: _minBowlersController,
                        decoration: _inputDecoration('Min Bowlers'),
                        keyboardType: TextInputType.number,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _minBattersController,
                        decoration: _inputDecoration('Min Batters'),
                        keyboardType: TextInputType.number,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: _minConfidenceController,
                        decoration: _inputDecoration('Min Confidence (0-1)'),
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),
        ElevatedButton(
          onPressed: _runOptimizer,
          style: ElevatedButton.styleFrom(
            backgroundColor: _accentColor,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
          ),
          child: const Text('Optimize XI', style: TextStyle(fontSize: 15)),
        ),
      ],
    );
  }

  Widget _buildSquadSelector({
    required String label,
    required TextEditingController controller,
    required List<String> squad,
    required PlayersLoaded playersState,
    required void Function(String) onAdd,
    required void Function(String) onRemove,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.black87),
        ),
        const SizedBox(height: 8),
        TypeAheadField<String>(
          builder: (context, typeAheadController, focusNode) {
            typeAheadController.text = controller.text;
            return TextField(
              controller: typeAheadController,
              focusNode: focusNode,
              decoration: _inputDecoration('Add player'),
              onChanged: (v) => controller.text = v,
            );
          },
          suggestionsCallback: (pattern) => playersState.players
              .where((p) => p.player.toLowerCase().contains(pattern.toLowerCase()))
              .map((p) => p.player)
              .where((p) => !squad.contains(p))
              .toList(),
          itemBuilder: (context, suggestion) => ListTile(
            dense: true,
            title: Text(suggestion, style: const TextStyle(fontSize: 14)),
          ),
          onSelected: (suggestion) {
            controller.clear();
            onAdd(suggestion);
          },
        ),
        const SizedBox(height: 8),
        if (squad.isNotEmpty)
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: squad
                .map(
                  (p) => Chip(
                    label: Text(p, style: const TextStyle(fontSize: 13)),
                    deleteIcon: const Icon(Icons.close, size: 16),
                    onDeleted: () => onRemove(p),
                    backgroundColor: Colors.black12,
                  ),
                )
                .toList(),
          ),
      ],
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
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
    );
  }

  Widget _buildResults() {
    return BlocBuilder<BestXiBloc, BestXiState>(
      builder: (context, state) {
        if (state is BestXiInitial) {
          return const Center(
            child: Text(
              'Add squads and run optimizer',
              style: TextStyle(fontSize: 15, color: Colors.black38),
            ),
          );
        }
        if (state is BestXiLoading) {
          return const Center(child: CircularProgressIndicator(color: _accentColor));
        }
        if (state is BestXiError) {
          return Center(
            child: Text(
              _cleanError(state.message),
              style: const TextStyle(color: _accentColor),
            ),
          );
        }
        if (state is BestXiLoaded) {
          return _buildTeam(state.response);
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildTeam(BestXiResponse response) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Optimized XI (${response.team.length} players)',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600, color: Colors.black87),
        ),
        const SizedBox(height: 12),
        Text(
          'Venue: ${response.venue}',
          style: const TextStyle(fontSize: 14, color: Colors.black54),
        ),
        const SizedBox(height: 16),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Text(
            'Team Value: ${response.teamTotalValue.toStringAsFixed(3)}   Synergy Bonus: ${response.teamSynergyBonus.toStringAsFixed(3)}   Matchup Advantage: ${response.teamMatchupAdvantage.toStringAsFixed(3)}',
            style: const TextStyle(fontSize: 13, color: Colors.black54),
          ),
        ),
        const SizedBox(height: 24),
        Expanded(
          child: ListView.separated(
            itemCount: response.team.length,
            separatorBuilder: (_, __) => const Divider(height: 1, color: Colors.black12),
            itemBuilder: (context, index) {
              final player = response.team[index];
              return InkWell(
                onTap: () => _showPlayerDetails(context, player),
                hoverColor: Colors.black.withOpacity(0.02),
                child: ListTile(
                  leading: Text(
                    '${index + 1}',
                    style: const TextStyle(fontSize: 14, color: Colors.black54),
                  ),
                  title: Text(
                    player.player,
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.black87),
                  ),
                  subtitle: Text(
                    '${player.role} · ${player.nationality}',
                    style: const TextStyle(fontSize: 13, color: Colors.black54),
                  ),
                  trailing: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      Text(
                        player.finalValue.toStringAsFixed(3),
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Colors.black87),
                      ),
                      Text(
                        'Confidence ${(player.confidence * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(fontSize: 12, color: Colors.black54),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  void _runOptimizer() {
    if (_homeSquad.isEmpty || _awaySquad.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Add players to both squads'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }

    final request = BestXiRequest(
      homeSquad: _homeSquad,
      awaySquad: _awaySquad,
      venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
      constraints: BestXiConstraints(
        maxOverseas: int.tryParse(_maxOverseasController.text) ?? 0,
        minBowlers: int.tryParse(_minBowlersController.text) ?? 0,
        minBatters: int.tryParse(_minBattersController.text) ?? 0,
        minConfidence: double.tryParse(_minConfidenceController.text) ?? 0,
      ),
    );

    context.read<BestXiBloc>().add(LoadBestXi(request));
  }

  String _cleanError(String message) {
    return message.replaceFirst(RegExp(r'^Exception:\\s*'), '');
  }

  void _showPlayerDetails(BuildContext context, BestXiPlayer player) {
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
                          player.player,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w600,
                            color: Colors.black87,
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          '${player.role} · ${player.nationality}',
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
              _buildSectionHeader('Value Metrics'),
              const SizedBox(height: 16),
              _buildDetailRow('Base Value', player.baseValue.toStringAsFixed(4)),
              _buildDetailRow('Form Value', player.formValue.toStringAsFixed(4)),
              _buildDetailRow('Combined Value', player.combinedValue.toStringAsFixed(4)),
              _buildDetailRow('Final Value', player.finalValue.toStringAsFixed(4)),
              _buildDetailRow('Matchup Adjustment', player.matchupAdjustment.toStringAsFixed(4)),
              _buildDetailRow('Synergy Bonus', player.synergyBonus.toStringAsFixed(4)),
              const SizedBox(height: 24),
              _buildSectionHeader('Performance Stats'),
              const SizedBox(height: 16),
              _buildDetailRow('Balls Faced', player.ballsFaced.toString()),
              _buildDetailRow('Balls Bowled', player.ballsBowled.toString()),
              _buildDetailRow('Days Since Last Match', player.daysSinceLastMatch.toString()),
              const SizedBox(height: 24),
              _buildSectionHeader('Confidence'),
              const SizedBox(height: 16),
              _buildDetailRow('Confidence', '${(player.confidence * 100).toStringAsFixed(1)}%'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w600,
        color: _accentColor,
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
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
}
