part of 'teams_bloc.dart';

abstract class TeamsState extends Equatable {
  const TeamsState();

  @override
  List<Object> get props => [];
}

class TeamsInitial extends TeamsState {}

class TeamsLoading extends TeamsState {}

class TeamsLoaded extends TeamsState {
  final List<String> teams;

  const TeamsLoaded({required this.teams});

  @override
  List<Object> get props => [teams];
}

class TeamsError extends TeamsState {
  final String message;

  const TeamsError({required this.message});

  @override
  List<Object> get props => [message];
}
