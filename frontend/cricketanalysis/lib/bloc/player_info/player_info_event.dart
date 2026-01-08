part of 'player_info_bloc.dart';

abstract class PlayerInfoEvent extends Equatable {
  const PlayerInfoEvent();

  @override
  List<Object> get props => [];
}

class LoadPlayerInfo extends PlayerInfoEvent {
  final String playerName;

  const LoadPlayerInfo(this.playerName);

  @override
  List<Object> get props => [playerName];
}

class ClearPlayerInfo extends PlayerInfoEvent {}
