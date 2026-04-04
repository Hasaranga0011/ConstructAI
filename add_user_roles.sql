-- ConstructAI Database Migration: Add User Roles
-- Run this in pgAdmin to add role support

-- Step 1: Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'site_engineer';

-- Step 2: Verify the column was added
SELECT column_name, data_type, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'role';

-- Step 3: Check sample users with roles
SELECT id, email, username, role FROM users LIMIT 10;
