import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/pvp.dart';
import '../../services/api_service.dart';

part 'pvp_event.dart';
part 'pvp_state.dart';

class PvpBloc extends Bloc<PvpEvent, PvpState> {
  final ApiService apiService;

  PvpBloc({required this.apiService}) : super(PvpInitial()) {
    on<LoadPvpPrediction>(_onLoadPvpPrediction);
    on<ClearPvp>(_onClearPvp);
  }

  Future<void> _onLoadPvpPrediction(
    LoadPvpPrediction event,
    Emitter<PvpState> emit,
  ) async {
    emit(PvpLoading());
    try {
      final response = await apiService.getPvpPrediction(event.request);
      emit(PvpLoaded(response: response));
    } catch (e) {
      emit(PvpError(message: e.toString()));
    }
  }

  void _onClearPvp(
    ClearPvp event,
    Emitter<PvpState> emit,
  ) {
    emit(PvpInitial());
  }
}
