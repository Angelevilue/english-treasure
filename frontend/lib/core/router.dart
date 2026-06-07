import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'providers.dart';
import '../features/auth/auth_screen.dart';
import '../features/vocab/vocab_screen.dart';
import '../features/grammar/grammar_screen.dart';
import '../features/speak/speak_screen.dart';
import '../features/profile/profile_screen.dart';

final _rootNavigatorKey = GlobalKey<NavigatorState>();
final _shellNavigatorKey = GlobalKey<NavigatorState>();

final appRouterProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authProvider);

  return GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/vocab',
    redirect: (context, state) {
      final isLoggedIn = auth.isLoggedIn;
      final isLoading = auth.isLoading;
      final isAuthRoute = state.uri.path == '/login';
      final isSplash = state.uri.path == '/splash';

      // 还在检查 token → 显示启动页
      if (isLoading && !isSplash) return '/splash';
      if (!isLoading && isSplash) return isLoggedIn ? '/vocab' : '/login';

      if (!isLoggedIn && !isAuthRoute) return '/login';
      if (isLoggedIn && isAuthRoute) return '/vocab';
      return null;
    },
    routes: [
      GoRoute(
        path: '/splash',
        builder: (_, __) => const Scaffold(
          body: Center(child: CircularProgressIndicator()),
        ),
      ),
      GoRoute(
        path: '/login',
        builder: (_, __) => const AuthScreen(),
      ),
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(
            path: '/vocab',
            builder: (_, __) => const VocabScreen(),
          ),
          GoRoute(
            path: '/grammar',
            builder: (_, __) => const GrammarScreen(),
          ),
          GoRoute(
            path: '/speak',
            builder: (_, __) => const SpeakScreen(),
          ),
          GoRoute(
            path: '/profile',
            builder: (_, __) => const ProfileScreen(),
          ),
        ],
      ),
    ],
  );
});

/// 底部导航外壳
class MainShell extends ConsumerWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  int _currentIndex(Uri uri) {
    if (uri.path.startsWith('/grammar')) return 1;
    if (uri.path.startsWith('/speak')) return 2;
    if (uri.path.startsWith('/profile')) return 3;
    return 0;
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final uri = GoRouterState.of(context).uri;
    return Scaffold(
      body: child,
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex(uri),
        onDestinationSelected: (i) {
          final routes = ['/vocab', '/grammar', '/speak', '/profile'];
          context.go(routes[i]);
        },
        destinations: const [
          NavigationDestination(icon: Icon(Icons.book), label: '速记'),
          NavigationDestination(icon: Icon(Icons.menu_book), label: '语法'),
          NavigationDestination(icon: Icon(Icons.record_voice_over), label: '跟读'),
          NavigationDestination(icon: Icon(Icons.person), label: '我的'),
        ],
      ),
    );
  }
}
