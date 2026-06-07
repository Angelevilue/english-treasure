import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/providers.dart';

// ── 词库列表 ──

class WordBankItem {
  final String id;
  final String name;
  final String stage;
  final int wordCount;
  final String? description;

  WordBankItem({
    required this.id,
    required this.name,
    required this.stage,
    required this.wordCount,
    this.description,
  });

  factory WordBankItem.fromJson(Map<String, dynamic> json) {
    return WordBankItem(
      id: json['id'],
      name: json['name'],
      stage: json['stage'],
      wordCount: json['word_count'],
      description: json['description'],
    );
  }
}

final wordBanksProvider = FutureProvider.autoDispose<List<WordBankItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  final resp = await api.dio.get('/api/vocab/banks');
  final items = (resp.data['items'] as List).map((j) => WordBankItem.fromJson(j)).toList();
  return items;
});

// ── 闪卡 ──

class FlashcardItem {
  final String wordId;
  final String word;
  final String? phonetic;
  final String? audioUrl;
  final String definition;
  final String? exampleSentence;
  final String? exampleTranslation;
  final String status;

  FlashcardItem({
    required this.wordId,
    required this.word,
    this.phonetic,
    this.audioUrl,
    required this.definition,
    this.exampleSentence,
    this.exampleTranslation,
    required this.status,
  });

  factory FlashcardItem.fromJson(Map<String, dynamic> json) {
    return FlashcardItem(
      wordId: json['word_id'],
      word: json['word'],
      phonetic: json['phonetic'],
      audioUrl: json['audio_url'],
      definition: json['definition'],
      exampleSentence: json['example_sentence'],
      exampleTranslation: json['example_translation'],
      status: json['status'],
    );
  }
}

final flashcardsProvider = FutureProvider.autoDispose<List<FlashcardItem>>((ref) async {
  final api = ref.read(apiClientProvider);
  final resp = await api.dio.get('/api/vocab/flashcards', queryParameters: {'limit': 20});
  final items = (resp.data['items'] as List).map((j) => FlashcardItem.fromJson(j)).toList();
  return items;
});
