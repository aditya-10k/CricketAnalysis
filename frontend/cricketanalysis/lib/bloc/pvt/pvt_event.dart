part of 'pvt_bloc.dart';

abstract class PvtEvent extends Equatable {
  const PvtEvent();

  @override
  List<Object> get props => [];
}

class LoadPvtBatter extends PvtEvent {
  final PvtBatterRequest request;

  const LoadPvtBatter(this.request);

  @override
  List<Object> get props => [request];
}

class LoadPvtBowler extends PvtEvent {
  final PvtBowlerRequest request;

  const LoadPvtBowler(this.request);

  @override
  List<Object> get props => [request];
}

class ClearPvt extends PvtEvent {}
