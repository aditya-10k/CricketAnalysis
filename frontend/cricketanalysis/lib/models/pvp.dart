class PvpRequest {
  final String batter;
  final String bowler;
  final String? venue;
  final bool recentMatchesOnly;

  PvpRequest({
    required this.batter,
    required this.bowler,
    this.venue,
    required this.recentMatchesOnly,
  });

  Map<String, dynamic> toJson() {
    return {
      'batter': batter,
      'bowler': bowler,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
      'recent_matches_only': recentMatchesOnly,
    };
  }
}

class PvpResponse {
  final String batter;
  final String bowler;
  final String venue;
  final Prediction prediction;
  final HistoricalData historicalData;
  final Context context;
  final String sampleQuality;

  PvpResponse({
    required this.batter,
    required this.bowler,
    required this.venue,
    required this.prediction,
    required this.historicalData,
    required this.context,
    required this.sampleQuality,
  });

  factory PvpResponse.fromJson(Map<String, dynamic> json) {
    return PvpResponse(
      batter: json['batter'] as String,
      bowler: json['bowler'] as String,
      venue: json['venue'] as String,
      prediction: Prediction.fromJson(json['prediction'] as Map<String, dynamic>),
      historicalData: HistoricalData.fromJson(
          json['historical_data'] as Map<String, dynamic>),
      context: Context.fromJson(json['context'] as Map<String, dynamic>),
      sampleQuality: json['sample_quality'] as String,
    );
  }
}

class Prediction {
  final double expectedRunsPerBall;
  final double expectedDismissalRate;
  final double matchupAdvantage;
  final String confidence;
  final String winner;

  Prediction({
    required this.expectedRunsPerBall,
    required this.expectedDismissalRate,
    required this.matchupAdvantage,
    required this.confidence,
    required this.winner,
  });

  factory Prediction.fromJson(Map<String, dynamic> json) {
    return Prediction(
      expectedRunsPerBall: (json['expected_runs_per_ball'] as num).toDouble(),
      expectedDismissalRate: (json['expected_dismissal_rate'] as num).toDouble(),
      matchupAdvantage: (json['matchup_advantage'] as num).toDouble(),
      confidence: json['confidence'] as String,
      winner: json['winner'] as String,
    );
  }
}

class HistoricalData {
  final int ballsFaced;
  final int runsScored;
  final int dismissals;
  final double strikeRate;
  final double average;
  final double boundaryPercentage;

  HistoricalData({
    required this.ballsFaced,
    required this.runsScored,
    required this.dismissals,
    required this.strikeRate,
    required this.average,
    required this.boundaryPercentage,
  });

  factory HistoricalData.fromJson(Map<String, dynamic> json) {
    return HistoricalData(
      ballsFaced: json['balls_faced'] as int,
      runsScored: json['runs_scored'] as int,
      dismissals: json['dismissals'] as int,
      strikeRate: (json['strike_rate'] as num).toDouble(),
      average: (json['average'] as num).toDouble(),
      boundaryPercentage: (json['boundary_percentage'] as num).toDouble(),
    );
  }
}

class Context {
  final double batterCareerAvgRpa;
  final double bowlerCareerAvgRpa;
  final double venueFactor;
  final List<String> styleMatchup;

  Context({
    required this.batterCareerAvgRpa,
    required this.bowlerCareerAvgRpa,
    required this.venueFactor,
    required this.styleMatchup,
  });

  factory Context.fromJson(Map<String, dynamic> json) {
    return Context(
      batterCareerAvgRpa: (json['batter_career_avg_rpa'] as num).toDouble(),
      bowlerCareerAvgRpa: (json['bowler_career_avg_rpa'] as num).toDouble(),
      venueFactor: (json['venue_factor'] as num).toDouble(),
      styleMatchup: (json['style_matchup'] as List).map((e) => e as String).toList(),
    );
  }
}
