class PvtBatterRequest {
  final String batter;
  final String team;
  final String? venue;
  final String phase;

  PvtBatterRequest({
    required this.batter,
    required this.team,
    this.venue,
    required this.phase,
  });

  Map<String, dynamic> toJson() {
    return {
      'batter': batter,
      'team': team,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
      'phase': phase,
    };
  }
}

class PvtBowlerRequest {
  final String bowler;
  final String team;
  final String? venue;
  final String phase;

  PvtBowlerRequest({
    required this.bowler,
    required this.team,
    this.venue,
    required this.phase,
  });

  Map<String, dynamic> toJson() {
    return {
      'bowler': bowler,
      'team': team,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
      'phase': phase,
    };
  }
}

class PvtBatterResponse {
  final String batter;
  final String team;
  final String venue;
  final Performance performance;
  final String confidence;

  PvtBatterResponse({
    required this.batter,
    required this.team,
    required this.venue,
    required this.performance,
    required this.confidence,
  });

  factory PvtBatterResponse.fromJson(Map<String, dynamic> json) {
    return PvtBatterResponse(
      batter: json['batter'] as String,
      team: json['team'] as String,
      venue: json['venue'] as String,
      performance: Performance.fromJson(json['performance'] as Map<String, dynamic>),
      confidence: json['confidence'] as String,
    );
  }
}

class PvtBowlerResponse {
  final String bowler;
  final String team;
  final String venue;
  final Performance performance;
  final String confidence;

  PvtBowlerResponse({
    required this.bowler,
    required this.team,
    required this.venue,
    required this.performance,
    required this.confidence,
  });

  factory PvtBowlerResponse.fromJson(Map<String, dynamic> json) {
    return PvtBowlerResponse(
      bowler: json['bowler'] as String,
      team: json['team'] as String,
      venue: json['venue'] as String,
      performance: Performance.fromJson(json['performance'] as Map<String, dynamic>),
      confidence: json['confidence'] as String,
    );
  }
}

class Performance {
  final int? inningsPlayed;
  final int? inningsBowled;
  final int runsScored;
  final int ballsFaced;
  final int? ballsBowled;
  final int dismissals;
  final int? wickets;
  final int? runsConceded;
  final double average;
  final double strikeRate;
  final double? economy;
  final double? dotBallPercentage;
  final double boundaryPercentage;
  final double avgRpa;
  final double avgWpa;
  final String performanceRating;

  Performance({
    this.inningsPlayed,
    this.inningsBowled,
    required this.runsScored,
    required this.ballsFaced,
    this.ballsBowled,
    required this.dismissals,
    this.wickets,
    this.runsConceded,
    required this.average,
    required this.strikeRate,
    this.economy,
    this.dotBallPercentage,
    required this.boundaryPercentage,
    required this.avgRpa,
    required this.avgWpa,
    required this.performanceRating,
  });

  factory Performance.fromJson(Map<String, dynamic> json) {
    return Performance(
      inningsPlayed: json['innings_played'] as int?,
      inningsBowled: json['innings_bowled'] as int?,
      runsScored: (json['runs_scored'] as num? ?? 0).toInt(),
      ballsFaced: (json['balls_faced'] as num? ?? 0).toInt(),
      ballsBowled: (json['balls_bowled'] as num?)?.toInt(),
      dismissals: (json['dismissals'] as num? ?? 0).toInt(),
      wickets: (json['wickets'] as num?)?.toInt(),
      runsConceded: (json['runs_conceded'] as num?)?.toInt(),
      average: (json['average'] as num? ?? 0).toDouble(),
      strikeRate: (json['strike_rate'] as num? ?? 0).toDouble(),
      economy:
          json['economy'] != null ? (json['economy'] as num).toDouble() : null,
      dotBallPercentage: json['dot_ball_percentage'] != null
          ? (json['dot_ball_percentage'] as num).toDouble()
          : null,
      boundaryPercentage:
          (json['boundary_percentage'] as num? ?? 0).toDouble(),
      avgRpa: (json['avg_rpa'] as num? ?? 0).toDouble(),
      avgWpa: (json['avg_wpa'] as num? ?? 0).toDouble(),
      performanceRating: json['performance_rating'] as String? ?? 'N/A',
    );
  }
}
