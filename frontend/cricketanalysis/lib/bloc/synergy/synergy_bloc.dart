import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/synergy.dart';
import '../../services/api_service.dart';

part 'synergy_event.dart';
part 'synergy_state.dart';

class SynergyBloc extends Bloc<SynergyEvent, SynergyState> {
  final ApiService apiService;

  SynergyBloc({required this.apiService}) : super(SynergyInitial()) {
    on<LoadSynergyBatting>(_onLoadBatting);
    on<LoadSynergyBowling>(_onLoadBowling);
    on<ClearSynergy>(_onClear);
  }

  Future<void> _onLoadBatting(
    LoadSynergyBatting event,
    Emitter<SynergyState> emit,
  ) async {
    emit(SynergyLoading());
    try {
      final response = await apiService.getSynergyBatting(event.request);
      emit(SynergyBattingLoaded(response: response));
    } catch (e) {
      emit(SynergyError(message: e.toString()));
    }
  }

  Future<void> _onLoadBowling(
    LoadSynergyBowling event,
    Emitter<SynergyState> emit,
  ) async {
    emit(SynergyLoading());
    try {
      final response = await apiService.getSynergyBowling(event.request);
      emit(SynergyBowlingLoaded(response: response));
    } catch (e) {
      emit(SynergyError(message: e.toString()));
    }
  }

  void _onClear(
    ClearSynergy event,
    Emitter<SynergyState> emit,
  ) {
    emit(SynergyInitial());
  }
}
