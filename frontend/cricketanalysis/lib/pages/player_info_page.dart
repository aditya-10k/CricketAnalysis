import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:flutter_typeahead/flutter_typeahead.dart';

import '../bloc/player_info/player_info_bloc.dart';
import '../bloc/players/players_bloc.dart';

const _accentColor = Color(0xFFC63A2E);

class PlayerInfoPage extends StatelessWidget {
  const PlayerInfoPage({super.key});

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
          Text('Player Info', style: TextStyle(fontSize: 20 , fontWeight: FontWeight.bold),),
          // Content
          Expanded(
            child: BlocBuilder<PlayersBloc, PlayersState>(
              builder: (context, playersState) {
                if (playersState is PlayersLoaded) {
                  return Center(
                    child: Container(
                      constraints: const BoxConstraints(maxWidth: 1200),
                      padding: const EdgeInsets.symmetric(horizontal: 40),
                      child: Column(
                        children: [
                          const SizedBox(height: 40),
                          Container(
                            constraints: const BoxConstraints(maxWidth: 600),
                            child: TypeAheadField<String>(
                              builder: (context, controller, focusNode) {
                                return TextField(
                                  controller: controller,
                                  focusNode: focusNode,
                                  decoration: InputDecoration(
                                    hintText: 'Search player',
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
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                                  ),
                                );
                              },
                              suggestionsCallback: (pattern) {
                                return playersState.players
                                    .where((player) => player.player
                                        .toLowerCase()
                                        .contains(pattern.toLowerCase()))
                                    .map((player) => player.player)
                                    .toList();
                              },
                              itemBuilder: (context, suggestion) {
                                return ListTile(
                                  dense: true,
                                  title: Text(suggestion, style: const TextStyle(fontSize: 14)),
                                );
                              },
                              onSelected: (suggestion) {
                                context.read<PlayerInfoBloc>().add(LoadPlayerInfo(suggestion));
                              },
                            ),
                          ),
                          const SizedBox(height: 40),
                          Expanded(
                            child: BlocBuilder<PlayerInfoBloc, PlayerInfoState>(
                              builder: (context, state) {
                                if (state is PlayerInfoInitial) {
                                  return const Center(
                                    child: Text(
                                      'Search for a player to view details',
                                      style: TextStyle(fontSize: 15, color: Colors.black38),
                                    ),
                                  );
                                } else if (state is PlayerInfoLoading) {
                                  return const Center(
                                    child: CircularProgressIndicator(color: _accentColor),
                                  );
                                } else if (state is PlayerInfoError) {
                                  return Center(
                                    child: Text(
                                      state.message,
                                      style: const TextStyle(color: _accentColor, fontSize: 15),
                                      textAlign: TextAlign.center,
                                    ),
                                  );
                                } else if (state is PlayerInfoLoaded) {
                                  return _buildPlayerInfo(context, state.playerInfo);
                                }
                                return const SizedBox();
                              },
                            ),
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
                } else {
                  return const Center(child: CircularProgressIndicator(color: _accentColor));
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlayerInfo(BuildContext context, dynamic playerInfo) {
    return SingleChildScrollView(
      child: Container(
        constraints: const BoxConstraints(maxWidth: 900),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionHeader('Player'),
                  _buildInfoRow('Name', playerInfo.player),
                  _buildInfoRow('Role', playerInfo.role),
                  _buildInfoRow('Nationality', playerInfo.nationality),
                  const SizedBox(height: 32),
                  _buildSectionHeader('Styles'),
                  _buildInfoRow('Batting', playerInfo.styles.batting),
                  if (playerInfo.styles.bowling != null)
                    _buildInfoRow('Bowling', playerInfo.styles.bowling!),
                  const SizedBox(height: 32),
                  _buildSectionHeader('Career'),
                  _buildInfoRow('Total Value Z', playerInfo.career.totalValueZ.toStringAsFixed(3)),
                  _buildInfoRow('Final Value', playerInfo.career.finalValue.toStringAsFixed(3)),
                  _buildInfoRow('Confidence', playerInfo.career.confidence.toStringAsFixed(3)),
                  _buildInfoRow('Days Since Last Match', playerInfo.career.daysSinceLastMatch.toString()),
                ],
              ),
            ),
            const SizedBox(width: 80),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSectionHeader('Exposure'),
                  _buildInfoRow('Balls Faced', playerInfo.exposure.ballsFaced.toString()),
                  _buildInfoRow('Balls Bowled', playerInfo.exposure.ballsBowled.toString()),
                  _buildInfoRow('Runs Scored', playerInfo.exposure.runsScored.toString()),
                  _buildInfoRow('Wickets Taken', playerInfo.exposure.wicketsTaken.toString()),
                  const SizedBox(height: 32),
                  _buildSectionHeader('Batting Position'),
                  _buildInfoRow('Average', playerInfo.battingPosition.avg.toStringAsFixed(2)),
                  _buildInfoRow('Median', playerInfo.battingPosition.median.toStringAsFixed(2)),
                  _buildInfoRow('Innings', playerInfo.battingPosition.innings.toString()),
                  const SizedBox(height: 32),
                  _buildSectionHeader('Recent Form'),
                  _buildInfoRow('Form Z', playerInfo.recentForm.formZ.toStringAsFixed(3)),
                  _buildInfoRow('Confidence', playerInfo.recentForm.confidence.toStringAsFixed(3)),
                  _buildInfoRow('As Of', playerInfo.recentForm.asOf),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16.0),
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
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 180,
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
}
