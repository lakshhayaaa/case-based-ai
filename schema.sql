-- USERS
CREATE TABLE users (
    user_id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ENTREPRENEURIAL CASES
CREATE TABLE entrepreneurial_cases (
    case_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255),
    source VARCHAR(255),
    industry VARCHAR(100),
    year INT,
    case_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- CASE CHUNKS
CREATE TABLE case_chunks (
    chunk_id BIGSERIAL PRIMARY KEY,
    case_id BIGINT REFERENCES entrepreneurial_cases(case_id),
    chunk_text TEXT,
    chunk_order INT,
    embedding_vector TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USER QUERIES
CREATE TABLE user_queries (
    query_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id),
    query_text TEXT,
    query_embedding TEXT,
    asked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI RESPONSES
CREATE TABLE ai_responses (
    response_id BIGSERIAL PRIMARY KEY,
    query_id BIGINT REFERENCES user_queries(query_id),
    final_response_text TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- RESPONSE CASE MAPPING
CREATE TABLE response_case_mapping (
    response_id BIGINT REFERENCES ai_responses(response_id),
    case_id BIGINT REFERENCES entrepreneurial_cases(case_id),
    PRIMARY KEY (response_id, case_id)
);

-- RESPONSE CHUNK MAPPING
CREATE TABLE response_chunk_mapping (
    response_id BIGINT REFERENCES ai_responses(response_id),
    chunk_id BIGINT REFERENCES case_chunks(chunk_id),
    used_for VARCHAR(100),
    PRIMARY KEY (response_id, chunk_id)
);

-- VERIFICATION LOG
CREATE TABLE verification_log (
    verification_id BIGSERIAL PRIMARY KEY,
    response_id BIGINT REFERENCES ai_responses(response_id),
    claim_text TEXT,
    chunk_id BIGINT REFERENCES case_chunks(chunk_id),
    similarity_score DECIMAL(5,4),
    status VARCHAR(30),
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TRUST SCORE
CREATE TABLE trust_score (
    response_id BIGINT PRIMARY KEY REFERENCES ai_responses(response_id),
    trust_score DECIMAL(5,2),
    supported_claim INT,
    total_claims INT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);