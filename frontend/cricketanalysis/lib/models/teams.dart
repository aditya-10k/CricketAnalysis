class TeamsResponse {
  final int count;
  final List<String> teams;

  TeamsResponse({
    required this.count,
    required this.teams,
  });

  factory TeamsResponse.fromJson(Map<String, dynamic> json) {
    return TeamsResponse(
      count: json['count'] as int,
      teams: (json['teams'] as List).map((e) => e as String).toList(),
    );
  }
}
