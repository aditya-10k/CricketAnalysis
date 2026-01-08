part of 'players_bloc.dart';

abstract class PlayersState extends Equatable {
  const PlayersState();

  @override
  List<Object> get props => [];
}

class PlayersInitial extends PlayersState {}

class PlayersLoading extends PlayersState {}

class PlayersLoaded extends PlayersState {
  final List<Player> players;

  const PlayersLoaded({required this.players});

  @override
  List<Object> get props => [players];
}

class PlayersError extends PlayersState {
  final String message;

  const PlayersError({required this.message});

  @override
  List<Object> get props => [message];
}
