import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/player.dart';
import '../../services/api_service.dart';

part 'players_event.dart';
part 'players_state.dart';

class PlayersBloc extends Bloc<PlayersEvent, PlayersState> {
  final ApiService apiService;

  PlayersBloc({required this.apiService}) : super(PlayersInitial()) {
    on<LoadPlayers>(_onLoadPlayers);
  }

  Future<void> _onLoadPlayers(
    LoadPlayers event,
    Emitter<PlayersState> emit,
  ) async {
    emit(PlayersLoading());
    try {
      final response = await apiService.getPlayers();
      emit(PlayersLoaded(players: response.players));
    } catch (e) {
      emit(PlayersError(message: e.toString()));
    }
  }
}
