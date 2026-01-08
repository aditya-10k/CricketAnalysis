part of 'player_info_bloc.dart';

abstract class PlayerInfoState extends Equatable {
  const PlayerInfoState();

  @override
  List<Object> get props => [];
}

class PlayerInfoInitial extends PlayerInfoState {}

class PlayerInfoLoading extends PlayerInfoState {}

class PlayerInfoLoaded extends PlayerInfoState {
  final PlayerInfo playerInfo;

  const PlayerInfoLoaded({required this.playerInfo});

  @override
  List<Object> get props => [playerInfo];
}

class PlayerInfoError extends PlayerInfoState {
  final String message;

  const PlayerInfoError({required this.message});

  @override
  List<Object> get props => [message];
}
