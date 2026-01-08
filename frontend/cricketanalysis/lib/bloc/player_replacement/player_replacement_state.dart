part of 'player_replacement_bloc.dart';

abstract class PlayerReplacementState extends Equatable {
  const PlayerReplacementState();

  @override
  List<Object> get props => [];
}

class PlayerReplacementInitial extends PlayerReplacementState {}

class PlayerReplacementLoading extends PlayerReplacementState {}

class PlayerReplacementLoaded extends PlayerReplacementState {
  final PlayerReplacementResponse response;

  const PlayerReplacementLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class PlayerReplacementError extends PlayerReplacementState {
  final String message;

  const PlayerReplacementError({required this.message});

  @override
  List<Object> get props => [message];
}
