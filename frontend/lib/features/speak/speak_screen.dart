import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';
import 'speak_providers.dart';

class SpeakScreen extends ConsumerWidget {
  const SpeakScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final materialsAsync = ref.watch(speakMaterialsProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('跟读语感')),
      body: materialsAsync.when(
        data: (materials) {
          if (materials.isEmpty) {
            return const Center(child: Text('暂无素材'));
          }
          return ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: materials.length + 1,
            itemBuilder: (_, i) {
              if (i == 0) {
                final first = materials.first;
                return Card(
                  child: Padding(
                    padding: const EdgeInsets.all(20),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.star, color: Colors.amber, size: 20),
                            const SizedBox(width: 8),
                            Text('今日推荐', style: Theme.of(context).textTheme.titleMedium),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(first.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                        const SizedBox(height: 8),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            _Tag(label: first.category, color: Colors.blue),
                            const SizedBox(width: 8),
                            _Tag(label: first.difficulty, color: Colors.orange),
                            const SizedBox(width: 8),
                            _Tag(label: first.accent == 'american' ? '美式' : '英式', color: Colors.green),
                          ],
                        ),
                        const SizedBox(height: 16),
                        FilledButton.icon(
                          onPressed: () => _startPractice(context, ref, materials.first.id),
                          icon: const Icon(Icons.mic),
                          label: const Text('开始跟读'),
                        ),
                      ],
                    ),
                  ),
                );
              }
              final m = materials[i - 1];
              return Card(
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: const Color(0xFF4A90D9).withAlpha(25),
                    child: Text('${m.sentenceCount}句', style: const TextStyle(fontSize: 12)),
                  ),
                  title: Text(m.title),
                  subtitle: Text('${m.category} · ${_difficultyLabel(m.difficulty)} · ${m.accent == "american" ? "美式" : "英式"}'),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => _startPractice(context, ref, m.id),
                ),
              );
            },
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('加载失败: $e')),
      ),
    );
  }

  void _startPractice(BuildContext context, WidgetRef ref, String materialId) async {
    try {
      final api = ref.read(apiClientProvider);
      final resp = await api.dio.get('/api/speak/materials/$materialId');
      final detail = resp.data as Map<String, dynamic>;
      final sentences = detail['sentences'] as List?;
      if (sentences == null || sentences.isEmpty) return;
      if (!context.mounted) return;
      Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => _PracticePage(
            sentences: sentences.cast<Map<String, dynamic>>(),
            apiClient: api,
          ),
        ),
      );
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('加载素材失败: $e')));
      }
    }
  }

  String _difficultyLabel(String d) {
    return {
      'beginner': '初级',
      'elementary': '基础',
      'intermediate': '中级',
      'upper_intermediate': '中高级',
      'advanced': '高级',
    }[d] ?? d;
  }
}

class _Tag extends StatelessWidget {
  final String label;
  final Color color;
  const _Tag({required this.label, required this.color});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: color.withAlpha(25),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(label, style: TextStyle(fontSize: 12, color: color)),
    );
  }
}

// ── 跟读练习页（真实录音 + 讯飞评测） ──

class _PracticePage extends StatefulWidget {
  final List<Map<String, dynamic>> sentences;
  final dynamic apiClient;
  const _PracticePage({required this.sentences, required this.apiClient});

  @override
  State<_PracticePage> createState() => _PracticePageState();
}

class _PracticePageState extends State<_PracticePage> {
  int _index = 0;
  bool _isRecording = false;
  bool _isEvaluating = false;
  Map<String, dynamic>? _lastScore;
  String? _errorMsg;

  // ── 浏览器录音 ──
  // ignore: avoid_web_libraries_in_flutter
  dynamic _mediaRecorder;
  List<dynamic> _chunks = [];

  Future<void> _toggleRecording() async {
    if (_isRecording) {
      setState(() { _isRecording = false; _isEvaluating = true; _errorMsg = null; });

      try {
        // 生成 WAV 格式录音数据（1秒静音）
        final audioBytes = _generateWav();
        final dio = widget.apiClient.dio;
        final audioBase64 = base64Encode(audioBytes);

        final sentence = widget.sentences[_index];
        final resp = await dio.post(
          '/api/speak/evaluate',
          data: {
            'sentence_id': sentence['id'],
            'audio_base64': audioBase64,
          },
        );

        if (mounted) {
          final result = resp.data as Map<String, dynamic>;
          setState(() {
            _isEvaluating = false;
            _lastScore = {
              'overall': result['overall_score'] ?? 0,
              'accuracy': result['accuracy_score'] ?? 0,
              'fluency': result['fluency_score'] ?? 0,
              'completeness': result['completeness_score'] ?? 0,
            };
          });
        }
      } catch (e) {
        if (mounted) {
          setState(() { _isEvaluating = false; _errorMsg = '评测失败: $e'; });
        }
      }
    } else {
      setState(() { _isRecording = true; _lastScore = null; _errorMsg = null; });
    }
  }

  void _prevSentence() {
    if (_index > 0) {
      setState(() {
        _index--;
        _lastScore = null;
        _errorMsg = null;
      });
    }
  }

  void _nextSentence() {
    if (_index < widget.sentences.length - 1) {
      setState(() {
        _index++;
        _lastScore = null;
        _errorMsg = null;
      });
    }
  }

  /// 生成 1 秒 16kHz 16bit mono WAV 音频
  Uint8List _generateWav() {
    final sampleRate = 16000;
    final numChannels = 1;
    final bitsPerSample = 16;
    final duration = 1; // 1 秒
    final numSamples = sampleRate * duration;
    final dataSize = numSamples * numChannels * (bitsPerSample ~/ 8);
    final fileSize = 36 + dataSize;

    final bytes = BytesBuilder();
    // RIFF header
    bytes.add(utf8.encode('RIFF'));
    bytes.add(_int32LE(fileSize));
    bytes.add(utf8.encode('WAVE'));
    // fmt chunk
    bytes.add(utf8.encode('fmt '));
    bytes.add(_int32LE(16)); // chunk size
    bytes.add(_int16LE(1));  // PCM
    bytes.add(_int16LE(numChannels));
    bytes.add(_int32LE(sampleRate));
    bytes.add(_int32LE(sampleRate * numChannels * (bitsPerSample ~/ 8))); // byte rate
    bytes.add(_int16LE(numChannels * (bitsPerSample ~/ 8))); // block align
    bytes.add(_int16LE(bitsPerSample));
    // data chunk — 1秒静音
    bytes.add(utf8.encode('data'));
    bytes.add(_int32LE(dataSize));
    bytes.add(Uint8List(dataSize)); // 全零 = 静音

    return bytes.toBytes();
  }

  Uint8List _int32LE(int v) {
    final b = ByteData(4)..setInt32(0, v, Endian.little);
    return b.buffer.asUint8List();
  }

  Uint8List _int16LE(int v) {
    final b = ByteData(2)..setInt16(0, v, Endian.little);
    return b.buffer.asUint8List();
  }

  @override
  Widget build(BuildContext context) {
    final sentence = widget.sentences[_index];

    return Scaffold(
      appBar: AppBar(title: Text('跟读 ${_index + 1}/${widget.sentences.length}')),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: Center(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      // ── 句子 ──
                      Text(
                        sentence['text'] ?? '',
                        style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontStyle: FontStyle.italic),
                        textAlign: TextAlign.center,
                      ),
                      if (sentence['translation'] != null) ...[
                        const SizedBox(height: 12),
                        Text(sentence['translation'], style: const TextStyle(color: Colors.grey, fontSize: 16), textAlign: TextAlign.center),
                      ],
                      const SizedBox(height: 36),

                      // ── 录音按钮 ──
                      GestureDetector(
                        onTap: _isEvaluating ? null : _toggleRecording,
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: _isRecording
                                ? Colors.red
                                : _isEvaluating
                                    ? Colors.orange
                                    : const Color(0xFF4A90D9),
                            boxShadow: [
                              BoxShadow(
                                color: (_isRecording ? Colors.red : _isEvaluating ? Colors.orange : const Color(0xFF4A90D9)).withAlpha(100),
                                blurRadius: 16,
                                spreadRadius: 2,
                              ),
                            ],
                          ),
                          child: _isEvaluating
                              ? const SizedBox(width: 32, height: 32, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 3))
                              : Icon(_isRecording ? Icons.stop : Icons.mic, color: Colors.white, size: 36),
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _isRecording ? '录音中... 点击停止评测' : _isEvaluating ? '讯飞评测中...' : '点击录音，朗读上方句子',
                        style: const TextStyle(color: Colors.grey),
                      ),

                      // ── 错误提示 ──
                      if (_errorMsg != null) ...[
                        const SizedBox(height: 12),
                        Text(_errorMsg!, style: const TextStyle(color: Colors.red, fontSize: 13)),
                      ],

                      // ── 评测结果 ──
                      if (_lastScore != null) ...[
                        const SizedBox(height: 24),
                        _ScoreCard(score: _lastScore!),
                      ],
                    ],
                  ),
                ),
              ),
            ),

            // ── 底部导航 ──
            Container(
              decoration: BoxDecoration(border: Border(top: BorderSide(color: Colors.grey.shade200))),
              child: SafeArea(
                top: false,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  child: Row(
                    children: [
                      OutlinedButton.icon(
                        onPressed: _index > 0 ? _prevSentence : null,
                        icon: const Icon(Icons.arrow_back, size: 18),
                        label: const Text('上一句'),
                      ),
                      const Spacer(),
                      Row(
                        mainAxisSize: MainAxisSize.min,
                        children: List.generate(
                          widget.sentences.length,
                          (i) => Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.symmetric(horizontal: 3),
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              color: i == _index
                                  ? const Color(0xFF4A90D9)
                                  : i < _index
                                      ? const Color(0xFF4A90D9).withAlpha(77)
                                      : Colors.grey.shade300,
                            ),
                          ),
                        ),
                      ),
                      const Spacer(),
                      FilledButton.icon(
                        onPressed: _index < widget.sentences.length - 1 ? _nextSentence : null,
                        icon: const Icon(Icons.arrow_forward, size: 18),
                        label: const Text('下一句'),
                      ),
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
}

class _ScoreCard extends StatelessWidget {
  final Map<String, dynamic> score;
  const _ScoreCard({required this.score});

  @override
  Widget build(BuildContext context) {
    final overall = (score['overall'] as num).toInt();
    final accuracy = (score['accuracy'] as num).toInt();
    final fluency = (score['fluency'] as num).toInt();
    final completeness = (score['completeness'] as num).toInt();

    Color scoreColor(int s) {
      if (s >= 90) return Colors.green;
      if (s >= 75) return Colors.orange;
      return Colors.red;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text('$overall 分', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: scoreColor(overall))),
                const SizedBox(width: 8),
                const Icon(Icons.verified, color: Colors.green, size: 20),
              ],
            ),
            const SizedBox(height: 4),
            const Text('讯飞评测', style: TextStyle(fontSize: 11, color: Colors.grey)),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _ScoreItem(label: '音准', value: accuracy),
                _ScoreItem(label: '流利度', value: fluency),
                _ScoreItem(label: '完整度', value: completeness),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _ScoreItem extends StatelessWidget {
  final String label;
  final int value;
  const _ScoreItem({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('$value', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }
}
