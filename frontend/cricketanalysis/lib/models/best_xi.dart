class BestXiRequest {
  final List<String> homeSquad;
  final List<String> awaySquad;
  final String? venue;
  final BestXiConstraints constraints;

  BestXiRequest({
    required this.homeSquad,
    required this.awaySquad,
    this.venue,
    required this.constraints,
  });

  Map<String, dynamic> toJson() {
    return {
      'home_squad': homeSquad,
      'away_squad': awaySquad,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
      'constraints': constraints.toJson(),
    };
  }
}

class BestXiConstraints {
  final int maxOverseas;
  final int minBowlers;
  final int minBatters;
  final double minConfidence;

  BestXiConstraints({
    required this.maxOverseas,
    required this.minBowlers,
    required this.minBatters,
    required this.minConfidence,
  });

  Map<String, dynamic> toJson() {
    return {
      'max_overseas': maxOverseas,
      'min_bowlers': minBowlers,
      'min_batters': minBatters,
      'min_confidence': minConfidence,
    };
  }
}

class BestXiPlayer {
  final String player;
  final String role;
  final String nationality;
  final double baseValue;
  final double formValue;
  final double combinedValue;
  final double confidence;
  final int ballsFaced;
  final int ballsBowled;
  final int daysSinceLastMatch;
  final double matchupAdjustment;
  final double synergyBonus;
  final double finalValue;

  BestXiPlayer({
    required this.player,
    required this.role,
    required this.nationality,
    required this.baseValue,
    required this.formValue,
    required this.combinedValue,
    required this.confidence,
    required this.ballsFaced,
    required this.ballsBowled,
    required this.daysSinceLastMatch,
    required this.matchupAdjustment,
    required this.synergyBonus,
    required this.finalValue,
  });

  factory BestXiPlayer.fromJson(Map<String, dynamic> json) {
    return BestXiPlayer(
      player: json['player']?.toString() ?? '',
      role: json['role']?.toString() ?? '',
      nationality: json['nationality']?.toString() ?? '',
      baseValue: _toDouble(json['base_value']),
      formValue: _toDouble(json['form_value']),
      combinedValue: _toDouble(json['combined_value']),
      confidence: _toDouble(json['confidence']),
      ballsFaced: _toInt(json['balls_faced']),
      ballsBowled: _toInt(json['balls_bowled']),
      daysSinceLastMatch: _toInt(json['days_since_last_match']),
      matchupAdjustment: _toDouble(json['matchup_adjustment']),
      synergyBonus: _toDouble(json['synergy_bonus']),
      finalValue: _toDouble(json['final_value']),
    );
  }

  static double _toDouble(dynamic value) {
    if (value == null) return 0.0;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is num) return value.toDouble();
    return 0.0;
  }

  static int _toInt(dynamic value) {
    if (value == null) return 0;
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is num) return value.toInt();
    return 0;
  }
}

class BestXiResponse {
  final List<BestXiPlayer> team;
  final double teamTotalValue;
  final double teamSynergyBonus;
  final double teamMatchupAdvantage;
  final String venue;

  BestXiResponse({
    required this.team,
    required this.teamTotalValue,
    required this.teamSynergyBonus,
    required this.teamMatchupAdvantage,
    required this.venue,
  });

  factory BestXiResponse.fromJson(Map<String, dynamic> json) {
    return BestXiResponse(
      team: (json['team'] as List<dynamic>? ?? [])
          .map((e) => BestXiPlayer.fromJson(e as Map<String, dynamic>))
          .toList(),
      teamTotalValue: (json['team_total_value'] as num? ?? 0).toDouble(),
      teamSynergyBonus: (json['team_synergy_bonus'] as num? ?? 0).toDouble(),
      teamMatchupAdvantage:
          (json['team_matchup_advantage'] as num? ?? 0).toDouble(),
      venue: json['venue'] ?? '',
    );
  }
}
