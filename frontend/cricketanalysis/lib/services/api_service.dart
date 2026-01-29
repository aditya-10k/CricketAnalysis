import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/player.dart';
import '../models/player_info.dart';
import '../models/player_replacement.dart';
import '../models/team_elo.dart';
import '../models/teams.dart';
import '../models/pvp.dart';
import '../models/pvt.dart';
import '../models/synergy.dart';
import '../models/best_xi.dart';

class ApiService {
  static const String baseUrl = 'https://cricketanalysis.onrender.com';

  String _extractError(http.Response response) {
    try {
      final body = json.decode(response.body);
      if (body is Map && body['detail'] != null) {
        return body['detail'].toString();
      }
      return body.toString();
    } catch (_) {
      return response.body;
    }
  }

  Future<PlayersResponse> getPlayers() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/meta/players'),
        headers: {'accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        return PlayersResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      print(e);
      throw Exception('Error fetching players: $e');
    }
  }

  Future<PlayerInfo> getPlayerInfo(String playerName) async {
    try {
      final encodedName = Uri.encodeComponent(playerName);
      final response = await http.get(
        Uri.parse('$baseUrl/api/meta/player/$encodedName'),
        headers: {'accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        return PlayerInfo.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error fetching player info: $e');
    }
  }

  Future<TeamEloHistory> getTeamEloHistory(String teamName) async {
    try {
      final encodedName = Uri.encodeComponent(teamName);
      final response = await http.get(
        Uri.parse('$baseUrl/api/meta/teams/$encodedName/elo'),
        headers: {'accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        return TeamEloHistory.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error fetching team ELO: $e');
    }
  }

  Future<PlayerReplacementResponse> findPlayerReplacement(
      PlayerReplacementRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/replacement/find'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        print(response.body);
        return PlayerReplacementResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error finding player replacement: $e');
    }
  }

  Future<TeamsResponse> getTeams() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/api/meta/teams'),
        headers: {'accept': 'application/json'},
      );

      if (response.statusCode == 200) {
        return TeamsResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error fetching teams: $e');
    }
  }

  Future<PvpResponse> getPvpPrediction(PvpRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/pvp/predict'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PvpResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting PvP prediction: $e');
    }
  }

  Future<PvtBatterResponse> getPvtBatter(PvtBatterRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/pvt/batter'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PvtBatterResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting PvT batter: $e');
    }
  }

  Future<PvtBowlerResponse> getPvtBowler(PvtBowlerRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/pvt/bowler'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );

      if (response.statusCode == 200) {
        return PvtBowlerResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting PvT bowler: $e');
    }
  }

  Future<SynergyBattingResponse> getSynergyBatting(
      SynergyBattingRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/synergy/batting'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );
      if (response.statusCode == 200) {
        return SynergyBattingResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting batting synergy: $e');
    }
  }

  Future<SynergyBowlingResponse> getSynergyBowling(
      SynergyBowlingRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/synergy/bowling'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );
      if (response.statusCode == 200) {
        return SynergyBowlingResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting bowling synergy: $e');
    }
  }

  Future<BestXiResponse> getBestXi(BestXiRequest request) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/bestxi/optimize'),
        headers: {
          'accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: json.encode(request.toJson()),
      );
      if (response.statusCode == 200) {
        return BestXiResponse.fromJson(
            json.decode(response.body) as Map<String, dynamic>);
      } else {
        throw Exception(_extractError(response));
      }
    } catch (e) {
      throw Exception('Error getting Best XI: $e');
    }
  }
}
