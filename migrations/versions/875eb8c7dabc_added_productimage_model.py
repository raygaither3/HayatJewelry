"""Added ProductImage model

Revision ID: 875eb8c7dabc
Revises: 17251aa2a5d9
Create Date: 2025-04-26 22:43:41.881790

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '875eb8c7dabc'
down_revision = '17251aa2a5d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('product_image',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('image_url', sa.String(length=200), nullable=False),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('product_picture')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('product_picture', sa.VARCHAR(length=1000), nullable=False))

    op.drop_table('product_image')
    # ### end Alembic commands ###
