"""add external_id to question_answers

Revision ID: c2d3e4f5g6h7
Revises: b1a2c3d4e5f6
Create Date: 2026-08-07 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5g6h7'
down_revision: Union[str, Sequence[str], None] = 'b1a2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('question_answers',
        sa.Column('external_id', sa.String(length=255), nullable=True)
    )
    op.create_index(
        op.f('ix_question_answers_external_id'),
        'question_answers',
        ['external_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_question_answers_external_id'), table_name='question_answers')
    op.drop_column('question_answers', 'external_id')
