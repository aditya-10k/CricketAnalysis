part of 'best_xi_bloc.dart';

abstract class BestXiEvent extends Equatable {
  const BestXiEvent();

  @override
  List<Object> get props => [];
}

class LoadBestXi extends BestXiEvent {
  final BestXiRequest request;

  const LoadBestXi(this.request);

  @override
  List<Object> get props => [request];
}

class ClearBestXi extends BestXiEvent {}
