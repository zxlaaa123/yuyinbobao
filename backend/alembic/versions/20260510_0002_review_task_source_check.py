"""add review task source check

Revision ID: 20260510_0002
Revises: 20260510_0001
Create Date: 2026-05-10
"""

from alembic import op

revision = "20260510_0002"
down_revision = "20260510_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("review_tasks") as batch_op:
            batch_op.create_check_constraint(
                "ck_review_tasks_source",
                "source in ('wrong_question', 'importance_high', 'new_knowledge')",
            )
        return

    op.create_check_constraint(
        "ck_review_tasks_source",
        "review_tasks",
        "source in ('wrong_question', 'importance_high', 'new_knowledge')",
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("review_tasks") as batch_op:
            batch_op.drop_constraint("ck_review_tasks_source", type_="check")
        return
    op.drop_constraint("ck_review_tasks_source", "review_tasks", type_="check")
