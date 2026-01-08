import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/pvt.dart';
import '../../services/api_service.dart';

part 'pvt_event.dart';
part 'pvt_state.dart';

class PvtBloc extends Bloc<PvtEvent, PvtState> {
  final ApiService apiService;

  PvtBloc({required this.apiService}) : super(PvtInitial()) {
    on<LoadPvtBatter>(_onLoadPvtBatter);
    on<LoadPvtBowler>(_onLoadPvtBowler);
    on<ClearPvt>(_onClearPvt);
  }

  Future<void> _onLoadPvtBatter(
    LoadPvtBatter event,
    Emitter<PvtState> emit,
  ) async {
    emit(PvtLoading());
    try {
      final response = await apiService.getPvtBatter(event.request);
      emit(PvtBatterLoaded(response: response));
    } catch (e) {
      emit(PvtError(message: e.toString()));
    }
  }

  Future<void> _onLoadPvtBowler(
    LoadPvtBowler event,
    Emitter<PvtState> emit,
  ) async {
    emit(PvtLoading());
    try {
      final response = await apiService.getPvtBowler(event.request);
      emit(PvtBowlerLoaded(response: response));
    } catch (e) {
      emit(PvtError(message: e.toString()));
    }
  }

  void _onClearPvt(
    ClearPvt event,
    Emitter<PvtState> emit,
  ) {
    emit(PvtInitial());
  }
}
