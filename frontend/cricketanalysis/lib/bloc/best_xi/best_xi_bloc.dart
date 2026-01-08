import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/best_xi.dart';
import '../../services/api_service.dart';

part 'best_xi_event.dart';
part 'best_xi_state.dart';

class BestXiBloc extends Bloc<BestXiEvent, BestXiState> {
  final ApiService apiService;

  BestXiBloc({required this.apiService}) : super(BestXiInitial()) {
    on<LoadBestXi>(_onLoadBestXi);
    on<ClearBestXi>(_onClear);
  }

  Future<void> _onLoadBestXi(
    LoadBestXi event,
    Emitter<BestXiState> emit,
  ) async {
    emit(BestXiLoading());
    try {
      final response = await apiService.getBestXi(event.request);
      emit(BestXiLoaded(response: response));
    } catch (e) {
      emit(BestXiError(message: e.toString()));
    }
  }

  void _onClear(
    ClearBestXi event,
    Emitter<BestXiState> emit,
  ) {
    emit(BestXiInitial());
  }
}
