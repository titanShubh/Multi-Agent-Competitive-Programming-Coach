-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    display_name VARCHAR(100),
    current_rating INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create Problems table
CREATE TABLE IF NOT EXISTS problems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    statement TEXT NOT NULL,
    constraints TEXT,
    input_format TEXT,
    output_format TEXT,
    sample_io JSONB,
    source VARCHAR(100),
    source_id VARCHAR(100),
    source_url TEXT,
    difficulty VARCHAR(50),
    estimated_rating INTEGER,
    categories VARCHAR(255)[] NOT NULL DEFAULT '{}',
    tags VARCHAR(255)[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create Coaching Sessions table
CREATE TABLE IF NOT EXISTS coaching_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE SET NULL,
    problem_statement TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    session_mode VARCHAR(50) NOT NULL DEFAULT 'learning',
    hint_level INTEGER NOT NULL DEFAULT 0,
    max_hint_used INTEGER NOT NULL DEFAULT 0,
    problem_analysis JSONB,
    timer_start TIMESTAMP WITHOUT TIME ZONE,
    timer_duration_minutes INTEGER,
    started_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Create Messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES coaching_sessions(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    agent_name VARCHAR(100),
    message_metadata JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create Learning Profiles table
CREATE TABLE IF NOT EXISTS learning_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    topic_proficiency JSONB NOT NULL DEFAULT '{}',
    weak_topics VARCHAR(255)[] NOT NULL DEFAULT '{}',
    strong_topics VARCHAR(255)[] NOT NULL DEFAULT '{}',
    common_mistakes JSONB NOT NULL DEFAULT '[]',
    total_problems_attempted INTEGER NOT NULL DEFAULT 0,
    total_problems_solved INTEGER NOT NULL DEFAULT 0,
    total_hints_used INTEGER NOT NULL DEFAULT 0,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create Problem Attempts table
CREATE TABLE IF NOT EXISTS problem_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    problem_id UUID REFERENCES problems(id) ON DELETE SET NULL,
    session_id UUID NOT NULL REFERENCES coaching_sessions(id) ON DELETE CASCADE,
    solved BOOLEAN NOT NULL DEFAULT FALSE,
    hints_used INTEGER NOT NULL DEFAULT 0,
    max_hint_level INTEGER NOT NULL DEFAULT 0,
    code_submitted TEXT,
    language VARCHAR(50),
    mistakes_made JSONB,
    attempted_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    solved_at TIMESTAMP WITHOUT TIME ZONE
);

-- Create Hint Progressions table
CREATE TABLE IF NOT EXISTS hint_progressions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES coaching_sessions(id) ON DELETE CASCADE,
    hint_level INTEGER NOT NULL,
    hint_type VARCHAR(100) NOT NULL,
    hint_content TEXT NOT NULL,
    revealed_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    was_helpful BOOLEAN
);

-- Create Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_user_id ON coaching_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_coaching_sessions_problem_id ON coaching_sessions(problem_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_learning_profiles_user_id ON learning_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_problem_attempts_user_id ON problem_attempts(user_id);
CREATE INDEX IF NOT EXISTS idx_problem_attempts_problem_id ON problem_attempts(problem_id);
CREATE INDEX IF NOT EXISTS idx_problem_attempts_session_id ON problem_attempts(session_id);
CREATE INDEX IF NOT EXISTS idx_hint_progressions_session_id ON hint_progressions(session_id);
