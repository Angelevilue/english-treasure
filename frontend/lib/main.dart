import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/router.dart';
import 'core/theme.dart';
import 'core/providers.dart';

void main() {
  runApp(
    const ProviderScope(
      child: EnglishTreasureApp(),
    ),
  );
}

class EnglishTreasureApp extends ConsumerStatefulWidget {
  const EnglishTreasureApp({super.key});

  @override
  ConsumerState<EnglishTreasureApp> createState() => _EnglishTreasureAppState();
}

class _EnglishTreasureAppState extends ConsumerState<EnglishTreasureApp> {
  @override
  void initState() {
    super.initState();
    // 启动时检查已保存的 token
    Future.microtask(() => ref.read(authProvider.notifier).checkAuth());
  }

  @override
  Widget build(BuildContext context) {
    final router = ref.watch(appRouterProvider);
    return MaterialApp.router(
      title: '英语宝典',
      theme: AppTheme.light,
      routerConfig: router,
      debugShowCheckedModeBanner: false,
    );
  }
}
