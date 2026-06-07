"""init

Revision ID: 001
Revises: 
Create Date: 2026-06-05
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('phone', sa.String(20), unique=True, nullable=True),
        sa.Column('wechat_openid', sa.String(128), unique=True, nullable=True),
        sa.Column('hashed_password', sa.String(128), nullable=True),
        sa.Column('nickname', sa.String(50), default='英语学习者'),
        sa.Column('avatar_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── user_profiles ──
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True),
        sa.Column('study_stage', sa.Enum('elementary', 'middle_school', 'high_school', 'college', 'postgraduate', 'overseas', name='studystage'), default='college'),
        sa.Column('daily_goal_words', sa.Integer(), default=20),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── word_banks ──
    op.create_table(
        'word_banks',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('stage', sa.Enum('elementary', 'middle_school', 'high_school', 'college', 'postgraduate', 'overseas', name='studystage')),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('word_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── words ──
    op.create_table(
        'words',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('word_bank_id', sa.String(36), sa.ForeignKey('word_banks.id', ondelete='CASCADE')),
        sa.Column('word', sa.String(100)),
        sa.Column('phonetic', sa.String(100), nullable=True),
        sa.Column('audio_url', sa.String(512), nullable=True),
        sa.Column('definition', sa.Text()),
        sa.Column('example_sentence', sa.Text(), nullable=True),
        sa.Column('example_translation', sa.Text(), nullable=True),
        sa.Column('part_of_speech', sa.String(30), nullable=True),
        sa.Column('difficulty', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── user_word_progress ──
    op.create_table(
        'user_word_progress',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('word_id', sa.String(36), sa.ForeignKey('words.id', ondelete='CASCADE')),
        sa.Column('ease_factor', sa.Float(), default=2.5),
        sa.Column('interval', sa.Integer(), default=0),
        sa.Column('repetitions', sa.Integer(), default=0),
        sa.Column('status', sa.Enum('new', 'learning', 'review', 'mastered', name='wordstatus'), default='new'),
        sa.Column('next_review_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_review_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('correct_count', sa.Integer(), default=0),
        sa.Column('incorrect_count', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── grammar_topics ──
    op.create_table(
        'grammar_topics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('parent_id', sa.String(36), sa.ForeignKey('grammar_topics.id', ondelete='SET NULL'), nullable=True),
        sa.Column('title', sa.String(200)),
        sa.Column('content', sa.Text()),
        sa.Column('common_errors', sa.Text(), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── grammar_analysis_records ──
    op.create_table(
        'grammar_analysis_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('input_text', sa.Text()),
        sa.Column('analysis_result', sa.Text()),
        sa.Column('mode', sa.String(20), default='analyze'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── speak_materials ──
    op.create_table(
        'speak_materials',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('title', sa.String(200)),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50)),
        sa.Column('accent', sa.Enum('american', 'british', name='accenttype'), default='american'),
        sa.Column('difficulty', sa.Enum('beginner', 'elementary', 'intermediate', 'upper_intermediate', 'advanced', name='difficultylevel'), default='intermediate'),
        sa.Column('audio_url', sa.String(512)),
        sa.Column('cover_url', sa.String(512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # ── speak_sentences ──
    op.create_table(
        'speak_sentences',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('material_id', sa.String(36), sa.ForeignKey('speak_materials.id', ondelete='CASCADE')),
        sa.Column('text', sa.Text()),
        sa.Column('translation', sa.Text(), nullable=True),
        sa.Column('audio_url', sa.String(512), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
    )

    # ── speak_records ──
    op.create_table(
        'speak_records',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('material_id', sa.String(36), sa.ForeignKey('speak_materials.id', ondelete='SET NULL'), nullable=True),
        sa.Column('sentence_id', sa.String(36), sa.ForeignKey('speak_sentences.id', ondelete='SET NULL'), nullable=True),
        sa.Column('audio_url', sa.String(512), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('overall_score', sa.Float(), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('fluency_score', sa.Float(), nullable=True),
        sa.Column('completeness_score', sa.Float(), nullable=True),
        sa.Column('phoneme_detail', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('speak_records')
    op.drop_table('speak_sentences')
    op.drop_table('speak_materials')
    op.drop_table('grammar_analysis_records')
    op.drop_table('grammar_topics')
    op.drop_table('user_word_progress')
    op.drop_table('words')
    op.drop_table('word_banks')
    op.drop_table('user_profiles')
    op.drop_table('users')
    op.execute('DROP TYPE IF EXISTS studystage')
    op.execute('DROP TYPE IF EXISTS wordstatus')
    op.execute('DROP TYPE IF EXISTS accenttype')
    op.execute('DROP TYPE IF EXISTS difficultylevel')
