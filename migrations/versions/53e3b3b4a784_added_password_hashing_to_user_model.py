"""Added password hashing to User model

Revision ID: 53e3b3b4a784
Revises: 3b4723ab8718
Create Date: 2025-02-09 18:52:55.179196

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53e3b3b4a784'
down_revision = '3b4723ab8718'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password_hash', sa.String(length=256), nullable=True))

    op.drop_column('user', 'password')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('password', sa.VARCHAR(length=60), autoincrement=False, nullable=False))
    op.drop_column('user', 'password_hash')
    # ### end Alembic commands ###
