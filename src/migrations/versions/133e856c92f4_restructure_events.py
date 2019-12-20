"""resctructure event tables to make them more reusable

Revision ID: 133e856c92f4
Revises: 2c925cd4bbb2
Create Date: 2019-12-19 15:47:47.505710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '133e856c92f4'
down_revision = '2c925cd4bbb2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event_template',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=True),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.Column('event_type', sa.Enum('event', '_class', 'reservation', name='eventtype'), nullable=False),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=4000), nullable=False),
    sa.Column('host_email', sa.String(length=120), nullable=True),
    sa.Column('host_name', sa.String(length=60), nullable=True),
    sa.Column('location', sa.String(length=120), nullable=True),
    sa.Column('duration', sa.Interval(), nullable=False),
    sa.Column('image_file', sa.String(length=20), nullable=True),
    sa.Column('min_age', sa.Integer(), nullable=True),
    sa.Column('max_age', sa.Integer(), nullable=True),
    sa.Column('registration_limit', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('event_authorization',
    sa.Column('authorization_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['authorization_id'], ['authorization.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], )
    )
    op.create_table('event_resources',
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], )
    )
    op.create_table('event_template_authorization',
    sa.Column('authorization_id', sa.Integer(), nullable=True),
    sa.Column('event_template_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['authorization_id'], ['authorization.id'], ),
    sa.ForeignKeyConstraint(['event_template_id'], ['event_template.id'], )
    )
    op.create_table('event_template_platform',
    sa.Column('platform_id', sa.Integer(), nullable=True),
    sa.Column('event_template_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_template_id'], ['event_template.id'], ),
    sa.ForeignKeyConstraint(['platform_id'], ['platform.id'], )
    )
    op.create_table('event_template_price',
    sa.Column('price_id', sa.Integer(), nullable=True),
    sa.Column('event_template_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_template_id'], ['event_template.id'], ),
    sa.ForeignKeyConstraint(['price_id'], ['price.id'], )
    )
    op.create_table('event_template_resources',
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('event_template_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_template_id'], ['event_template.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], )
    )
    op.drop_table('event_resource')
    op.drop_table('association')
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cancelled_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('decision_date', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('duration', sa.Interval(), nullable=False))
        batch_op.add_column(sa.Column('host_email', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('host_name', sa.String(length=60), nullable=True))
        batch_op.add_column(sa.Column('submission_date', sa.DateTime(), nullable=True))
        batch_op.drop_column('host_email')
        batch_op.drop_column('end_date')
        batch_op.drop_column('host_name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('event', schema=None) as batch_op:
        batch_op.add_column(sa.Column('host_name', sa.VARCHAR(length=60), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.DATETIME(), nullable=True))
        batch_op.add_column(sa.Column('host_email', sa.VARCHAR(length=120), nullable=True))
        batch_op.drop_column('submission_date')
        batch_op.drop_column('host_name')
        batch_op.drop_column('host_email')
        batch_op.drop_column('duration')
        batch_op.drop_column('decision_date')
        batch_op.drop_column('cancelled_date')

    op.create_table('association',
    sa.Column('event_id', sa.INTEGER(), nullable=True),
    sa.Column('authorization_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['authorization_id'], ['authorization.id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], )
    )
    op.create_table('event_resource',
    sa.Column('event_id', sa.INTEGER(), nullable=True),
    sa.Column('resource_id', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['resource_id'], ['resource.id'], )
    )
    op.drop_table('event_template_resources')
    op.drop_table('event_template_price')
    op.drop_table('event_template_platform')
    op.drop_table('event_template_authorization')
    op.drop_table('event_resources')
    op.drop_table('event_authorization')
    op.drop_table('event_template')
    # ### end Alembic commands ###