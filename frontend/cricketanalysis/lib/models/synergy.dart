class SynergyBattingRequest {
  final String batter1;
  final String batter2;
  final String? venue;

  SynergyBattingRequest({
    required this.batter1,
    required this.batter2,
    this.venue,
  });

  Map<String, dynamic> toJson() {
    return {
      'batter1': batter1,
      'batter2': batter2,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
    };
  }
}

class SynergyBowlingRequest {
  final String bowler1;
  final String bowler2;
  final String? venue;
  final String? phase;

  SynergyBowlingRequest({
    required this.bowler1,
    required this.bowler2,
    this.venue,
    this.phase,
  });

  Map<String, dynamic> toJson() {
    return {
      'bowler1': bowler1,
      'bowler2': bowler2,
      if (venue != null && venue!.isNotEmpty) 'venue': venue,
      if (phase != null && phase!.isNotEmpty) 'phase': phase,
    };
  }
}

class SynergyBattingResponse {
  final String batter1;
  final String batter2;
  final Partnership partnership;
  final SynergyAnalysis synergyAnalysis;
  final IndividualWhenTogether individualWhenTogether;
  final String sampleQuality;
  final double confidence;

  SynergyBattingResponse({
    required this.batter1,
    required this.batter2,
    required this.partnership,
    required this.synergyAnalysis,
    required this.individualWhenTogether,
    required this.sampleQuality,
    required this.confidence,
  });

  factory SynergyBattingResponse.fromJson(Map<String, dynamic> json) {
    return SynergyBattingResponse(
      batter1: json['batter1'] ?? '',
      batter2: json['batter2'] ?? '',
      partnership:
          Partnership.fromJson(json['partnership'] as Map<String, dynamic>),
      synergyAnalysis:
          SynergyAnalysis.fromJson(json['synergy_analysis'] as Map<String, dynamic>),
      individualWhenTogether: IndividualWhenTogether.fromJson(
          json['individual_when_together'] as Map<String, dynamic>),
      sampleQuality: json['sample_quality'] ?? '',
      confidence: (json['confidence'] as num? ?? 0).toDouble(),
    );
  }
}

class SynergyBowlingResponse {
  final String bowler1;
  final String bowler2;
  final Combination combination;
  final SynergyAnalysis synergyAnalysis;
  final WicketPartnership wicketPartnership;
  final String sampleQuality;
  final double confidence;

  SynergyBowlingResponse({
    required this.bowler1,
    required this.bowler2,
    required this.combination,
    required this.synergyAnalysis,
    required this.wicketPartnership,
    required this.sampleQuality,
    required this.confidence,
  });

  factory SynergyBowlingResponse.fromJson(Map<String, dynamic> json) {
    return SynergyBowlingResponse(
      bowler1: json['bowler1'] ?? '',
      bowler2: json['bowler2'] ?? '',
      combination:
          Combination.fromJson(json['combination'] as Map<String, dynamic>),
      synergyAnalysis:
          SynergyAnalysis.fromJson(json['synergy_analysis'] as Map<String, dynamic>),
      wicketPartnership: WicketPartnership.fromJson(
          json['wicket_partnership'] as Map<String, dynamic>),
      sampleQuality: json['sample_quality'] ?? '',
      confidence: (json['confidence'] as num? ?? 0).toDouble(),
    );
  }
}

class Partnership {
  final int inningsTogether;
  final int partnershipRuns;
  final int ballsTogether;
  final double partnershipRate;
  final double avgPartnership;
  final int highestPartnership;

  Partnership({
    required this.inningsTogether,
    required this.partnershipRuns,
    required this.ballsTogether,
    required this.partnershipRate,
    required this.avgPartnership,
    required this.highestPartnership,
  });

  factory Partnership.fromJson(Map<String, dynamic> json) {
    return Partnership(
      inningsTogether: (json['innings_together'] as num? ?? 0).toInt(),
      partnershipRuns: (json['partnership_runs'] as num? ?? 0).toInt(),
      ballsTogether: (json['balls_together'] as num? ?? 0).toInt(),
      partnershipRate: (json['partnership_rate'] as num? ?? 0).toDouble(),
      avgPartnership: (json['avg_partnership'] as num? ?? 0).toDouble(),
      highestPartnership: (json['highest_partnership'] as num? ?? 0).toInt(),
    );
  }
}

class SynergyAnalysis {
  final double synergyScore;
  final String rating;
  final String explanation;

  SynergyAnalysis({
    required this.synergyScore,
    required this.rating,
    required this.explanation,
  });

  factory SynergyAnalysis.fromJson(Map<String, dynamic> json) {
    return SynergyAnalysis(
      synergyScore: (json['synergy_score'] as num? ?? 0).toDouble(),
      rating: json['rating'] ?? '',
      explanation: json['explanation'] ?? json['compatibility'] ?? '',
    );
  }
}

class IndividualWhenTogether {
  final IndividualBatter batter1;
  final IndividualBatter batter2;

  IndividualWhenTogether({
    required this.batter1,
    required this.batter2,
  });

  factory IndividualWhenTogether.fromJson(Map<String, dynamic> json) {
    return IndividualWhenTogether(
      batter1: IndividualBatter.fromJson(
          json['batter1'] as Map<String, dynamic>? ?? const {}),
      batter2: IndividualBatter.fromJson(
          json['batter2'] as Map<String, dynamic>? ?? const {}),
    );
  }
}

class IndividualBatter {
  final double strikeRate;

  IndividualBatter({required this.strikeRate});

  factory IndividualBatter.fromJson(Map<String, dynamic> json) {
    return IndividualBatter(
      strikeRate: (json['strike_rate'] as num? ?? 0).toDouble(),
    );
  }
}

class Combination {
  final int matchesTogether;
  final int ballsTogether;
  final int combinedWickets;
  final double combinedEconomy;
  final double partnershipStrikeRate;
  final double dotBallPercentage;

  Combination({
    required this.matchesTogether,
    required this.ballsTogether,
    required this.combinedWickets,
    required this.combinedEconomy,
    required this.partnershipStrikeRate,
    required this.dotBallPercentage,
  });

  factory Combination.fromJson(Map<String, dynamic> json) {
    return Combination(
      matchesTogether: (json['matches_together'] as num? ?? 0).toInt(),
      ballsTogether: (json['balls_together'] as num? ?? 0).toInt(),
      combinedWickets: (json['combined_wickets'] as num? ?? 0).toInt(),
      combinedEconomy: (json['combined_economy'] as num? ?? 0).toDouble(),
      partnershipStrikeRate:
          (json['partnership_strike_rate'] as num? ?? 0).toDouble(),
      dotBallPercentage:
          (json['dot_ball_percentage'] as num? ?? 0).toDouble(),
    );
  }
}

class WicketPartnership {
  final double wicketClustering;

  WicketPartnership({required this.wicketClustering});

  factory WicketPartnership.fromJson(Map<String, dynamic> json) {
    return WicketPartnership(
      wicketClustering: (json['wicket_clustering'] as num? ?? 0).toDouble(),
    );
  }
}
