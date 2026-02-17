-- ============================================================
-- FASE 2: DATA WAREHOUSE - CAPA GOLD (NeonDB PostgreSQL)
-- Esquema dimensional optimizado para análisis
-- ============================================================

-- Eliminar tablas existentes (en orden inverso de dependencias)
DROP TABLE IF EXISTS fact_market_metrics CASCADE;
DROP TABLE IF EXISTS bridge_market_tag CASCADE;
DROP TABLE IF EXISTS dim_tag CASCADE;
DROP TABLE IF EXISTS dim_series CASCADE;
DROP TABLE IF EXISTS dim_event CASCADE;
DROP TABLE IF EXISTS dim_market CASCADE;
DROP TABLE IF EXISTS dim_time CASCADE;

-- ============================================================
-- DIMENSIÓN: TIEMPO
-- ============================================================
CREATE TABLE dim_time (
    time_key SERIAL PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,
    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,
    is_weekend BOOLEAN NOT NULL,
    is_month_start BOOLEAN NOT NULL,
    is_month_end BOOLEAN NOT NULL,
    is_quarter_start BOOLEAN NOT NULL,
    is_quarter_end BOOLEAN NOT NULL,
    is_year_start BOOLEAN NOT NULL,
    is_year_end BOOLEAN NOT NULL,
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_time_date ON dim_time(date_value);
CREATE INDEX idx_dim_time_year_month ON dim_time(year, month);
CREATE INDEX idx_dim_time_quarter ON dim_time(year, quarter);

-- ============================================================
-- DIMENSIÓN: SERIES
-- ============================================================
CREATE TABLE dim_series (
    series_key SERIAL PRIMARY KEY,
    series_id VARCHAR(100) NOT NULL UNIQUE,
    slug VARCHAR(255) NOT NULL,
    title TEXT,
    description TEXT,
    image VARCHAR(500),
    icon VARCHAR(500),
    series_type VARCHAR(50),
    recurrence VARCHAR(50),
    active BOOLEAN,
    closed BOOLEAN,
    archived BOOLEAN,
    restricted BOOLEAN,
    featured BOOLEAN,
    layout VARCHAR(50),
    start_date TIMESTAMP,
    published_at TIMESTAMP,
    created_at_source TIMESTAMP,
    updated_at_source TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    expiration_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_series_id ON dim_series(series_id);
CREATE INDEX idx_dim_series_slug ON dim_series(slug);
CREATE INDEX idx_dim_series_current ON dim_series(is_current);

-- ============================================================
-- DIMENSIÓN: EVENTO
-- ============================================================
CREATE TABLE dim_event (
    event_key SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL UNIQUE,
    ticker VARCHAR(255),
    slug VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    image VARCHAR(500),
    icon VARCHAR(500),
    resolution_source TEXT,
    
    -- Estado
    active BOOLEAN,
    closed BOOLEAN,
    archived BOOLEAN,
    new BOOLEAN,
    featured BOOLEAN,
    restricted BOOLEAN,
    cyom BOOLEAN,
    competitive NUMERIC(20, 10),
    
    -- Fechas
    start_date TIMESTAMP,
    creation_date TIMESTAMP,
    end_date TIMESTAMP,
    closed_time TIMESTAMP,
    published_at TIMESTAMP,
    created_at_source TIMESTAMP,
    updated_at_source TIMESTAMP,
    
    -- Configuración
    show_all_outcomes BOOLEAN,
    show_market_images BOOLEAN,
    enable_neg_risk BOOLEAN,
    enable_order_book BOOLEAN,
    neg_risk_augmented BOOLEAN,
    pending_deployment BOOLEAN,
    deploying BOOLEAN,
    requires_translation BOOLEAN,
    comments_enabled BOOLEAN,
    
    -- Referencias
    series_slug VARCHAR(255),
    parent_event_id INTEGER,
    
    -- Metadatos deportivos (si aplica)
    sport VARCHAR(50),
    event_date TIMESTAMP,
    event_week INTEGER,
    game_id VARCHAR(100),
    game_status VARCHAR(50),
    
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    expiration_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_event_id ON dim_event(event_id);
CREATE INDEX idx_dim_event_slug ON dim_event(slug);
CREATE INDEX idx_dim_event_category ON dim_event(category);
CREATE INDEX idx_dim_event_current ON dim_event(is_current);
CREATE INDEX idx_dim_event_series_slug ON dim_event(series_slug);

-- ============================================================
-- DIMENSIÓN: MERCADO
-- ============================================================
CREATE TABLE dim_market (
    market_key SERIAL PRIMARY KEY,
    market_id VARCHAR(100) NOT NULL UNIQUE,
    condition_id VARCHAR(200),
    slug VARCHAR(255) NOT NULL,
    question TEXT NOT NULL,
    description TEXT,
    
    -- Configuración
    market_type VARCHAR(50),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    outcomes JSONB, -- Array de outcomes: ["Yes", "No"]
    
    -- Estado
    active BOOLEAN,
    closed BOOLEAN,
    archived BOOLEAN,
    restricted BOOLEAN,
    new BOOLEAN,
    featured BOOLEAN,
    
    -- Configuración de trading
    enable_order_book BOOLEAN,
    clear_book_on_start BOOLEAN,
    fppm_live BOOLEAN,
    rfq_enabled BOOLEAN,
    
    -- Fechas
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    closed_time TIMESTAMP,
    created_at_source TIMESTAMP,
    updated_at_source TIMESTAMP,
    
    -- Recursos
    image VARCHAR(500),
    icon VARCHAR(500),
    resolution_source TEXT,
    
    -- Configuraciones avanzadas
    neg_risk BOOLEAN,
    neg_risk_market_id VARCHAR(100),
    format_type VARCHAR(50),
    wide_format BOOLEAN,
    
    -- Límites (para mercados numéricos)
    lower_bound NUMERIC(20, 10),
    upper_bound NUMERIC(20, 10),
    
    -- Identificadores externos
    question_id VARCHAR(100),
    market_maker_address VARCHAR(200),
    
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    expiration_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_market_id ON dim_market(market_id);
CREATE INDEX idx_dim_market_slug ON dim_market(slug);
CREATE INDEX idx_dim_market_category ON dim_market(category);
CREATE INDEX idx_dim_market_current ON dim_market(is_current);
CREATE INDEX idx_dim_market_type ON dim_market(market_type);

-- ============================================================
-- DIMENSIÓN: TAG (Con jerarquía)
-- ============================================================
CREATE TABLE dim_tag (
    tag_key SERIAL PRIMARY KEY,
    tag_id VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL,
    
    -- Jerarquía
    parent_tag_id VARCHAR(100),
    level INTEGER DEFAULT 1,
    path VARCHAR(1000), -- Formato: /parent/child/grandchild
    
    -- Configuración
    force_show BOOLEAN,
    force_hide BOOLEAN,
    is_carousel BOOLEAN,
    requires_translation BOOLEAN,
    
    -- Metadata
    published_at TIMESTAMP,
    created_at_source TIMESTAMP,
    updated_at_source TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- SCD Type 2 fields
    effective_date DATE DEFAULT CURRENT_DATE,
    expiration_date DATE DEFAULT '9999-12-31',
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_tag_id ON dim_tag(tag_id);
CREATE INDEX idx_dim_tag_slug ON dim_tag(slug);
CREATE INDEX idx_dim_tag_parent ON dim_tag(parent_tag_id);
CREATE INDEX idx_dim_tag_level ON dim_tag(level);
CREATE INDEX idx_dim_tag_current ON dim_tag(is_current);

-- ============================================================
-- TABLA PUENTE: MARKET-TAG (Many-to-Many)
-- ============================================================
CREATE TABLE bridge_market_tag (
    bridge_key SERIAL PRIMARY KEY,
    market_key INTEGER NOT NULL REFERENCES dim_market(market_key),
    tag_key INTEGER NOT NULL REFERENCES dim_tag(tag_key),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(market_key, tag_key)
);

CREATE INDEX idx_bridge_market ON bridge_market_tag(market_key);
CREATE INDEX idx_bridge_tag ON bridge_market_tag(tag_key);

-- ============================================================
-- TABLA DE HECHOS: MÉTRICAS DE MERCADO
-- ============================================================
CREATE TABLE fact_market_metrics (
    fact_key SERIAL PRIMARY KEY,
    
    -- Foreign Keys a dimensiones
    market_key INTEGER NOT NULL REFERENCES dim_market(market_key),
    event_key INTEGER REFERENCES dim_event(event_key),
    series_key INTEGER REFERENCES dim_series(series_key),
    snapshot_date_key INTEGER NOT NULL REFERENCES dim_time(time_key),
    start_date_key INTEGER REFERENCES dim_time(time_key),
    end_date_key INTEGER REFERENCES dim_time(time_key),
    closed_date_key INTEGER REFERENCES dim_time(time_key),
    
    -- Métricas financieras (desanidadas y normalizadas)
    liquidity NUMERIC(20, 10),
    liquidity_amm NUMERIC(20, 10),
    liquidity_clob NUMERIC(20, 10),
    
    -- Volumen
    volume NUMERIC(20, 10),
    volume_24hr NUMERIC(20, 10),
    volume_1wk NUMERIC(20, 10),
    volume_1mo NUMERIC(20, 10),
    volume_1yr NUMERIC(20, 10),
    
    -- Volumen por tipo
    volume_amm NUMERIC(20, 10),
    volume_clob NUMERIC(20, 10),
    volume_24hr_amm NUMERIC(20, 10),
    volume_24hr_clob NUMERIC(20, 10),
    volume_1wk_amm NUMERIC(20, 10),
    volume_1wk_clob NUMERIC(20, 10),
    volume_1mo_amm NUMERIC(20, 10),
    volume_1mo_clob NUMERIC(20, 10),
    volume_1yr_amm NUMERIC(20, 10),
    volume_1yr_clob NUMERIC(20, 10),
    
    -- Open Interest
    open_interest NUMERIC(20, 10),
    
    -- Precios (desanidados del array outcomePrices)
    outcome_price_yes NUMERIC(30, 20),
    outcome_price_no NUMERIC(30, 20),
    
    -- Precios de mercado
    last_trade_price NUMERIC(30, 20),
    best_bid NUMERIC(30, 20),
    best_ask NUMERIC(30, 20),
    spread NUMERIC(30, 20),
    
    -- Cambios de precio
    price_change_1h NUMERIC(30, 20),
    price_change_1d NUMERIC(30, 20),
    price_change_1wk NUMERIC(30, 20),
    price_change_1mo NUMERIC(30, 20),
    price_change_1yr NUMERIC(30, 20),
    
    -- Métricas de engagement
    comment_count INTEGER,
    tweet_count INTEGER,
    
    -- Fees y configuración
    fee NUMERIC(20, 10),
    taker_base_fee NUMERIC(20, 10),
    maker_base_fee NUMERIC(20, 10),
    
    -- Estado del mercado en el snapshot
    competitive NUMERIC(20, 10),
    
    -- Metadata
    extraction_timestamp TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(market_key, snapshot_date_key)
);

-- Índices para optimizar consultas analíticas
CREATE INDEX idx_fact_market_key ON fact_market_metrics(market_key);
CREATE INDEX idx_fact_event_key ON fact_market_metrics(event_key);
CREATE INDEX idx_fact_series_key ON fact_market_metrics(series_key);
CREATE INDEX idx_fact_snapshot_date ON fact_market_metrics(snapshot_date_key);
CREATE INDEX idx_fact_start_date ON fact_market_metrics(start_date_key);
CREATE INDEX idx_fact_end_date ON fact_market_metrics(end_date_key);
CREATE INDEX idx_fact_volume ON fact_market_metrics(volume);
CREATE INDEX idx_fact_liquidity ON fact_market_metrics(liquidity);

-- Índices compuestos para consultas comunes
CREATE INDEX idx_fact_market_snapshot ON fact_market_metrics(market_key, snapshot_date_key);
CREATE INDEX idx_fact_series_snapshot ON fact_market_metrics(series_key, snapshot_date_key);

-- ============================================================
-- COMENTARIOS PARA DOCUMENTACIÓN
-- ============================================================

COMMENT ON TABLE dim_time IS 'Dimensión de tiempo con granularidad diaria y atributos de calendario';
COMMENT ON TABLE dim_series IS 'Dimensión de series de mercados (ej: NBA, Elections)';
COMMENT ON TABLE dim_event IS 'Dimensión de eventos que contienen mercados';
COMMENT ON TABLE dim_market IS 'Dimensión de mercados de predicción';
COMMENT ON TABLE dim_tag IS 'Dimensión de tags con jerarquía para categorización';
COMMENT ON TABLE bridge_market_tag IS 'Tabla puente para relación many-to-many entre markets y tags';
COMMENT ON TABLE fact_market_metrics IS 'Tabla de hechos con métricas de mercado (volumen, liquidez, precios)';

COMMENT ON COLUMN dim_tag.path IS 'Ruta jerárquica completa del tag (ej: /sports/nba/playoffs)';
COMMENT ON COLUMN fact_market_metrics.outcome_price_yes IS 'Precio desanidado del outcome "Yes" del array outcomePrices';
COMMENT ON COLUMN fact_market_metrics.outcome_price_no IS 'Precio desanidado del outcome "No" del array outcomePrices';
