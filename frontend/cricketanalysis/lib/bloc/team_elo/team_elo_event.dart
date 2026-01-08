part of 'team_elo_bloc.dart';

abstract class TeamEloEvent extends Equatable {
  const TeamEloEvent();

  @override
  List<Object> get props => [];
}

class LoadTeamElo extends TeamEloEvent {
  final String teamName;

  const LoadTeamElo(this.teamName);

  @override
  List<Object> get props => [teamName];
}

class ClearTeamElo extends TeamEloEvent {}
