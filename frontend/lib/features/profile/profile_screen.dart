import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';

class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  Map<String, dynamic>? _stats;
  Map<String, dynamic>? _profile;
  bool _loading = true;
  String? _error;
  bool _loadInProgress = false;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  @override
  void dispose() {
    super.dispose();
  }

  Future<void> _loadData() async {
    _loadInProgress = true;
    final api = ref.read(apiClientProvider);
    try {
      final results = await Future.wait([
        api.dio.get('/api/stats/overview'),
        api.dio.get('/api/auth/me'),
      ]);
      if (mounted) {
        setState(() {
          _stats = results[0].data as Map<String, dynamic>;
          _profile = results[1].data as Map<String, dynamic>;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) setState(() { _loading = false; _error = '$e'; });
    } finally {
      _loadInProgress = false;
    }
  }

  void _reloadIfNeeded() {
    if (!_loadInProgress) _loadData();
  }

  Future<void> _switchStage(String stage) async {
    try {
      final api = ref.read(apiClientProvider);
      await api.dio.put('/api/auth/me/stage', queryParameters: {'stage': stage});
      _loadData(); // 刷新
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    _reloadIfNeeded();

    final auth = ref.watch(authProvider);
    final nickname = _profile?['nickname'] as String? ?? auth.nickname ?? '英语学习者';
    final stage = _stats?['study_stage'] as String? ?? 'college';

    return Scaffold(
      appBar: AppBar(title: const Text('我的')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // ── 头像 + 昵称 ──
                  const CircleAvatar(
                    radius: 40,
                    backgroundColor: Color(0xFF4A90D9),
                    child: Icon(Icons.person, size: 48, color: Colors.white),
                  ),
                  const SizedBox(height: 12),
                  Text(nickname, style: Theme.of(context).textTheme.titleLarge, textAlign: TextAlign.center),
                  const SizedBox(height: 24),

                  // ── 学段切换 ──
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('当前学段', style: TextStyle(fontWeight: FontWeight.w600)),
                          const SizedBox(height: 8),
                          Wrap(
                            spacing: 8,
                            runSpacing: 4,
                            children: [
                              ('elementary', '小学'),
                              ('middle_school', '初中'),
                              ('high_school', '高中'),
                              ('college', '大学'),
                              ('postgraduate', '研究生'),
                              ('overseas', '海思'),
                            ].map((s) {
                              final isSelected = stage == s.$1;
                              return ChoiceChip(
                                label: Text(s.$2),
                                selected: isSelected,
                                onSelected: (_) => _switchStage(s.$1),
                                selectedColor: const Color(0xFF4A90D9).withAlpha(40),
                              );
                            }).toList(),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // ── 学习统计 ──
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('学习统计', style: TextStyle(fontWeight: FontWeight.w600)),
                          const SizedBox(height: 12),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _StatItem(
                                label: '累计词汇',
                                value: '${_stats?['total_vocab'] ?? 0}',
                              ),
                              _StatItem(
                                label: '连续打卡',
                                value: '${_stats?['streak_days'] ?? 0} 天',
                              ),
                              _StatItem(
                                label: '跟读句数',
                                value: '${_stats?['speak_count'] ?? 0}',
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _StatItem(
                                label: '已掌握',
                                value: '${_stats?['mastered_vocab'] ?? 0}',
                              ),
                              _StatItem(
                                label: '每日目标',
                                value: '${_stats?['daily_goal'] ?? 20} 词',
                              ),
                              _StatItem(
                                label: '正确率',
                                value: _calcAccuracy(),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),

                  // ── 功能菜单 ──
                  Card(
                    child: Column(
                      children: [
                        ListTile(
                          leading: const Icon(Icons.favorite_border),
                          title: const Text('收藏'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {},
                        ),
                        const Divider(height: 1),
                        ListTile(
                          leading: const Icon(Icons.error_outline),
                          title: const Text('错题本'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {},
                        ),
                        const Divider(height: 1),
                        ListTile(
                          leading: const Icon(Icons.calendar_month),
                          title: const Text('打卡记录'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {},
                        ),
                        const Divider(height: 1),
                        ListTile(
                          leading: const Icon(Icons.settings),
                          title: const Text('设置'),
                          trailing: const Icon(Icons.chevron_right),
                          onTap: () {},
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  OutlinedButton(
                    onPressed: () => ref.read(authProvider.notifier).logout(),
                    child: const Text('退出登录'),
                  ),
                  const SizedBox(height: 32),
                ],
              ),
            ),
    );
  }

  String _calcAccuracy() {
    final total = _stats?['total_vocab'] as int? ?? 0;
    final mastered = _stats?['mastered_vocab'] as int? ?? 0;
    if (total == 0) return '--';
    return '${(mastered / total * 100).toInt()}%';
  }
}

class _StatItem extends StatelessWidget {
  final String label;
  final String value;
  const _StatItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF4A90D9))),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}
