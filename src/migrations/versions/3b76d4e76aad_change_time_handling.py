"""Change time handling

Revision ID: 3b76d4e76aad
Revises: 6cb2954b8582
Create Date: 2019-12-20 15:01:02.873295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b76d4e76aad'
down_revision = '6cb2954b8582'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('host_email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('host_name', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('start_time', sa.Time(), nullable=True))
        batch_op.alter_column('duration',
               existing_type=sa.DATETIME(),
               type_=sa.Interval(),
               existing_nullable=False)
        batch_op.alter_column('start_date',
               existing_type=sa.DATETIME(),
               type_=sa.Date(),
               existing_nullable=True)

    with op.batch_alter_table('event_template', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_time', sa.Time(), nullable=True))
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
        batch_op.drop_column('start_time')

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('start_date',
               existing_type=sa.Date(),
               type_=sa.DATETIME(),
               existing_nullable=True)
        batch_op.alter_column('duration',
               existing_type=sa.Interval(),
               type_=sa.DATETIME(),
               existing_nullable=False)
        batch_op.drop_column('start_time')
        batch_op.drop_column('host_name')
        batch_op.drop_column('host_email')

    # ### end Alembic commands ###