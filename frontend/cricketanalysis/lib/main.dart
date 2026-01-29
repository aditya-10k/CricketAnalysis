import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import 'bloc/players/players_bloc.dart';
import 'bloc/player_info/player_info_bloc.dart';
import 'bloc/team_elo/team_elo_bloc.dart';
import 'bloc/player_replacement/player_replacement_bloc.dart';
import 'bloc/teams/teams_bloc.dart';
import 'bloc/pvp/pvp_bloc.dart';
import 'bloc/pvt/pvt_bloc.dart';
import 'bloc/synergy/synergy_bloc.dart';
import 'bloc/best_xi/best_xi_bloc.dart';
import 'services/api_service.dart';
import 'pages/landing_page.dart';
import 'pages/player_info_page.dart';
import 'pages/team_elo_page.dart';
import 'pages/player_replacement_page.dart';
import 'pages/pvp_page.dart';
import 'pages/pvt_page.dart';
import 'pages/synergy_page.dart';
import 'pages/best_xi_page.dart';
import 'pages/splash_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiService = ApiService();

    return MultiBlocProvider(
      providers: [
        BlocProvider(
          create: (context) => PlayersBloc(apiService: apiService)
            ..add(LoadPlayers()),
        ),
        BlocProvider(
          create: (context) => TeamsBloc(apiService: apiService)
            ..add(LoadTeams()),
        ),
        BlocProvider(
          create: (context) => PlayerInfoBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => TeamEloBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => PlayerReplacementBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => PvpBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => PvtBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => SynergyBloc(apiService: apiService),
        ),
        BlocProvider(
          create: (context) => BestXiBloc(apiService: apiService),
        ),
      ],
      child: MaterialApp.router(
        title: 'Cricket Analysis',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
          useMaterial3: true,
        ),
        routerConfig: _router,
      ),
    );
  }
}

final GoRouter _router = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(
      path: '/splash',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/',
      builder: (context, state) => const LandingPage(),
    ),
    GoRoute(
      path: '/player-info',
      builder: (context, state) => const PlayerInfoPage(),
    ),
    GoRoute(
      path: '/team-elo',
      builder: (context, state) => const TeamEloPage(),
    ),
    GoRoute(
      path: '/player-replacement',
      builder: (context, state) => const PlayerReplacementPage(),
    ),
    GoRoute(
      path: '/pvp',
      builder: (context, state) => const PvpPage(),
    ),
    GoRoute(
      path: '/pvt',
      builder: (context, state) => const PvtPage(),
    ),
    GoRoute(
      path: '/synergy',
      builder: (context, state) => const SynergyPage(),
    ),
    GoRoute(
      path: '/best-xi',
      builder: (context, state) => const BestXiPage(),
    ),
  ],
);
