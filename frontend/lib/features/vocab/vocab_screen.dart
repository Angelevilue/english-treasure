import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'vocab_providers.dart';

class VocabScreen extends ConsumerWidget {
  const VocabScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final banksAsync = ref.watch(wordBanksProvider);
    final flashcardsAsync = ref.watch(flashcardsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('单词速记')),
      body: Column(
        children: [
          // ── 今日任务卡片 ──
          Padding(
            padding: const EdgeInsets.all(16),
            child: flashcardsAsync.when(
              data: (cards) => Card(
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      const Text('今日任务', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          _StatBadge(label: '新学', value: '${cards.where((c) => c.status == 'new').length}', color: Colors.blue),
                          _StatBadge(label: '复习', value: '${cards.where((c) => c.status != 'new').length}', color: Colors.orange),
                          _StatBadge(label: '总计', value: '${cards.length}', color: Colors.green),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: () => _startFlashcard(context, cards),
                          icon: const Icon(Icons.play_arrow),
                          label: const Text('开始闪卡学习'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              loading: () => const Card(child: Padding(padding: EdgeInsets.all(40), child: Center(child: CircularProgressIndicator()))),
              error: (e, _) => Card(child: Padding(padding: EdgeInsets.all(16), child: Text('加载失败: $e'))),
            ),
          ),

          // ── 词库列表 ──
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('词库', style: Theme.of(context).textTheme.titleMedium),
              ],
            ),
          ),
          Expanded(
            child: banksAsync.when(
              data: (banks) => ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                itemCount: banks.length,
                itemBuilder: (_, i) {
                  final b = banks[i];
                  return ListTile(
                    leading: const Icon(Icons.menu_book, color: Color(0xFF4A90D9)),
                    title: Text(b.name),
                    subtitle: Text(_stageLabel(b.stage), style: const TextStyle(fontSize: 12)),
                    trailing: Text('${b.wordCount} 词', style: const TextStyle(color: Colors.grey)),
                    onTap: () {},
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

  void _startFlashcard(BuildContext context, List<FlashcardItem> cards) {
    if (cards.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('暂无待学单词')),
      );
      return;
    }
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => _FlashcardPage(cards: cards)),
    );
  }

  String _stageLabel(String stage) {
    return {
      'elementary': '小学',
      'middle_school': '初中',
      'high_school': '高中',
      'college': '大学',
      'postgraduate': '研究生',
      'overseas': '海思',
    }[stage] ?? stage;
  }
}

// ── 闪卡学习页 ──

class _FlashcardPage extends StatefulWidget {
  final List<FlashcardItem> cards;
  const _FlashcardPage({required this.cards});

  @override
  State<_FlashcardPage> createState() => _FlashcardPageState();
}

class _FlashcardPageState extends State<_FlashcardPage> {
  int _index = 0;
  bool _showBack = false;

  @override
  Widget build(BuildContext context) {
    if (_index >= widget.cards.length) {
      return Scaffold(
        appBar: AppBar(title: const Text('完成！')),
        body: const Center(child: Text('🎉 今日任务完成！', style: TextStyle(fontSize: 24))),
      );
    }

    final card = widget.cards[_index];
    return Scaffold(
      appBar: AppBar(title: Text('${_index + 1} / ${widget.cards.length}')),
      body: GestureDetector(
        onTap: () => setState(() => _showBack = !_showBack),
        child: Center(
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: _showBack ? _cardBack(card) : _cardFront(card),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => setState(() { _index++; _showBack = false; }),
                  child: const Text('不认识'),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: FilledButton(
                  onPressed: () => setState(() { _index++; _showBack = false; }),
                  child: const Text('认识'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _cardFront(FlashcardItem card) {
    return Card(
      key: const ValueKey('front'),
      elevation: 4,
      margin: const EdgeInsets.all(32),
      child: SizedBox(
        width: double.infinity,
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(card.word, style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold)),
              if (card.phonetic != null) ...[
                const SizedBox(height: 8),
                Text(card.phonetic!, style: const TextStyle(fontSize: 18, color: Colors.grey)),
              ],
              const SizedBox(height: 24),
              const Text('点击翻面查看释义', style: TextStyle(color: Colors.grey)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _cardBack(FlashcardItem card) {
    return Card(
      key: const ValueKey('back'),
      elevation: 4,
      margin: const EdgeInsets.all(32),
      child: SizedBox(
        width: double.infinity,
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(card.word, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Text(card.definition, style: const TextStyle(fontSize: 20, color: Color(0xFF4A90D9))),
              if (card.exampleSentence != null) ...[
                const SizedBox(height: 24),
                Text(card.exampleSentence!, style: const TextStyle(fontStyle: FontStyle.italic)),
                if (card.exampleTranslation != null)
                  Text(card.exampleTranslation!, style: const TextStyle(fontSize: 12, color: Colors.grey)),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _StatBadge extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  const _StatBadge({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: color)),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}
