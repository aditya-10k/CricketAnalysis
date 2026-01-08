import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';
import '../../services/api_service.dart';

part 'teams_event.dart';
part 'teams_state.dart';

class TeamsBloc extends Bloc<TeamsEvent, TeamsState> {
  final ApiService apiService;

  TeamsBloc({required this.apiService}) : super(TeamsInitial()) {
    on<LoadTeams>(_onLoadTeams);
  }

  Future<void> _onLoadTeams(
    LoadTeams event,
    Emitter<TeamsState> emit,
  ) async {
    emit(TeamsLoading());
    try {
      final response = await apiService.getTeams();
      emit(TeamsLoaded(teams: response.teams));
    } catch (e) {
      emit(TeamsError(message: e.toString()));
    }
  }
}
