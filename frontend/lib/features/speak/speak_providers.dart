import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';

// ── 跟读素材 ──

class SpeakMaterialItem {
  final String id;
  final String title;
  final String? description;
  final String category;
  final String accent;
  final String difficulty;
  final String audioUrl;
  final String? coverUrl;
  final int sentenceCount;

  SpeakMaterialItem({
    required this.id,
    required this.title,
    this.description,
    required this.category,
    required this.accent,
    required this.difficulty,
    required this.audioUrl,
    this.coverUrl,
    required this.sentenceCount,
  });

  factory SpeakMaterialItem.fromJson(Map<String, dynamic> json) {
    return SpeakMaterialItem(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      category: json['category'],
      accent: json['accent'],
      difficulty: json['difficulty'],
      audioUrl: json['audio_url'],
      coverUrl: json['cover_url'],
      sentenceCount: json['sentence_count'] ?? 0,
    );
  }
}

class SpeakSentenceItem {
  final String id;
  final String text;
  final String? translation;
  final String? audioUrl;
  final int sortOrder;

  SpeakSentenceItem({
    required this.id,
    required this.text,
    this.translation,
    this.audioUrl,
    required this.sortOrder,
  });

  factory SpeakSentenceItem.fromJson(Map<String, dynamic> json) {
    return SpeakSentenceItem(
      id: json['id'],
      text: json['text'],
      translation: json['translation'],
      audioUrl: json['audio_url'],
      sortOrder: json['sort_order'] ?? 0,
    );
  }
}

final speakMaterialsProvider =
    FutureProvider.autoDispose<List<SpeakMaterialItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  final resp = await api.dio.get('/api/speak/materials');
  final items = (resp.data['items'] as List)
      .map((j) => SpeakMaterialItem.fromJson(j))
      .toList();
  return items;
});

final speakMaterialDetailProvider =
    FutureProvider.family.autoDispose<Map<String, dynamic>, String>(
  (ref, materialId) async {
    final api = ref.read(apiClientProvider);
    final resp = await api.dio.get('/api/speak/materials/$materialId');
    return resp.data as Map<String, dynamic>;
  },
);
