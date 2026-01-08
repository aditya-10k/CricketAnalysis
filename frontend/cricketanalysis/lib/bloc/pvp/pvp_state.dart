part of 'pvp_bloc.dart';

abstract class PvpState extends Equatable {
  const PvpState();

  @override
  List<Object> get props => [];
}

class PvpInitial extends PvpState {}

class PvpLoading extends PvpState {}

class PvpLoaded extends PvpState {
  final PvpResponse response;

  const PvpLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class PvpError extends PvpState {
  final String message;

  const PvpError({required this.message});

  @override
  List<Object> get props => [message];
}
