class Player {
  final String player;
  final String role;
  final String nationality;
  final String battingStyle;
  final String? bowlingStyle;
  final double totalValueZ;
  final double confidence;
  final int daysSinceLastMatch;

  Player({
    required this.player,
    required this.role,
    required this.nationality,
    required this.battingStyle,
    this.bowlingStyle,
    required this.totalValueZ,
    required this.confidence,
    required this.daysSinceLastMatch,
  });

  factory Player.fromJson(Map<String, dynamic> json) {
    return Player(
      player: json['player'] as String,
      role: json['role'] as String,
      nationality: json['nationality'] as String,
      battingStyle: json['batting_style'] as String,
      bowlingStyle: json['bowling_style'] as String?,
      totalValueZ: (json['total_value_z'] as num).toDouble(),
      confidence: (json['confidence'] as num).toDouble(),
      daysSinceLastMatch: json['days_since_last_match'] as int,
    );
  }
}

class PlayersResponse {
  final int count;
  final List<Player> players;

  PlayersResponse({
    required this.count,
    required this.players,
  });

  factory PlayersResponse.fromJson(Map<String, dynamic> json) {
    return PlayersResponse(
      count: json['count'] as int,
      players: (json['players'] as List)
          .map((e) => Player.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}
