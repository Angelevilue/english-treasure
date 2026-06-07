import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/api_client.dart';

// ── API Client ──
final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(baseUrl: 'http://localhost:8080'); // macOS / Chrome / iOS 模拟器
  // iOS 模拟器使用: http://localhost:8080
  // 真机使用: http://<你的电脑IP>:8080
});

// ── Auth State ──
class AuthState {
  final bool isLoading;
  final bool isLoggedIn;
  final String? token;
  final String? nickname;
  final String? studyStage;

  const AuthState({
    this.isLoading = true,
    this.isLoggedIn = false,
    this.token,
    this.nickname,
    this.studyStage,
  });

  AuthState copyWith({
    bool? isLoading,
    bool? isLoggedIn,
    String? token,
    String? nickname,
    String? studyStage,
  }) {
    return AuthState(
      isLoading: isLoading ?? this.isLoading,
      isLoggedIn: isLoggedIn ?? this.isLoggedIn,
      token: token ?? this.token,
      nickname: nickname ?? this.nickname,
      studyStage: studyStage ?? this.studyStage,
    );
  }
}

class AuthNotifier extends StateNotifier<AuthState> {
  final ApiClient _api;

  AuthNotifier(this._api) : super(const AuthState());

  Future<bool> login(String phone, String password) async {
    try {
      final resp = await _api.dio.post('/api/auth/login/phone', data: {
        'phone': phone,
        'password': password,
      });
      final token = resp.data['access_token'] as String;
      await _api.saveToken(token);
      state = state.copyWith(isLoading: false, isLoggedIn: true, token: token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<bool> register(String phone, String password, String nickname) async {
    try {
      final resp = await _api.dio.post('/api/auth/register/phone', data: {
        'phone': phone,
        'password': password,
        'nickname': nickname,
      });
      final token = resp.data['access_token'] as String;
      await _api.saveToken(token);
      state = state.copyWith(isLoading: false, isLoggedIn: true, token: token);
      return true;
    } catch (e) {
      return false;
    }
  }

  Future<void> logout() async {
    await _api.clearToken();
    state = const AuthState(isLoading: false, isLoggedIn: false);
  }

  Future<void> checkAuth() async {
    final token = await _api.getToken();
    if (token != null) {
      state = state.copyWith(isLoading: false, isLoggedIn: true, token: token);
    } else {
      state = state.copyWith(isLoading: false, isLoggedIn: false);
    }
  }
}

final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  return AuthNotifier(ref.read(apiClientProvider));
});
