part of 'synergy_bloc.dart';

abstract class SynergyEvent extends Equatable {
  const SynergyEvent();

  @override
  List<Object> get props => [];
}

class LoadSynergyBatting extends SynergyEvent {
  final SynergyBattingRequest request;

  const LoadSynergyBatting(this.request);

  @override
  List<Object> get props => [request];
}

class LoadSynergyBowling extends SynergyEvent {
  final SynergyBowlingRequest request;

  const LoadSynergyBowling(this.request);

  @override
  List<Object> get props => [request];
}

class ClearSynergy extends SynergyEvent {}
