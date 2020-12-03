"""add event tags

Revision ID: e3f86a9d05cb
Revises: 3b76d4e76aad
Create Date: 2019-12-22 11:29:29.169735

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f86a9d05cb'
down_revision = '3b76d4e76aad'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tag',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event_tags',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], )
    )
    op.create_table('event_template_tags',
    sa.Column('tag_id', sa.Integer(), nullable=True),
    sa.Column('event_template_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_template_id'], ['event_template.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], )
    )
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

    op.drop_table('event_template_tags')
    op.drop_table('event_tags')
    op.drop_table('tag')
    # ### end Alembic commands ###