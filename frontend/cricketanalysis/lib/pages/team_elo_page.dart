import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/team_elo/team_elo_bloc.dart';
import '../bloc/teams/teams_bloc.dart';
import '../models/team_elo.dart';

const _accentColor = Color(0xFFC63A2E);

class TeamEloPage extends StatefulWidget {
  const TeamEloPage({super.key});

  @override
  State<TeamEloPage> createState() => _TeamEloPageState();
}

class _TeamEloPageState extends State<TeamEloPage> {
  final TextEditingController _teamController = TextEditingController();
  final List<TeamEloHistory> _loadedTeams = [];
  bool _isLoading = false;
  final List<Color> _teamColors = [
    _accentColor,
    Colors.blue,
    Colors.green,
    Colors.orange,
    Colors.purple,
    Colors.teal,
    Colors.pink,
    Colors.indigo,
  ];

  @override
  void dispose() {
    _teamController.dispose();
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
                child: Row(
                  children: [
                    const Text(
                      'Team ELO History',
                      style: TextStyle(
                        color: Colors.black87,
                        fontWeight: FontWeight.w600,
                        fontSize: 18,
                      ),
                    ),
                    const Spacer(),
                    BlocBuilder<TeamsBloc, TeamsState>(
                      builder: (context, teamsState) {
                        if (teamsState is TeamsLoaded) {
                          return SizedBox(
                            width: 300,
                            child: TypeAheadField<String>(
                              builder: (context, controller, focusNode) {
                                controller.text = _teamController.text;
                                return TextField(
                                  controller: controller,
                                  focusNode: focusNode,
                                  decoration: InputDecoration(
                                    hintText: 'Enter team name',
                                    hintStyle: const TextStyle(color: Colors.black38, fontSize: 14),
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
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                                    isDense: true,
                                  ),
                                  onChanged: (value) => _teamController.text = value,
                                );
                              },
                              suggestionsCallback: (pattern) {
                                return teamsState.teams
                                    .where((team) => team.toLowerCase().contains(pattern.toLowerCase()))
                                    .where((team) => !_loadedTeams.any((t) => t.team == team))
                                    .toList();
                              },
                              itemBuilder: (context, suggestion) {
                                return ListTile(
                                  dense: true,
                                  title: Text(suggestion, style: const TextStyle(fontSize: 14)),
                                );
                              },
                              onSelected: (suggestion) {
                                _teamController.text = suggestion;
                                _loadTeam(suggestion);
                              },
                            ),
                          );
                        }
                        return const SizedBox();
                      },
                    ),
                    const SizedBox(width: 12),
                    ElevatedButton(
                      onPressed: _isLoading
                          ? null
                          : () {
                              if (_teamController.text.isNotEmpty) {
                                _loadTeam(_teamController.text.trim());
                              }
                            },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _accentColor,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      child: _isLoading
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 2,
                              ),
                            )
                          : const Text('Add Team'),
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Content
          Expanded(
            child: BlocListener<TeamEloBloc, TeamEloState>(
              listener: (context, state) {
                if (state is TeamEloLoaded) {
                  setState(() {
                    _isLoading = false;
                    if (!_loadedTeams.any((t) => t.team == state.eloHistory.team)) {
                      _loadedTeams.add(state.eloHistory);
                    }
                  });
                  _teamController.clear();
                } else if (state is TeamEloError) {
                  setState(() {
                    _isLoading = false;
                  });
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(state.message),
                      backgroundColor: _accentColor,
                    ),
                  );
                } else if (state is TeamEloLoading) {
                  setState(() {
                    _isLoading = true;
                  });
                }
              },
              child: _loadedTeams.isEmpty
                  ? const Center(
                      child: Text(
                        'Add teams to view ELO history',
                        style: TextStyle(fontSize: 15, color: Colors.black38),
                      ),
                    )
                  : _buildMultiTeamChart(),
            ),
          ),
        ],
      ),
    );
  }

  void _loadTeam(String teamName) {
    // Check if team already loaded
    if (_loadedTeams.any((t) => t.team == teamName)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Team already added'),
          backgroundColor: _accentColor,
        ),
      );
      return;
    }
    context.read<TeamEloBloc>().add(LoadTeamElo(teamName));
  }

  Widget _buildMultiTeamChart() {
    return Center(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 1200),
        padding: const EdgeInsets.all(40),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: _loadedTeams.asMap().entries.map((entry) {
                      final index = entry.key;
                      final team = entry.value;
                      return Chip(
                        label: Text(
                          team.team,
                          style: TextStyle(
                            color: _teamColors[index % _teamColors.length],
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        backgroundColor: _teamColors[index % _teamColors.length].withOpacity(0.1),
                        deleteIcon: Icon(
                          Icons.close,
                          size: 18,
                          color: _teamColors[index % _teamColors.length],
                        ),
                        onDeleted: () {
                          setState(() {
                            _loadedTeams.removeAt(index);
                          });
                        },
                      );
                    }).toList(),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 40),
            Expanded(
              child: _buildChart(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildChart() {
    if (_loadedTeams.isEmpty) {
      return const Center(child: Text('No teams loaded'));
    }

    // Find common date range
    final allDates = <String>{};
    for (var team in _loadedTeams) {
      for (var point in team.eloHistory) {
        allDates.add(point.date);
      }
    }
    final sortedDates = allDates.toList()..sort();

    if (sortedDates.isEmpty) {
      return const Center(child: Text('No date data available'));
    }

    // Build spots for each team
    final lineBarsData = <LineChartBarData>[];
    double minY = double.infinity;
    double maxY = double.negativeInfinity;

    for (int teamIndex = 0; teamIndex < _loadedTeams.length; teamIndex++) {
      final team = _loadedTeams[teamIndex];
      final spots = <FlSpot>[];
      final teamDateMap = <String, double>{};
      
      for (var point in team.eloHistory) {
        teamDateMap[point.date] = point.elo;
      }

      for (int i = 0; i < sortedDates.length; i++) {
        final date = sortedDates[i];
        final elo = teamDateMap[date];
        if (elo != null) {
          spots.add(FlSpot(i.toDouble(), elo));
          if (elo < minY) minY = elo;
          if (elo > maxY) maxY = elo;
        }
      }

      if (spots.isNotEmpty) {
        lineBarsData.add(
          LineChartBarData(
            spots: spots,
            isCurved: true,
            color: _teamColors[teamIndex % _teamColors.length],
            barWidth: 2,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(
              show: false,
            ),
          ),
        );
      }
    }

    if (minY == double.infinity || lineBarsData.isEmpty) {
      return const Center(child: Text('No valid ELO data'));
    }

    minY -= 50;
    maxY += 50;

    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 50,
          getDrawingHorizontalLine: (value) {
            return FlLine(
              color: Colors.black12,
              strokeWidth: 1,
            );
          },
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          topTitles: const AxisTitles(
            sideTitles: SideTitles(showTitles: false),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              interval: (sortedDates.length / 10).ceil().toDouble().clamp(1, double.infinity),
              getTitlesWidget: (value, meta) {
                final index = value.toInt();
                if (index >= 0 && index < sortedDates.length) {
                  final date = sortedDates[index];
                  return Padding(
                    padding: const EdgeInsets.only(top: 8.0),
                    child: Text(
                      date.split('-')[0],
                      style: const TextStyle(
                        fontSize: 11,
                        color: Colors.black54,
                      ),
                    ),
                  );
                }
                return const Text('');
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 50,
              getTitlesWidget: (value, meta) {
                return Text(
                  value.toInt().toString(),
                  style: const TextStyle(
                    fontSize: 11,
                    color: Colors.black54,
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(
          show: true,
          border: const Border(
            left: BorderSide(color: Colors.black12),
            bottom: BorderSide(color: Colors.black12),
          ),
        ),
        lineBarsData: lineBarsData,
        minY: minY,
        maxY: maxY,
      ),
    );
  }
}
