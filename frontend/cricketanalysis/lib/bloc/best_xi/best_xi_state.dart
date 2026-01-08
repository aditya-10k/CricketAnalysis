part of 'best_xi_bloc.dart';

abstract class BestXiState extends Equatable {
  const BestXiState();

  @override
  List<Object> get props => [];
}

class BestXiInitial extends BestXiState {}

class BestXiLoading extends BestXiState {}

class BestXiLoaded extends BestXiState {
  final BestXiResponse response;

  const BestXiLoaded({required this.response});

  @override
  List<Object> get props => [response];
}

class BestXiError extends BestXiState {
  final String message;

  const BestXiError({required this.message});

  @override
  List<Object> get props => [message];
}
