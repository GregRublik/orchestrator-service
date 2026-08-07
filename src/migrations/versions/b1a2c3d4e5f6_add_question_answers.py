"""add question_answers table

Revision ID: b1a2c3d4e5f6
Revises: fc77d041db20
Create Date: 2026-08-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1a2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'fc77d041db20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('question_answers',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('question_text', sa.Text(), nullable=True),
    sa.Column('product_name', sa.String(length=500), nullable=True),
    sa.Column('product_description', sa.Text(), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('prompt_id', sa.Integer(), nullable=False),
    sa.Column('answer_text', sa.Text(), nullable=True),
    sa.Column('is_read', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_answers_is_read'), 'question_answers', ['is_read'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_question_answers_is_read'), table_name='question_answers')
    op.drop_table('question_answers')
