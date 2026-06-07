import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';

// ── 语法知识库 ──

class GrammarTopicNode {
  final String id;
  final String title;
  final String content;
  final String? commonErrors;
  final List<GrammarTopicNode> children;

  GrammarTopicNode({
    required this.id,
    required this.title,
    required this.content,
    this.commonErrors,
    this.children = const [],
  });

  factory GrammarTopicNode.fromJson(Map<String, dynamic> json) {
    return GrammarTopicNode(
      id: json['id'],
      title: json['title'],
      content: json['content'],
      commonErrors: json['common_errors'],
      children: (json['children'] as List?)
              ?.map((c) => GrammarTopicNode.fromJson(c))
              .toList() ??
          [],
    );
  }
}

final grammarTopicsProvider = FutureProvider.autoDispose<List<GrammarTopicNode>>((ref) async {
  final api = ref.read(apiClientProvider);
  final resp = await api.dio.get('/api/grammar/topics');
  final topics = (resp.data['topics'] as List)
      .map((j) => GrammarTopicNode.fromJson(j))
      .toList();
  return topics;
});

// ── AI 分析 ──

final grammarAnalysisProvider =
    FutureProvider.family.autoDispose<Map<String, dynamic>, String>(
  (ref, text) async {
    final api = ref.read(apiClientProvider);
    final resp = await api.dio.post('/api/grammar/analyze', data: {
      'text': text,
      'mode': 'analyze',
    });
    return resp.data['result'] as Map<String, dynamic>;
  },
);
