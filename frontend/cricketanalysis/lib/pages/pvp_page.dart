import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/pvp/pvp_bloc.dart';
import '../bloc/players/players_bloc.dart';
import '../models/pvp.dart';

const _accentColor = Color(0xFFC63A2E);

class PvpPage extends StatefulWidget {
  const PvpPage({super.key});

  @override
  State<PvpPage> createState() => _PvpPageState();
}

class _PvpPageState extends State<PvpPage> {
  final TextEditingController _batterController = TextEditingController();
  final TextEditingController _bowlerController = TextEditingController();
  final TextEditingController _venueController = TextEditingController();
  bool _recentMatchesOnly = false;

  @override
  void dispose() {
    _batterController.dispose();
    _bowlerController.dispose();
    _venueController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
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
                constraints: const BoxConstraints(maxWidth: 1200),
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: const Row(
                  children: [
                    Text(
                      'Player vs Player',
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
          // Content
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
                          Expanded(
                            child: _buildResults(),
                          ),
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
          'Matchup Prediction',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 24),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _batterController.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Batter',
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
              onChanged: (value) => _batterController.text = value,
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
              _batterController.text = suggestion;
            });
          },
        ),
        const SizedBox(height: 16),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _bowlerController.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Bowler',
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
              onChanged: (value) => _bowlerController.text = value,
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
              _bowlerController.text = suggestion;
            });
          },
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _venueController,
          decoration: InputDecoration(
            labelText: 'Venue (Optional)',
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
        const SizedBox(height: 16),
        Row(
          children: [
            Checkbox(
              value: _recentMatchesOnly,
              onChanged: (value) => setState(() => _recentMatchesOnly = value ?? false),
              activeColor: _accentColor,
            ),
            const Text(
              'Recent Matches Only',
              style: TextStyle(fontSize: 14, color: Colors.black87),
            ),
          ],
        ),
        const Spacer(),
        ElevatedButton(
          onPressed: _getPrediction,
          style: ElevatedButton.styleFrom(
            backgroundColor: _accentColor,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          child: const Text('Get Prediction', style: TextStyle(fontSize: 15)),
        ),
      ],
    );
  }

  Widget _buildResults() {
    return BlocBuilder<PvpBloc, PvpState>(
      builder: (context, state) {
        if (state is PvpInitial) {
          return const Center(
            child: Text(
              'Enter batter and bowler to get prediction',
              style: TextStyle(fontSize: 15, color: Colors.black38),
            ),
          );
        }
        if (state is PvpLoading) {
          return const Center(child: CircularProgressIndicator(color: _accentColor));
        }
        if (state is PvpError) {
          return Center(
            child: Text(
              _cleanError(state.message),
              style: const TextStyle(color: _accentColor),
            ),
          );
        }
        if (state is PvpLoaded) {
          return _buildPredictionResults(state.response);
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildPredictionResults(PvpResponse response) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${response.batter} vs ${response.bowler}',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.w600,
              color: Colors.black87,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Venue: ${response.venue}',
            style: const TextStyle(
              fontSize: 14,
              color: Colors.black54,
            ),
          ),
          const SizedBox(height: 40),
          _buildSectionHeader('Prediction'),
          const SizedBox(height: 16),
          _buildInfoRow('Winner', response.prediction.winner.toUpperCase()),
          _buildInfoRow('Expected Runs per Ball', response.prediction.expectedRunsPerBall.toStringAsFixed(3)),
          _buildInfoRow('Expected Dismissal Rate', '${(response.prediction.expectedDismissalRate * 100).toStringAsFixed(2)}%'),
          _buildInfoRow('Matchup Advantage', '${(response.prediction.matchupAdvantage * 100).toStringAsFixed(1)}%'),
          _buildInfoRow('Confidence', response.prediction.confidence),
          const SizedBox(height: 40),
          _buildSectionHeader('Historical Data'),
          const SizedBox(height: 16),
          _buildInfoRow('Balls Faced', response.historicalData.ballsFaced.toString()),
          _buildInfoRow('Runs Scored', response.historicalData.runsScored.toString()),
          _buildInfoRow('Dismissals', response.historicalData.dismissals.toString()),
          _buildInfoRow('Strike Rate', response.historicalData.strikeRate.toStringAsFixed(2)),
          _buildInfoRow('Average', response.historicalData.average.toStringAsFixed(2)),
          _buildInfoRow('Boundary Percentage', '${response.historicalData.boundaryPercentage.toStringAsFixed(2)}%'),
          const SizedBox(height: 40),
          _buildSectionHeader('Context'),
          const SizedBox(height: 16),
          _buildInfoRow('Batter Career Avg RPA', response.context.batterCareerAvgRpa.toStringAsFixed(3)),
          _buildInfoRow('Bowler Career Avg RPA', response.context.bowlerCareerAvgRpa.toStringAsFixed(3)),
          _buildInfoRow('Venue Factor', response.context.venueFactor.toStringAsFixed(3)),
          if (response.context.styleMatchup.isNotEmpty)
            _buildInfoRow('Style Matchup', response.context.styleMatchup.join(', ')),
          const SizedBox(height: 24),
          _buildInfoRow('Sample Quality', response.sampleQuality),
        ],
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

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 200,
            child: Text(
              label,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.black54,
              ),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                fontSize: 14,
                color: Colors.black87,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _getPrediction() {
    if (_batterController.text.isEmpty || _bowlerController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select both batter and bowler'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }

    final request = PvpRequest(
      batter: _batterController.text.trim(),
      bowler: _bowlerController.text.trim(),
      venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
      recentMatchesOnly: _recentMatchesOnly,
    );

    context.read<PvpBloc>().add(LoadPvpPrediction(request));
  }

  String _cleanError(String message) {
    return message.replaceFirst(RegExp(r'^Exception:\s*'), '');
  }
}
