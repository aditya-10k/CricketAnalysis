part of 'player_replacement_bloc.dart';

abstract class PlayerReplacementEvent extends Equatable {
  const PlayerReplacementEvent();

  @override
  List<Object> get props => [];
}

class FindPlayerReplacement extends PlayerReplacementEvent {
  final PlayerReplacementRequest request;

  const FindPlayerReplacement(this.request);

  @override
  List<Object> get props => [request];
}

class ClearPlayerReplacement extends PlayerReplacementEvent {}
