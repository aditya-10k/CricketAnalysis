part of 'synergy_bloc.dart';

abstract class SynergyState extends Equatable {
  const SynergyState();

  @override
  List<Object> get props => [];
}

class SynergyInitial extends SynergyState {}

class SynergyLoading extends SynergyState {}

class SynergyBattingLoaded extends SynergyState {
  final SynergyBattingResponse response;

  const SynergyBattingLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class SynergyBowlingLoaded extends SynergyState {
  final SynergyBowlingResponse response;

  const SynergyBowlingLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class SynergyError extends SynergyState {
  final String message;

  const SynergyError({required this.message});

  @override
  List<Object> get props => [message];
}
