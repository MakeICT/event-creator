"""events table

Revision ID: fe42fb19ee33
Revises: 
Create Date: 2019-08-05 17:37:39.659242

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fe42fb19ee33'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('authorization',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=40), nullable=False),
    sa.Column('wa_group_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    sa.UniqueConstraint('wa_group_id')
    )
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('instructor_email', sa.String(length=120), nullable=True),
    sa.Column('instructor_name', sa.String(length=60), nullable=True),
    sa.Column('location', sa.String(length=120), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=True),
    sa.Column('description', sa.String(length=500), nullable=False),
    sa.Column('min_age', sa.Integer(), nullable=True),
    sa.Column('max_age', sa.Integer(), nullable=True),
    sa.Column('registration_limit', sa.Integer(), nullable=True),
    sa.Column('member_price', sa.Float(), nullable=True),
    sa.Column('nonmember_price', sa.Float(), nullable=True),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('updated_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('association',
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('authorization_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['authorization_id'], ['authorization.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('association')
    op.drop_table('event')
    op.drop_table('authorization')
    # ### end Alembic commands ###
