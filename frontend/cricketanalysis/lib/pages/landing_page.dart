import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

const _accentColor = Color(0xFFC63A2E);

class LandingPage extends StatelessWidget {
  const LandingPage({super.key});

  @override
  Widget build(BuildContext context) {
    final isMobile = MediaQuery.of(context).size.width <= 800;
          
    return Scaffold(
      backgroundColor: Colors.white,
      body: Column(
        children: [
          // Header
          Container(
            height: 64,
            decoration: const BoxDecoration(
              color: Colors.white,
              border: Border(
                bottom: BorderSide(color: Colors.black12, width: 1),
              ),
            ),
            child: Center(
              child: Container(
                constraints: const BoxConstraints(maxWidth: 1400),
                padding: const EdgeInsets.symmetric(horizontal: 40),
                child: Row(
                  children: [
                    Image.asset("assets/image-removebg-preview.png", height: 60,),
                    SizedBox(width: 20,),
                    const Text(
                      '12th Man',
                      style: TextStyle(
                        color: Colors.black87,
                        fontWeight: FontWeight.w600,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
          // Content
          Expanded(
            child: Center(
              child: Container(
                constraints: const BoxConstraints(maxWidth: 1400),
                padding: EdgeInsets.symmetric(
                  horizontal: isMobile ? 20 : 40,
                  vertical: isMobile ? 20 : 40,
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Cricket Analysis Dashboard',
                      style: TextStyle(
                        fontSize: isMobile ? 24 : 32,
                        fontWeight: FontWeight.w600,
                        color: Colors.black87,
                        letterSpacing: -0.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Quick tools for player and team evaluation',
                      style: TextStyle(
                        fontSize: 15,
                        color: Colors.black54,
                      ),
                    ),
                    const SizedBox(height: 40),
                    Expanded(
                      child: SingleChildScrollView(
                        child: isMobile
                            ? Column(
                                children: [
                                  _buildOptionItem(
                                    context,
                                    title: 'Player Info',
                                    description: 'Search and view detailed player information',
                                    onTap: () => context.go('/player-info'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Team ELO History',
                                    description: 'View team ELO rating history with graphs',
                                    onTap: () => context.go('/team-elo'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Player Replacement',
                                    description: 'Find suitable player replacements',
                                    onTap: () => context.go('/player-replacement'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Player vs Player',
                                    description: 'Predict matchup outcomes between players',
                                    onTap: () => context.go('/pvp'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Player vs Team',
                                    description: 'Analyze player performance against teams',
                                    onTap: () => context.go('/pvt'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Synergy',
                                    description: 'Evaluate batting/bowling pair synergy',
                                    onTap: () => context.go('/synergy'),
                                  ),
                                  _buildOptionItem(
                                    context,
                                    title: 'Best XI',
                                    description: 'Optimize playing XI for two squads',
                                    onTap: () => context.go('/best-xi'),
                                  ),
                                ],
                              )
                            : Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Expanded(
                                    child: Column(
                                      children: [
                                        _buildOptionItem(
                                          context,
                                          title: 'Player Info',
                                          description: 'Search and view detailed player information',
                                          onTap: () => context.go('/player-info'),
                                        ),
                                        _buildOptionItem(
                                          context,
                                          title: 'Team ELO History',
                                          description: 'View team ELO rating history with graphs',
                                          onTap: () => context.go('/team-elo'),
                                        ),
                                        _buildOptionItem(
                                          context,
                                          title: 'Player Replacement',
                                          description: 'Find suitable player replacements',
                                          onTap: () => context.go('/player-replacement'),
                                        ),
                                        _buildOptionItem(
                                          context,
                                          title: 'Player vs Player',
                                          description: 'Predict matchup outcomes between players',
                                          onTap: () => context.go('/pvp'),
                                        ),
                                      ],
                                    ),
                                  ),
                                  const SizedBox(width: 40),
                                  Expanded(
                                    child: Column(
                                      children: [
                                        _buildOptionItem(
                                          context,
                                          title: 'Player vs Team',
                                          description: 'Analyze player performance against teams',
                                          onTap: () => context.go('/pvt'),
                                        ),
                                        _buildOptionItem(
                                          context,
                                          title: 'Synergy',
                                          description: 'Evaluate batting/bowling pair synergy',
                                          onTap: () => context.go('/synergy'),
                                        ),
                                        _buildOptionItem(
                                          context,
                                          title: 'Best XI',
                                          description: 'Optimize playing XI for two squads',
                                          onTap: () => context.go('/best-xi'),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildOptionItem(
    BuildContext context, {
    required String title,
    required String description,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      hoverColor: Colors.black.withOpacity(0.02),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: Colors.black12, width: 1),
          ),
        ),
        child: Row(
            children: [
                 Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            title,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w600,
                              color: _accentColor,
                            ),
                          ),
                          const SizedBox(height: 6),
                          Text(
                            description,
                            style: const TextStyle(
                              fontSize: 14,
                              color: Colors.black54,
                              height: 1.4,
                            ),
                          ),
                        ],
                      ),
                 ),
            ],
        ),
      ),
    );
  }
}
