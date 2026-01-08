import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/player_replacement.dart';
import '../../services/api_service.dart';

part 'player_replacement_event.dart';
part 'player_replacement_state.dart';

class PlayerReplacementBloc
    extends Bloc<PlayerReplacementEvent, PlayerReplacementState> {
  final ApiService apiService;

  PlayerReplacementBloc({required this.apiService})
      : super(PlayerReplacementInitial()) {
    on<FindPlayerReplacement>(_onFindPlayerReplacement);
    on<ClearPlayerReplacement>(_onClearPlayerReplacement);
  }

  Future<void> _onFindPlayerReplacement(
    FindPlayerReplacement event,
    Emitter<PlayerReplacementState> emit,
  ) async {
    emit(PlayerReplacementLoading());
    try {
      final response = await apiService.findPlayerReplacement(event.request);
      print(response);
      emit(PlayerReplacementLoaded(response: response));
    } catch (e) {
      emit(PlayerReplacementError(message: e.toString()));
    }
  }

  void _onClearPlayerReplacement(
    ClearPlayerReplacement event,
    Emitter<PlayerReplacementState> emit,
  ) {
    emit(PlayerReplacementInitial());
  }
}
