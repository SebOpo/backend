"""user registration and password renewal tokens

Revision ID: 6055a1941c2a
Revises: 84f620c1240d
Create Date: 2022-10-16 21:11:26.335228

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6055a1941c2a'
down_revision = '84f620c1240d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    # op.drop_table('spatial_ref_sys')
    op.add_column('user', sa.Column('registration_token', sa.String(), nullable=True))
    op.add_column('user', sa.Column('registration_token_expires', sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('password_renewal_token', sa.String(), nullable=True))
    op.add_column('user', sa.Column('password_renewal_token_expires', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'password_renewal_token_expires')
    op.drop_column('user', 'password_renewal_token')
    op.drop_column('user', 'registration_token_expires')
    op.drop_column('user', 'registration_token')
    op.create_table('spatial_ref_sys',
    sa.Column('srid', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('auth_name', sa.VARCHAR(length=256), autoincrement=False, nullable=True),
    sa.Column('auth_srid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('srtext', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.Column('proj4text', sa.VARCHAR(length=2048), autoincrement=False, nullable=True),
    sa.CheckConstraint('(srid > 0) AND (srid <= 998999)', name='spatial_ref_sys_srid_check'),
    sa.PrimaryKeyConstraint('srid', name='spatial_ref_sys_pkey')
    )
    # ### end Alembic commands ###
