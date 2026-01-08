import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../models/team_elo.dart';
import '../../services/api_service.dart';

part 'team_elo_event.dart';
part 'team_elo_state.dart';

class TeamEloBloc extends Bloc<TeamEloEvent, TeamEloState> {
  final ApiService apiService;

  TeamEloBloc({required this.apiService}) : super(TeamEloInitial()) {
    on<LoadTeamElo>(_onLoadTeamElo);
    on<ClearTeamElo>(_onClearTeamElo);
  }

  Future<void> _onLoadTeamElo(
    LoadTeamElo event,
    Emitter<TeamEloState> emit,
  ) async {
    emit(TeamEloLoading());
    try {
      final eloHistory = await apiService.getTeamEloHistory(event.teamName);
      emit(TeamEloLoaded(eloHistory: eloHistory));
    } catch (e) {
      emit(TeamEloError(message: e.toString()));
    }
  }

  void _onClearTeamElo(
    ClearTeamElo event,
    Emitter<TeamEloState> emit,
  ) {
    emit(TeamEloInitial());
  }
}
