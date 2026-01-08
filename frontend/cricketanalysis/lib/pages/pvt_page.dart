import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/pvt/pvt_bloc.dart';
import '../bloc/players/players_bloc.dart';
import '../bloc/teams/teams_bloc.dart';
import '../models/pvt.dart';

const _accentColor = Color(0xFFC63A2E);

class PvtPage extends StatefulWidget {
  const PvtPage({super.key});

  @override
  State<PvtPage> createState() => _PvtPageState();
}

class _PvtPageState extends State<PvtPage> {
  final TextEditingController _playerController = TextEditingController();
  final TextEditingController _teamController = TextEditingController();
  final TextEditingController _venueController = TextEditingController();
  String _mode = 'batting'; // 'batting' or 'bowling'
  String _phase = 'all';

  @override
  void dispose() {
    _playerController.dispose();
    _teamController.dispose();
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
                      'Player vs Team',
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
                return BlocBuilder<TeamsBloc, TeamsState>(
                  builder: (context, teamsState) {
                    if (playersState is PlayersLoaded && teamsState is TeamsLoaded) {
                      return Center(
                        child: Container(
                          constraints: const BoxConstraints(maxWidth: 1200),
                          padding: const EdgeInsets.all(40),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              SizedBox(
                                width: 400,
                                child: _buildForm(playersState, teamsState),
                              ),
                              const SizedBox(width: 40),
                              Expanded(
                                child: _buildResults(),
                              ),
                            ],
                          ),
                        ),
                      );
                    } else if (playersState is PlayersError || teamsState is TeamsError) {
                      return Center(
                        child: Text(
                          playersState is PlayersError ? playersState.message : (teamsState as TeamsError).message,
                          style: const TextStyle(color: _accentColor),
                        ),
                      );
                    }
                    return const Center(child: CircularProgressIndicator(color: _accentColor));
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForm(PlayersLoaded playersState, TeamsLoaded teamsState) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text(
          'Performance Analysis',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        const SizedBox(height: 24),
        SegmentedButton<String>(
          segments: const [
            ButtonSegment(value: 'batting', label: Text('Batting')),
            ButtonSegment(value: 'bowling', label: Text('Bowling')),
          ],
          selected: {_mode},
          onSelectionChanged: (Set<String> newSelection) {
            setState(() {
              _mode = newSelection.first;
            });
          },
          style: ButtonStyle(
            backgroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return _accentColor;
              }
              return Colors.transparent;
            }),
            foregroundColor: WidgetStateProperty.resolveWith((states) {
              if (states.contains(WidgetState.selected)) {
                return Colors.white;
              }
              return Colors.black87;
            }),
          ),
        ),
        const SizedBox(height: 24),
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _playerController.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: _mode == 'batting' ? 'Batter' : 'Bowler',
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
        TypeAheadField<String>(
          builder: (context, controller, focusNode) {
            controller.text = _teamController.text;
            return TextField(
              controller: controller,
              focusNode: focusNode,
              decoration: InputDecoration(
                labelText: 'Team',
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
              onChanged: (value) => _teamController.text = value,
            );
          },
          suggestionsCallback: (pattern) => teamsState.teams
              .where((team) => team.toLowerCase().contains(pattern.toLowerCase()))
              .toList(),
          itemBuilder: (context, suggestion) => ListTile(
            dense: true,
            title: Text(suggestion, style: const TextStyle(fontSize: 14)),
          ),
          onSelected: (suggestion) {
            setState(() {
              _teamController.text = suggestion;
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
        DropdownButtonFormField<String>(
          value: _phase,
          decoration: InputDecoration(
            labelText: 'Phase',
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
          items: const [
            DropdownMenuItem(value: 'all', child: Text('All')),
            DropdownMenuItem(value: 'powerplay', child: Text('Powerplay')),
            DropdownMenuItem(value: 'middle', child: Text('Middle')),
            DropdownMenuItem(value: 'death', child: Text('Death')),
          ],
          onChanged: (value) {
            setState(() {
              _phase = value ?? 'all';
            });
          },
        ),
        const Spacer(),
        ElevatedButton(
          onPressed: _getPerformance,
          style: ElevatedButton.styleFrom(
            backgroundColor: _accentColor,
            foregroundColor: Colors.white,
            elevation: 0,
            padding: const EdgeInsets.symmetric(vertical: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          child: const Text('Get Performance', style: TextStyle(fontSize: 15)),
        ),
      ],
    );
  }

  Widget _buildResults() {
    return BlocBuilder<PvtBloc, PvtState>(
      builder: (context, state) {
        if (state is PvtInitial) {
          return const Center(
            child: Text(
              'Enter player and team to get performance',
              style: TextStyle(fontSize: 15, color: Colors.black38),
            ),
          );
        }
        if (state is PvtLoading) {
          return const Center(child: CircularProgressIndicator(color: _accentColor));
        }
        if (state is PvtError) {
          return Center(
            child: Text(
              _cleanError(state.message),
              style: const TextStyle(color: _accentColor),
            ),
          );
        }
        if (state is PvtBatterLoaded) {
          return _buildBatterResults(state.response);
        }
        if (state is PvtBowlerLoaded) {
          return _buildBowlerResults(state.response);
        }
        return const SizedBox();
      },
    );
  }

  Widget _buildBatterResults(PvtBatterResponse response) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${response.batter} vs ${response.team}',
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
          _buildSectionHeader('Performance'),
          const SizedBox(height: 16),
          _buildInfoRow('Innings Played', response.performance.inningsPlayed?.toString() ?? 'N/A'),
          _buildInfoRow('Runs Scored', response.performance.runsScored.toString()),
          _buildInfoRow('Balls Faced', response.performance.ballsFaced.toString()),
          _buildInfoRow('Dismissals', response.performance.dismissals.toString()),
          _buildInfoRow('Average', response.performance.average.toStringAsFixed(2)),
          _buildInfoRow('Strike Rate', response.performance.strikeRate.toStringAsFixed(2)),
          _buildInfoRow('Boundary Percentage', '${response.performance.boundaryPercentage.toStringAsFixed(2)}%'),
          _buildInfoRow('Avg RPA', response.performance.avgRpa.toStringAsFixed(4)),
          _buildInfoRow('Avg WPA', response.performance.avgWpa.toStringAsFixed(4)),
          _buildInfoRow('Performance Rating', response.performance.performanceRating),
          const SizedBox(height: 24),
          _buildInfoRow('Confidence', response.confidence),
        ],
      ),
    );
  }

  Widget _buildBowlerResults(PvtBowlerResponse response) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            '${response.bowler} vs ${response.team}',
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
          _buildSectionHeader('Performance'),
          const SizedBox(height: 16),
          _buildInfoRow('Innings Bowled', response.performance.inningsBowled?.toString() ?? 'N/A'),
          _buildInfoRow('Balls Bowled', response.performance.ballsBowled?.toString() ?? 'N/A'),
          _buildInfoRow('Runs Conceded', response.performance.runsConceded?.toString() ?? 'N/A'),
          _buildInfoRow('Wickets', response.performance.wickets?.toString() ?? 'N/A'),
          _buildInfoRow('Economy', response.performance.economy?.toStringAsFixed(2) ?? 'N/A'),
          _buildInfoRow('Strike Rate', response.performance.strikeRate.toStringAsFixed(2)),
          _buildInfoRow('Average', response.performance.average.toStringAsFixed(2)),
          _buildInfoRow('Dot Ball Percentage', response.performance.dotBallPercentage?.toStringAsFixed(2) ?? 'N/A'),
          _buildInfoRow('Avg RPA', response.performance.avgRpa.toStringAsFixed(4)),
          _buildInfoRow('Avg WPA', response.performance.avgWpa.toStringAsFixed(4)),
          _buildInfoRow('Performance Rating', response.performance.performanceRating),
          const SizedBox(height: 24),
          _buildInfoRow('Confidence', response.confidence),
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

  void _getPerformance() {
    if (_playerController.text.isEmpty || _teamController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select both player and team'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }

    if (_mode == 'batting') {
      final request = PvtBatterRequest(
        batter: _playerController.text.trim(),
        team: _teamController.text.trim(),
        venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
        phase: _phase,
      );
      context.read<PvtBloc>().add(LoadPvtBatter(request));
    } else {
      final request = PvtBowlerRequest(
        bowler: _playerController.text.trim(),
        team: _teamController.text.trim(),
        venue: _venueController.text.trim().isEmpty ? null : _venueController.text.trim(),
        phase: _phase,
      );
      context.read<PvtBloc>().add(LoadPvtBowler(request));
    }
  }

  String _cleanError(String message) {
    return message.replaceFirst(RegExp(r'^Exception:\\s*'), '');
  }
}
