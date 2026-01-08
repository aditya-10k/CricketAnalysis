part of 'team_elo_bloc.dart';

abstract class TeamEloState extends Equatable {
  const TeamEloState();

  @override
  List<Object> get props => [];
}

class TeamEloInitial extends TeamEloState {}

class TeamEloLoading extends TeamEloState {}

class TeamEloLoaded extends TeamEloState {
  final TeamEloHistory eloHistory;

  const TeamEloLoaded({required this.eloHistory});

  @override
  List<Object> get props => [eloHistory];
}

class TeamEloError extends TeamEloState {
  final String message;

  const TeamEloError({required this.message});

  @override
  List<Object> get props => [message];
}
