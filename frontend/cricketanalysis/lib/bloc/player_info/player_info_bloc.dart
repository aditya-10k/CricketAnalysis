import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/player_info.dart';
import '../../services/api_service.dart';

part 'player_info_event.dart';
part 'player_info_state.dart';

class PlayerInfoBloc extends Bloc<PlayerInfoEvent, PlayerInfoState> {
  final ApiService apiService;

  PlayerInfoBloc({required this.apiService}) : super(PlayerInfoInitial()) {
    on<LoadPlayerInfo>(_onLoadPlayerInfo);
    on<ClearPlayerInfo>(_onClearPlayerInfo);
  }

  Future<void> _onLoadPlayerInfo(
    LoadPlayerInfo event,
    Emitter<PlayerInfoState> emit,
  ) async {
    emit(PlayerInfoLoading());
    try {
      final playerInfo = await apiService.getPlayerInfo(event.playerName);
      emit(PlayerInfoLoaded(playerInfo: playerInfo));
    } catch (e) {
      emit(PlayerInfoError(message: e.toString()));
    }
  }

  void _onClearPlayerInfo(
    ClearPlayerInfo event,
    Emitter<PlayerInfoState> emit,
  ) {
    emit(PlayerInfoInitial());
  }
}
