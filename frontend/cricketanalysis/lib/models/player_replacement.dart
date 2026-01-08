class PlayerReplacementRequest {
  final String player;
  final String? nationalityFilter;
  final List<String> excludePlayers;
  final int topN;
  final bool considerForm;

  PlayerReplacementRequest({
    required this.player,
    this.nationalityFilter,
    required this.excludePlayers,
    required this.topN,
    required this.considerForm,
  });

  Map<String, dynamic> toJson() {
    return {
      'player': player,
      if (nationalityFilter != null && nationalityFilter!.isNotEmpty)
        'nationality_filter': nationalityFilter,
      'exclude_players': excludePlayers,
      'top_n': topN,
      'consider_form': considerForm,
    };
  }
}

// Updated to match your new API response
class TargetProfile {
  final String role;
  final String nationality;
  final double careerValue;
  final double confidence;
  final int exposure;
  final int daysSinceLastMatch;

  TargetProfile({
    required this.role,
    required this.nationality,
    required this.careerValue,
    required this.confidence,
    required this.exposure,
    required this.daysSinceLastMatch,
  });

  factory TargetProfile.fromJson(Map<String, dynamic> json) {
    return TargetProfile(
      role: json['role'] ?? '',
      nationality: json['nationality'] ?? '',
      careerValue: (json['career_value'] ?? 0).toDouble(),
      confidence: (json['confidence'] ?? 0).toDouble(),
      exposure: json['exposure'] ?? 0,
      daysSinceLastMatch: json['days_since_last_match'] ?? 0,
    );
  }
}

// Updated ReplacementPlayer to match API fields
class ReplacementPlayer {
  final String player;
  final String role;
  final String nationality;
  final double similarityScore;
  final double careerValue;
  final double finalValue;
  final double confidence;
  final int daysSinceLastMatch;
  final String explanation;

  ReplacementPlayer({
    required this.player,
    required this.role,
    required this.nationality,
    required this.similarityScore,
    required this.careerValue,
    required this.finalValue,
    required this.confidence,
    required this.daysSinceLastMatch,
    required this.explanation,
  });

  // ✅ Add computed score property for backward compatibility
  double get score => finalValue;

  // ✅ Computed details map for backward compatibility  
  Map<String, dynamic> get details => {
    'role': role,
    'nationality': nationality,
    'similarity_score': similarityScore,
    'career_value': careerValue,
    'final_value': finalValue,
    'confidence': confidence,
    'days_since_last_match': daysSinceLastMatch,
    'explanation': explanation,
  };

  factory ReplacementPlayer.fromJson(Map<String, dynamic> json) {
    return ReplacementPlayer(
      player: json['player'] ?? '',
      role: json['role'] ?? '',
      nationality: json['nationality'] ?? '',
      similarityScore: (json['similarity_score'] ?? 0).toDouble(),
      careerValue: (json['career_value'] ?? 0).toDouble(),
      finalValue: (json['final_value'] ?? 0).toDouble(),
      confidence: (json['confidence'] ?? 0).toDouble(),
      daysSinceLastMatch: json['days_since_last_match'] ?? 0,
      explanation: json['explanation'] ?? '',
    );
  }
}

class Metadata {
  final int totalCandidates;
  final int filteredCount;
  final int searchTimeMs;

  Metadata({
    required this.totalCandidates,
    required this.filteredCount,
    required this.searchTimeMs,
  });

  factory Metadata.fromJson(Map<String, dynamic> json) {
    return Metadata(
      totalCandidates: json['total_candidates'] ?? 0,
      filteredCount: json['filtered_count'] ?? 0,
      searchTimeMs: json['search_time_ms'] ?? 0,
    );
  }
}

// Updated to handle your new API structure
class PlayerReplacementResponse {
  final String targetPlayer;
  final TargetProfile targetProfile;
  final List<ReplacementPlayer> replacements;
  final Metadata metadata;

  PlayerReplacementResponse({
    required this.targetPlayer,
    required this.targetProfile,
    required this.replacements,
    required this.metadata,
  });

  // ✅ Backward compatible getter for old UI code
  List<ReplacementPlayer> get oldReplacements => replacements;

  factory PlayerReplacementResponse.fromJson(dynamic json) {
    if (json is Map<String, dynamic>) {
      return PlayerReplacementResponse(
        targetPlayer: json['target_player'] ?? '',
        targetProfile: TargetProfile.fromJson(json['target_profile'] ?? {}),
        replacements: (json['replacements'] as List<dynamic>?)
            ?.map((e) => ReplacementPlayer.fromJson(e as Map<String, dynamic>))
            .toList() ?? [],
        metadata: Metadata.fromJson(json['metadata'] ?? {}),
      );
    }
    
    // Fallback for old response formats
    return PlayerReplacementResponse(
      targetPlayer: '',
      targetProfile: TargetProfile(role: '', nationality: '', careerValue: 0, confidence: 0, exposure: 0, daysSinceLastMatch: 0),
      replacements: (json as List<dynamic>?)
          ?.map((e) => ReplacementPlayer.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      metadata: Metadata(totalCandidates: 0, filteredCount: 0, searchTimeMs: 0),
    );
  }
}
