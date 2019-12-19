"""Update event duration field

Revision ID: 6cb2954b8582
Revises: c8b5fda83a1a
Create Date: 2019-12-19 16:34:37.619942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6cb2954b8582'
down_revision = 'c8b5fda83a1a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('duration',
               existing_type=sa.DATETIME(),
               type_=sa.Interval(),
               existing_nullable=False)

    with op.batch_alter_table('event_template', schema=None) as batch_op:
        batch_op.alter_column('duration',
               existing_type=sa.DATETIME(),
               type_=sa.Interval(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event_template', schema=None) as batch_op:
        batch_op.alter_column('duration',
               existing_type=sa.Interval(),
               type_=sa.DATETIME(),
               existing_nullable=False)

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('duration',
               existing_type=sa.Interval(),
               type_=sa.DATETIME(),
               existing_nullable=False)

    # ### end Alembic commands ###
