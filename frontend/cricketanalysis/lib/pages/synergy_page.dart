import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/players/players_bloc.dart';
import '../bloc/synergy/synergy_bloc.dart';
import '../models/synergy.dart';

const _accentColor = Color(0xFFC63A2E);

class SynergyPage extends StatefulWidget {
  const SynergyPage({super.key});

  @override
  State<SynergyPage> createState() => _SynergyPageState();
}

class _SynergyPageState extends State<SynergyPage> {
  String _mode = 'batting';
  final TextEditingController _player1Controller = TextEditingController();
  final TextEditingController _player2Controller = TextEditingController();
  final TextEditingController _venueController = TextEditingController();
  final TextEditingController _phaseController = TextEditingController();

  @override
  void dispose() {
    _player1Controller.dispose();
    _player2Controller.dispose();
    _venueController.dispose();
    _phaseController.dispose();
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
                child: const Row(
                  children: [
                    Text(
                      'Synergy',
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
                            width: 400,
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

  Widget _buildForm(PlayersLoaded playersState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Pair Synergy',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 16),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: 'batting', label: Text('Batting')),
            ButtonSegment(value: 'bowling', label: Text('Bowling')),
          ],
          selected: {_mode},
          onSelectionChanged: (selection) {
            setState(() {
              _mode = selection.first;
            });
          },
          style: ButtonStyle(
            backgroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) return _accentColor;
              return Colors.transparent;
            }),
            foregroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) return Colors.white;
              return Colors.black87;
            }),
          ),
        ),
        const SizedBox(height: 24),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _player1Controller.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: _inputDecoration(_mode == 'batting' ? 'Batter 1' : 'Bowler 1'),
              onChanged: (v) => _player1Controller.text = v,
            );
          },
          suggestionsCallback: (pattern) => playersState.players
              .where((p) => p.player.toLowerCase().contains(pattern.toLowerCase()))
              .map((p) => p.player)
              .toList(),
          itemBuilder: (context, suggestion) => ListTile(
            dense: true,
            title: Text(suggestion, style: const TextStyle(fontSize: 14)),
          ),
          onSelected: (suggestion) => setState(() => _player1Controller.text = suggestion),
        ),
        const SizedBox(height: 16),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _player2Controller.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: _inputDecoration(_mode == 'batting' ? 'Batter 2' : 'Bowler 2'),
              onChanged: (v) => _player2Controller.text = v,
            );
          },
          suggestionsCallback: (pattern) => playersState.players
              .where((p) => p.player.toLowerCase().contains(pattern.toLowerCase()))
              .map((p) => p.player)
              .toList(),
          itemBuilder: (context, suggestion) => ListTile(
            dense: true,
            title: Text(suggestion, style: const TextStyle(fontSize: 14)),
          ),
          onSelected: (suggestion) => setState(() => _player2Controller.text = suggestion),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _venueController,
          decoration: _inputDecoration('Venue (Optional)'),
        ),
        const SizedBox(height: 16),
        if (_mode == 'bowling')
          TextField(
            controller: _phaseController,
            decoration: _inputDecoration('Phase (Optional)'),
          ),
        const Spacer(),
        ElevatedButton(
          onPressed: _getSynergy,
          style: ElevatedButton.styleFrom(
            backgroundColor: _accentColor,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
          ),
          child: const Text('Analyze Synergy', style: TextStyle(fontSize: 15)),
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
    return BlocBuilder<SynergyBloc, SynergyState>(
      builder: (context, state) {
        if (state is SynergyInitial) {
          return const Center(
            child: Text(
              'Select players to see synergy',
              style: TextStyle(fontSize: 15, color: Colors.black38),
            ),
          );
        }
        if (state is SynergyLoading) {
          return const Center(child: CircularProgressIndicator(color: _accentColor));
        }
        if (state is SynergyError) {
          return Center(
            child: Text(
              _cleanError(state.message),
              style: const TextStyle(color: _accentColor),
            ),
          );
        }
        if (state is SynergyBattingLoaded) {
          return _buildBattingResults(state.response);
        }
        if (state is SynergyBowlingLoaded) {
          return _buildBowlingResults(state.response);
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildBattingResults(SynergyBattingResponse response) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${response.batter1} & ${response.batter2}',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          _buildSectionHeader('Partnership'),
          _buildInfoRow('Innings Together', response.partnership.inningsTogether.toString()),
          _buildInfoRow('Partnership Runs', response.partnership.partnershipRuns.toString()),
          _buildInfoRow('Balls Together', response.partnership.ballsTogether.toString()),
          _buildInfoRow('Partnership Rate', response.partnership.partnershipRate.toStringAsFixed(2)),
          _buildInfoRow('Avg Partnership', response.partnership.avgPartnership.toStringAsFixed(2)),
          _buildInfoRow('Highest Partnership', response.partnership.highestPartnership.toString()),
          const SizedBox(height: 24),
          _buildSectionHeader('Synergy'),
          _buildInfoRow('Synergy Score', response.synergyAnalysis.synergyScore.toStringAsFixed(3)),
          _buildInfoRow('Rating', response.synergyAnalysis.rating),
          if (response.synergyAnalysis.explanation.isNotEmpty)
            _buildInfoRow('Explanation', response.synergyAnalysis.explanation),
          const SizedBox(height: 24),
          _buildSectionHeader('Individual (Together)'),
          _buildInfoRow('${response.batter1} SR', response.individualWhenTogether.batter1.strikeRate.toStringAsFixed(2)),
          _buildInfoRow('${response.batter2} SR', response.individualWhenTogether.batter2.strikeRate.toStringAsFixed(2)),
          const SizedBox(height: 24),
          _buildInfoRow('Sample Quality', response.sampleQuality),
          _buildInfoRow('Confidence', (response.confidence * 100).toStringAsFixed(0) + '%'),
        ],
      ),
    );
  }

  Widget _buildBowlingResults(SynergyBowlingResponse response) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${response.bowler1} & ${response.bowler2}',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 32),
          _buildSectionHeader('Combination'),
          _buildInfoRow('Matches Together', response.combination.matchesTogether.toString()),
          _buildInfoRow('Balls Together', response.combination.ballsTogether.toString()),
          _buildInfoRow('Combined Wickets', response.combination.combinedWickets.toString()),
          _buildInfoRow('Combined Economy', response.combination.combinedEconomy.toStringAsFixed(2)),
          _buildInfoRow('Partnership Strike Rate', response.combination.partnershipStrikeRate.toStringAsFixed(2)),
          _buildInfoRow('Dot Ball %', response.combination.dotBallPercentage.toStringAsFixed(2)),
          const SizedBox(height: 24),
          _buildSectionHeader('Synergy'),
          _buildInfoRow('Synergy Score', response.synergyAnalysis.synergyScore.toStringAsFixed(3)),
          _buildInfoRow('Rating', response.synergyAnalysis.rating),
          if (response.synergyAnalysis.explanation.isNotEmpty)
            _buildInfoRow('Explanation', response.synergyAnalysis.explanation),
          const SizedBox(height: 24),
          _buildSectionHeader('Wicket Partnership'),
          _buildInfoRow('Wicket Clustering', response.wicketPartnership.wicketClustering.toStringAsFixed(3)),
          const SizedBox(height: 24),
          _buildInfoRow('Sample Quality', response.sampleQuality),
          _buildInfoRow('Confidence', (response.confidence * 100).toStringAsFixed(0) + '%'),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0, top: 8.0),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: _accentColor,
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 220,
            child: Text(
              label,
              style: const TextStyle(fontSize: 14, color: Colors.black54),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(fontSize: 14, color: Colors.black87),
            ),
          ),
        ],
      ),
    );
  }

  void _getSynergy() {
    if (_player1Controller.text.isEmpty || _player2Controller.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select both players'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }

    if (_mode == 'batting') {
      final request = SynergyBattingRequest(
        batter1: _player1Controller.text.trim(),
        batter2: _player2Controller.text.trim(),
        venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
      );
      context.read<SynergyBloc>().add(LoadSynergyBatting(request));
    } else {
      final request = SynergyBowlingRequest(
        bowler1: _player1Controller.text.trim(),
        bowler2: _player2Controller.text.trim(),
        venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
        phase: _phaseController.text.trim().isEmpty ? null : _phaseController.text.trim(),
      );
      context.read<SynergyBloc>().add(LoadSynergyBowling(request));
    }
  }

  String _cleanError(String message) {
    return message.replaceFirst(RegExp(r'^Exception:\\s*'), '');
  }
}
