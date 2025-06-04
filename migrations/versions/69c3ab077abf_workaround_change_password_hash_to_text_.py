"""Workaround: change password_hash to Text in SQLite"""

revision = '69c3ab077abf'
down_revision = '3094e2378b64'  # ← adjust if this isn't your actual last revision
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Rename old table
    op.rename_table('customer', 'customer_old')

    # Create new table with updated password_hash column as Text
    op.create_table(
        'customer',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(150), unique=True, nullable=False),
        sa.Column('username', sa.String(150), unique=True, nullable=False),
        sa.Column('password_hash', sa.Text, nullable=False),  # ← CHANGED TO Text
        sa.Column('phone_number', sa.String(100)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    # Migrate data
    op.execute("""
        INSERT INTO customer (id, email, username, password_hash, phone_number, created_at, updated_at)
        SELECT id, email, username, password_hash, phone_number, created_at, updated_at
        FROM customer_old
    """)

    # Drop old table
    op.drop_table('customer_old')

def downgrade():
    # Do the reverse (if needed)
    op.rename_table('customer', 'customer_new')

    op.create_table(
        'customer',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(150), unique=True, nullable=False),
        sa.Column('username', sa.String(150), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(150), nullable=False),  # ← back to String
        sa.Column('phone_number', sa.String(100)),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False)
    )

    op.execute("""
        INSERT INTO customer (id, email, username, password_hash, phone_number, created_at, updated_at)
        SELECT id, email, username, password_hash, phone_number, created_at, updated_at
        FROM customer_new
    """)

    op.drop_table('customer_new')