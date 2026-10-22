-- schema.sql
-- Run once in your Postgres SQL editor (Supabase / Neon) before migrating.

CREATE TABLE IF NOT EXISTS bookings (
    id            BIGSERIAL PRIMARY KEY,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    pet_name      TEXT        NOT NULL,
    service_type  TEXT        NOT NULL,
    booking_date  DATE,                     -- NULL only for migrated rows with unreadable dates
    booking_time  TEXT        NOT NULL,
    phone_number  TEXT        NOT NULL,
    status        TEXT        NOT NULL DEFAULT 'confirmed'
                  CHECK (status IN ('confirmed', 'cancelled', 'rebooked')),
    updated_at    TIMESTAMPTZ
);

-- Speeds up cancel/reschedule lookups
CREATE INDEX IF NOT EXISTS idx_bookings_lookup
    ON bookings (phone_number, lower(pet_name), booking_date);

CREATE TABLE IF NOT EXISTS faq (
    id           BIGSERIAL PRIMARY KEY,
    intent_name  TEXT NOT NULL,
    question     TEXT NOT NULL,
    answer       TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_faq_intent ON faq (intent_name);

CREATE TABLE IF NOT EXISTS receptionist_requests (
    id             BIGSERIAL PRIMARY KEY,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    customer_name  TEXT NOT NULL,
    phone_number   TEXT NOT NULL,
    query_text     TEXT NOT NULL
);
