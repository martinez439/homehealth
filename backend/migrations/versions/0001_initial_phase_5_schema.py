"""initial phase 5 schema

Revision ID: 0001_initial_phase_5
Revises: 
Create Date: 2026-05-28
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_initial_phase_5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('clients', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('first_name', sa.String(100), nullable=False), sa.Column('last_name', sa.String(100), nullable=False), sa.Column('date_of_birth', sa.Date(), nullable=True), sa.Column('phone', sa.String(40), nullable=False), sa.Column('email', sa.String(255), nullable=True), sa.Column('address', sa.String(255), nullable=False), sa.Column('city', sa.String(120), nullable=False), sa.Column('state', sa.String(50), nullable=False), sa.Column('zip_code', sa.String(20), nullable=False), sa.Column('care_level', sa.String(100), nullable=False), sa.Column('status', sa.String(40), nullable=False), sa.Column('notes', sa.Text(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('caregivers', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('first_name', sa.String(100), nullable=False), sa.Column('last_name', sa.String(100), nullable=False), sa.Column('phone', sa.String(40), nullable=False), sa.Column('email', sa.String(255), nullable=False), sa.Column('certification', sa.String(100), nullable=False), sa.Column('availability_notes', sa.Text(), nullable=False), sa.Column('status', sa.String(40), nullable=False), sa.Column('notes', sa.Text(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('intake_requests', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('client_name', sa.String(255), nullable=False), sa.Column('phone', sa.String(40), nullable=False), sa.Column('email', sa.String(255), nullable=True), sa.Column('city', sa.String(120), nullable=False), sa.Column('care_needs', sa.Text(), nullable=False), sa.Column('preferred_schedule', sa.String(120), nullable=False), sa.Column('urgency', sa.String(40), nullable=False), sa.Column('status', sa.String(40), nullable=False), sa.Column('notes', sa.Text(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('users', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('email', sa.String(255), nullable=False), sa.Column('password_hash', sa.String(255), nullable=False), sa.Column('first_name', sa.String(100), nullable=False), sa.Column('last_name', sa.String(100), nullable=False), sa.Column('role', sa.String(40), nullable=False), sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=True), sa.Column('caregiver_id', sa.Integer(), sa.ForeignKey('caregivers.id'), nullable=True), sa.Column('is_active', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'])
    op.create_table('visits', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False), sa.Column('caregiver_id', sa.Integer(), sa.ForeignKey('caregivers.id'), nullable=False), sa.Column('scheduled_start', sa.DateTime(), nullable=False), sa.Column('scheduled_end', sa.DateTime(), nullable=False), sa.Column('status', sa.String(40), nullable=False), sa.Column('service_type', sa.String(120), nullable=False), sa.Column('notes', sa.Text(), nullable=False), sa.Column('checked_in_at', sa.DateTime(), nullable=True), sa.Column('checked_out_at', sa.DateTime(), nullable=True), sa.Column('check_in_location', sa.String(255), nullable=True), sa.Column('check_out_location', sa.String(255), nullable=True), sa.Column('mileage_start', sa.Float(), nullable=True), sa.Column('mileage_end', sa.Float(), nullable=True), sa.Column('mileage_total', sa.Float(), nullable=True), sa.Column('task_checklist', sa.Text(), nullable=False), sa.Column('caregiver_notes', sa.Text(), nullable=False), sa.Column('missed_alert_sent', sa.Boolean(), nullable=False), sa.Column('recurrence_group_id', sa.String(80), nullable=True), sa.Column('recurrence_rule', sa.String(40), nullable=True), sa.Column('recurrence_end_date', sa.Date(), nullable=True), sa.Column('generated_from_recurring', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('caregiver_availability', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('caregiver_id', sa.Integer(), sa.ForeignKey('caregivers.id'), nullable=False), sa.Column('day_of_week', sa.Integer(), nullable=False), sa.Column('available', sa.Boolean(), nullable=False), sa.Column('start_time', sa.Time(), nullable=True), sa.Column('end_time', sa.Time(), nullable=True), sa.Column('notes', sa.Text(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('family_contacts', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False), sa.Column('first_name', sa.String(100), nullable=False), sa.Column('last_name', sa.String(100), nullable=False), sa.Column('relationship', sa.String(100), nullable=False), sa.Column('phone', sa.String(40), nullable=False), sa.Column('email', sa.String(255), nullable=False), sa.Column('is_primary', sa.Boolean(), nullable=False), sa.Column('receives_updates', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('family_messages', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('client_id', sa.Integer(), sa.ForeignKey('clients.id'), nullable=False), sa.Column('sender_name', sa.String(200), nullable=False), sa.Column('sender_email', sa.String(255), nullable=True), sa.Column('message_type', sa.String(60), nullable=False), sa.Column('subject', sa.String(255), nullable=False), sa.Column('message', sa.Text(), nullable=False), sa.Column('status', sa.String(40), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))
    op.create_table('audit_logs', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True), sa.Column('actor_email', sa.String(255), nullable=True), sa.Column('actor_role', sa.String(40), nullable=True), sa.Column('action', sa.String(120), nullable=False), sa.Column('entity_type', sa.String(120), nullable=False), sa.Column('entity_id', sa.Integer(), nullable=True), sa.Column('description', sa.Text(), nullable=False), sa.Column('ip_address', sa.String(120), nullable=True), sa.Column('user_agent', sa.String(255), nullable=True), sa.Column('created_at', sa.DateTime(), nullable=False))
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_entity_type', 'audit_logs', ['entity_type'])
    op.create_index('ix_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_table('file_attachments', sa.Column('id', sa.Integer(), primary_key=True), sa.Column('owner_type', sa.String(80), nullable=False), sa.Column('owner_id', sa.Integer(), nullable=True), sa.Column('uploaded_by_user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True), sa.Column('original_filename', sa.String(255), nullable=False), sa.Column('stored_filename', sa.String(255), nullable=False, unique=True), sa.Column('content_type', sa.String(120), nullable=False), sa.Column('file_size', sa.Integer(), nullable=False), sa.Column('storage_path', sa.String(500), nullable=False), sa.Column('is_deleted', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(), nullable=False), sa.Column('updated_at', sa.DateTime(), nullable=False))


def downgrade() -> None:
    op.drop_table('file_attachments')
    op.drop_index('ix_audit_logs_created_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_entity_type', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_table('family_messages')
    op.drop_table('family_contacts')
    op.drop_table('caregiver_availability')
    op.drop_table('visits')
    op.drop_index('ix_users_role', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    op.drop_table('intake_requests')
    op.drop_table('caregivers')
    op.drop_table('clients')
