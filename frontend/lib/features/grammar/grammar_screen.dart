import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import 'grammar_providers.dart';

class GrammarScreen extends ConsumerStatefulWidget {
  const GrammarScreen({super.key});

  @override
  ConsumerState<GrammarScreen> createState() => _GrammarScreenState();
}

class _GrammarScreenState extends ConsumerState<GrammarScreen> {
  final _textCtrl = TextEditingController();
  bool _isAnalyzing = false;

  Future<void> _analyze() async {
    if (_textCtrl.text.trim().isEmpty) return;
    setState(() => _isAnalyzing = true);
    try {
      final api = ref.read(apiClientProvider);
      final resp = await api.dio.post('/api/grammar/analyze', data: {
        'text': _textCtrl.text.trim(),
        'mode': 'analyze',
      });
      if (mounted) {
        final result = resp.data['result'] as Map<String, dynamic>;
        _showResultDialog(result);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('分析失败: $e')));
      }
    } finally {
      if (mounted) setState(() => _isAnalyzing = false);
    }
  }

  void _showResultDialog(Map<String, dynamic> result) {
    showDialog(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: const Text('AI 语法分析'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              if (result['translation'] != null)
                Text('翻译: ${result['translation']}', style: const TextStyle(color: Colors.grey)),
              const SizedBox(height: 12),
              if (result['tense'] != null) Text('时态: ${result['tense']}'),
              if (result['voice'] != null) Text('语态: ${result['voice']}'),
              const SizedBox(height: 8),
              if (result['components'] != null) ...[
                const Text('成分分析:', style: TextStyle(fontWeight: FontWeight.bold)),
                ...(result['components'] as List).map((c) => Padding(
                      padding: const EdgeInsets.only(left: 8, top: 4),
                      child: Text('${c['role']}: ${c['text']}'),
                    )),
              ],
              if (result['notes'] != null) ...[
                const SizedBox(height: 8),
                ...(result['notes'] as List).map((n) => Text('💡 $n')),
              ],
              if (result['parse_error'] == true)
                Text('原始输出:\n${result['raw_output']}', style: const TextStyle(fontSize: 10, color: Colors.grey)),
            ],
          ),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(dialogCtx), child: const Text('关闭'))],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final topicsAsync = ref.watch(grammarTopicsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('语法分析')),
      body: Column(
        children: [
          // ── AI 分析输入 ──
          Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('AI 语法分析', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _textCtrl,
                      maxLines: 3,
                      decoration: const InputDecoration(
                        hintText: '输入或粘贴英文句子...\n例如: The book that I borrowed yesterday is very interesting.',
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: FilledButton.icon(
                        onPressed: _isAnalyzing ? null : _analyze,
                        icon: _isAnalyzing
                            ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                            : const Icon(Icons.auto_awesome),
                        label: Text(_isAnalyzing ? 'DeepSeek 分析中...' : '语法分析'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ── 语法知识库 ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('语法知识库', style: Theme.of(context).textTheme.titleMedium),
                TextButton(onPressed: () {}, child: const Text('搜索')),
              ],
            ),
          ),
          Expanded(
            child: topicsAsync.when(
              data: (topics) => ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: topics.length,
                itemBuilder: (_, i) {
                  final t = topics[i];
                  return ExpansionTile(
                    leading: const Icon(Icons.menu_book, color: Color(0xFF4A90D9)),
                    title: Text(t.title),
                    subtitle: Text('${t.children.length} 节'),
                    children: t.children.map((c) => ListTile(
                      title: Text(c.title),
                      onTap: () => _showTopicDetail(context, c),
                    )).toList(),
                  );
                },
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('加载失败: $e')),
            ),
          ),
        ],
      ),
    );
  }

  void _showTopicDetail(BuildContext context, GrammarTopicNode topic) {
    showDialog(
      context: context,
      builder: (dialogCtx) => AlertDialog(
        title: Text(topic.title),
        content: SingleChildScrollView(
          child: Text(topic.content),
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(dialogCtx), child: const Text('关闭'))],
      ),
    );
  }
}
