-- ============================================================================
-- Migration 004: Add payload_hash idempotency key to event_queue
-- ----------------------------------------------------------------------------
-- event_queue had no dedup key, so a retried webhook/API submission (client
-- timeout, network retry — same payload resent) inserted a second row and
-- silently double-counted DORA metrics downstream. Adds a SHA-256 hash of
-- the canonical payload as a partial unique index (NULL-safe for any rows
-- written before this migration) so enqueue_event can detect and no-op on
-- an exact-duplicate resubmission instead of enqueueing it again.
-- (production-audit finding, 2026-08-21)
-- ============================================================================

ALTER TABLE event_queue
    ADD COLUMN IF NOT EXISTS payload_hash VARCHAR(64);

CREATE UNIQUE INDEX IF NOT EXISTS idx_event_queue_payload_hash
    ON event_queue (payload_hash)
    WHERE payload_hash IS NOT NULL;

-- Record this migration
INSERT INTO _schema_migrations (version, description, checksum)
VALUES (
    4,
    'Add payload_hash idempotency key to event_queue',
    'sha256-004-add-payload-hash-idempotency'
)
ON CONFLICT (version) DO NOTHING;
