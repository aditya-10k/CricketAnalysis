part of 'pvt_bloc.dart';

abstract class PvtState extends Equatable {
  const PvtState();

  @override
  List<Object> get props => [];
}

class PvtInitial extends PvtState {}

class PvtLoading extends PvtState {}

class PvtBatterLoaded extends PvtState {
  final PvtBatterResponse response;

  const PvtBatterLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class PvtBowlerLoaded extends PvtState {
  final PvtBowlerResponse response;

  const PvtBowlerLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class PvtError extends PvtState {
  final String message;

  const PvtError({required this.message});

  @override
  List<Object> get props => [message];
}
