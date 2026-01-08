class TeamEloHistory {
  final String team;
  final List<EloDataPoint> eloHistory;

  TeamEloHistory({
    required this.team,
    required this.eloHistory,
  });

  factory TeamEloHistory.fromJson(Map<String, dynamic> json) {
    return TeamEloHistory(
      team: json['team'] as String,
      eloHistory: (json['elo_history'] as List)
          .map((e) => EloDataPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

class EloDataPoint {
  final String date;
  final double elo;

  EloDataPoint({
    required this.date,
    required this.elo,
  });

  factory EloDataPoint.fromJson(Map<String, dynamic> json) {
    return EloDataPoint(
      date: json['date'] as String,
      elo: (json['elo'] as num).toDouble(),
    );
  }
}
