part of 'pvp_bloc.dart';

abstract class PvpEvent extends Equatable {
  const PvpEvent();

  @override
  List<Object> get props => [];
}

class LoadPvpPrediction extends PvpEvent {
  final PvpRequest request;

  const LoadPvpPrediction(this.request);

  @override
  List<Object> get props => [request];
}

class ClearPvp extends PvpEvent {}
