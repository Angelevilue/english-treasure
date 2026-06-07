import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';

/// 选择模式 — 四选一限时答题
class QuizScreen extends ConsumerStatefulWidget {
  const QuizScreen({super.key});

  @override
  ConsumerState<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends ConsumerState<QuizScreen> {
  List<Map<String, dynamic>> _questions = [];
  int _currentIndex = 0;
  int _timerSeconds = 8;
  Timer? _timer;
  bool _answered = false;
  int? _selectedIndex;
  bool _loading = true;
  String? _error;

  // 成绩统计
  int _correctCount = 0;
  List<Map<String, dynamic>> _wrongList = [];
  bool _finished = false;

  @override
  void initState() {
    super.initState();
    _loadQuiz();
  }

  Future<void> _loadQuiz() async {
    try {
      final api = ref.read(apiClientProvider);
      final resp = await api.dio.get('/api/vocab/quiz', queryParameters: {
        'mode': 'en2cn',
        'count': 10,
      });
      if (mounted) {
        setState(() {
          _questions = (resp.data['questions'] as List).cast<Map<String, dynamic>>();
          _loading = false;
        });
        _startTimer();
      }
    } catch (e) {
      if (mounted) {
        setState(() { _loading = false; _error = '加载题目失败: $e'; });
      }
    }
  }

  void _startTimer() {
    _timer?.cancel();
    _timerSeconds = 8;
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!mounted) { timer.cancel(); return; }
      setState(() => _timerSeconds--);
      if (_timerSeconds <= 0) {
        timer.cancel();
        if (!_answered) _handleTimeout();
      }
    });
  }

  void _handleTimeout() {
    setState(() { _answered = true; _selectedIndex = -1; });
    _recordAnswer(false);
    _nextQuestion();
  }

  void _handleSelect(int index) {
    if (_answered) return;
    _timer?.cancel();
    setState(() { _answered = true; _selectedIndex = index; });

    final q = _questions[_currentIndex];
    final correct = index == q['correct_index'];
    _recordAnswer(correct);
    _nextQuestion();
  }

  void _recordAnswer(bool correct) {
    if (correct) {
      _correctCount++;
    } else {
      _wrongList.add(_questions[_currentIndex]);
    }
  }

  void _nextQuestion() {
    Future.delayed(const Duration(milliseconds: 1200), () {
      if (!mounted) return;
      if (_currentIndex + 1 >= _questions.length) {
        // 提交结果
        _submitResults();
        setState(() { _finished = true; });
      } else {
        setState(() {
          _currentIndex++;
          _answered = false;
          _selectedIndex = null;
        });
        _startTimer();
      }
    });
  }

  Future<void> _submitResults() async {
    try {
      final api = ref.read(apiClientProvider);
      final answers = _questions.map((q) => {
        'word_id': q['word_id'],
        'correct': !_wrongList.any((w) => w['word_id'] == q['word_id']),
      }).toList();
      await api.dio.post('/api/vocab/quiz/submit', data: {'answers': answers});
    } catch (_) {}
  }

  void _restart() {
    setState(() {
      _currentIndex = 0;
      _correctCount = 0;
      _wrongList = [];
      _finished = false;
      _answered = false;
      _selectedIndex = null;
      _loading = true;
      _error = null;
    });
    _loadQuiz();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('选择模式')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('选择模式')),
        body: Center(child: Text(_error!, style: const TextStyle(color: Colors.red))),
      );
    }

    if (_finished) {
      return _buildResultPage();
    }

    final q = _questions[_currentIndex];
    final progress = (_currentIndex + 1) / _questions.length;

    return Scaffold(
      appBar: AppBar(
        title: Text('选择模式 ${_currentIndex + 1}/${_questions.length}'),
        automaticallyImplyLeading: false,
      ),
      body: SafeArea(
        child: Column(
          children: [
            // ── 倒计时进度条 ──
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: [
                  Expanded(
                    child: ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: LinearProgressIndicator(
                        value: progress,
                        minHeight: 6,
                        backgroundColor: Colors.grey.shade200,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  _TimerBadge(seconds: _timerSeconds),
                ],
              ),
            ),

            const Divider(),

            // ── 题目 ──
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        q['question'] ?? '',
                        style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: const Color(0xFF4A90D9),
                            ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '选择正确的中文释义',
                        style: TextStyle(color: Colors.grey.shade500, fontSize: 13),
                      ),
                      const SizedBox(height: 40),

                      // ── 四个选项 ──
                      ...List.generate(4, (i) {
                        final option = (q['options'] as List)[i] ?? '';
                        final isCorrect = i == q['correct_index'];
                        final isSelected = i == _selectedIndex;

                        Color bgColor = Colors.white;
                        Color borderColor = Colors.grey.shade300;
                        Color textColor = Colors.black87;

                        if (_answered) {
                          if (isCorrect) {
                            bgColor = Colors.green.shade50;
                            borderColor = Colors.green;
                            textColor = Colors.green.shade700;
                          } else if (isSelected && !isCorrect) {
                            bgColor = Colors.red.shade50;
                            borderColor = Colors.red;
                            textColor = Colors.red.shade700;
                          }
                        }

                        return Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: GestureDetector(
                            onTap: _answered ? null : () => _handleSelect(i),
                            child: AnimatedContainer(
                              duration: const Duration(milliseconds: 200),
                              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                              decoration: BoxDecoration(
                                color: bgColor,
                                border: Border.all(color: borderColor, width: 1.5),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Row(
                                children: [
                                  Container(
                                    width: 28,
                                    height: 28,
                                    decoration: BoxDecoration(
                                      shape: BoxShape.circle,
                                      color: _answered && isCorrect
                                          ? Colors.green
                                          : _answered && isSelected && !isCorrect
                                              ? Colors.red
                                              : Colors.grey.shade200,
                                    ),
                                    child: Center(
                                      child: Text(
                                        ['A', 'B', 'C', 'D'][i],
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          color: _answered && (isCorrect || isSelected)
                                              ? Colors.white
                                              : Colors.grey.shade600,
                                        ),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 16),
                                  Expanded(
                                    child: Text(
                                      option,
                                      style: TextStyle(fontSize: 16, color: textColor),
                                    ),
                                  ),
                                  if (_answered && isCorrect)
                                    const Icon(Icons.check_circle, color: Colors.green),
                                  if (_answered && isSelected && !isCorrect)
                                    const Icon(Icons.cancel, color: Colors.red),
                                ],
                              ),
                            ),
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultPage() {
    final accuracy = _questions.isEmpty
        ? 0.0
        : (_correctCount / _questions.length * 100);
    final emoji = accuracy >= 90 ? '🏆' : accuracy >= 70 ? '👍' : accuracy >= 50 ? '💪' : '📚';

    return Scaffold(
      appBar: AppBar(title: const Text('答题结果'), automaticallyImplyLeading: false),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              const SizedBox(height: 20),
              Text(emoji, style: const TextStyle(fontSize: 64)),
              const SizedBox(height: 16),
              Text(
                '${accuracy.toInt()} 分',
                style: TextStyle(
                  fontSize: 48,
                  fontWeight: FontWeight.bold,
                  color: accuracy >= 70 ? Colors.green : Colors.orange,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                '答对 $_correctCount / ${_questions.length} 题',
                style: const TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 32),

              // ── 错词列表 ──
              if (_wrongList.isNotEmpty) ...[
                const Text('错题复习', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
                const SizedBox(height: 12),
                ..._wrongList.map((w) => Card(
                      child: ListTile(
                        leading: const Icon(Icons.error_outline, color: Colors.red),
                        title: Text(w['question'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                        subtitle: Text('正确答案: ${w['correct_answer'] ?? ''}', style: const TextStyle(color: Colors.green)),
                      ),
                    )),
              ],

              const SizedBox(height: 32),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => Navigator.pop(context),
                      icon: const Icon(Icons.arrow_back),
                      label: const Text('返回'),
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: FilledButton.icon(
                      onPressed: _restart,
                      icon: const Icon(Icons.refresh),
                      label: const Text('再来一组'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _TimerBadge extends StatelessWidget {
  final int seconds;
  const _TimerBadge({required this.seconds});

  @override
  Widget build(BuildContext context) {
    final color = seconds <= 3 ? Colors.red : seconds <= 5 ? Colors.orange : const Color(0xFF4A90D9);
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: color.withAlpha(30),
        border: Border.all(color: color, width: 2),
      ),
      child: Center(
        child: Text(
          '$seconds',
          style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 16),
        ),
      ),
    );
  }
}
