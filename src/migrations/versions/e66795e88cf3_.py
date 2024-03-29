"""empty message

Revision ID: e66795e88cf3
Revises: e3f86a9d05cb
Create Date: 2021-06-17 12:23:22.010226

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'e66795e88cf3'
down_revision = 'e3f86a9d05cb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('authorization', schema=None) as batch_op:
        batch_op.drop_index('name')

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('image_file',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=40),
               existing_nullable=True)

    with op.batch_alter_table('event_template', schema=None) as batch_op:
        batch_op.alter_column('image_file',
               existing_type=mysql.VARCHAR(length=20),
               type_=sa.String(length=40),
               existing_nullable=True)

    with op.batch_alter_table('external_event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('has_registration', sa.Boolean(), nullable=True))

    with op.batch_alter_table('resource', schema=None) as batch_op:
        batch_op.drop_index('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('resource', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=True)

    with op.batch_alter_table('external_event', schema=None) as batch_op:
        batch_op.drop_column('has_registration')

    with op.batch_alter_table('event_template', schema=None) as batch_op:
        batch_op.alter_column('image_file',
               existing_type=sa.String(length=40),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=True)

    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.alter_column('image_file',
               existing_type=sa.String(length=40),
               type_=mysql.VARCHAR(length=20),
               existing_nullable=True)

    with op.batch_alter_table('authorization', schema=None) as batch_op:
        batch_op.create_index('name', ['name'], unique=True)

    # ### end Alembic commands ###
