class PlayerInfo {
  final String player;
  final String role;
  final String nationality;
  final Styles styles;
  final Career career;
  final Exposure exposure;
  final BattingPosition battingPosition;
  final RecentForm recentForm;

  PlayerInfo({
    required this.player,
    required this.role,
    required this.nationality,
    required this.styles,
    required this.career,
    required this.exposure,
    required this.battingPosition,
    required this.recentForm,
  });

  factory PlayerInfo.fromJson(Map<String, dynamic> json) {
    return PlayerInfo(
      player: json['player'] as String,
      role: json['role'] as String,
      nationality: json['nationality'] as String,
      styles: Styles.fromJson(json['styles'] as Map<String, dynamic>),
      career: Career.fromJson(json['career'] as Map<String, dynamic>),
      exposure: Exposure.fromJson(json['exposure'] as Map<String, dynamic>),
      battingPosition: BattingPosition.fromJson(
          json['batting_position'] as Map<String, dynamic>),
      recentForm: RecentForm.fromJson(
          json['recent_form'] as Map<String, dynamic>),
    );
  }
}

class Styles {
  final String batting;
  final String? bowling;

  Styles({
    required this.batting,
    this.bowling,
  });

  factory Styles.fromJson(Map<String, dynamic> json) {
    return Styles(
      batting: json['batting'] as String,
      bowling: json['bowling'] as String?,
    );
  }
}

class Career {
  final double totalValueZ;
  final double finalValue;
  final double confidence;
  final int daysSinceLastMatch;

  Career({
    required this.totalValueZ,
    required this.finalValue,
    required this.confidence,
    required this.daysSinceLastMatch,
  });

  factory Career.fromJson(Map<String, dynamic> json) {
    return Career(
      totalValueZ: (json['total_value_z'] as num).toDouble(),
      finalValue: (json['final_value'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      daysSinceLastMatch: json['days_since_last_match'] as int,
    );
  }
}

class Exposure {
  final int ballsFaced;
  final int ballsBowled;
  final int runsScored;
  final int wicketsTaken;

  Exposure({
    required this.ballsFaced,
    required this.ballsBowled,
    required this.runsScored,
    required this.wicketsTaken,
  });

  factory Exposure.fromJson(Map<String, dynamic> json) {
    return Exposure(
      ballsFaced: json['balls_faced'] as int,
      ballsBowled: json['balls_bowled'] as int,
      runsScored: json['runs_scored'] as int,
      wicketsTaken: json['wickets_taken'] as int,
    );
  }
}

class BattingPosition {
  final double avg;
  final double median;
  final int innings;

  BattingPosition({
    required this.avg,
    required this.median,
    required this.innings,
  });

  factory BattingPosition.fromJson(Map<String, dynamic> json) {
    return BattingPosition(
      avg: (json['avg'] as num).toDouble(),
      median: (json['median'] as num).toDouble(),
      innings: json['innings'] as int,
    );
  }
}

class RecentForm {
  final double formZ;
  final double confidence;
  final String asOf;

  RecentForm({
    required this.formZ,
    required this.confidence,
    required this.asOf,
  });

  factory RecentForm.fromJson(Map<String, dynamic> json) {
    return RecentForm(
      formZ: (json['form_z'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      asOf: json['as_of'] as String,
    );
  }
}
