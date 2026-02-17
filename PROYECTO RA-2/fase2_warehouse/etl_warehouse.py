"""
ETL: Delta Lake (Capa Bronze) → NeonDB Data Warehouse (Capa Gold)
Carga completa de datos con limpieza, normalización y desanidado
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import json
from datetime import datetime, date
import sys
import os

# Agregar path para imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from delta_utils import DeltaLakeManager
from fase2_warehouse.neondb_config import get_connection_string, DEFAULT_ENVIRONMENT
import logging

class DataWarehouseETL:
    """
    ETL para cargar datos desde Delta Lake hacia el Data Warehouse en NeonDB
    """
    
    def __init__(self, environment=DEFAULT_ENVIRONMENT):
        self.environment = environment
        self.delta_manager = DeltaLakeManager()
        self.conn = None
        self.logger = self._setup_logger()
        
    def _setup_logger(self):
        """Configurar logger"""
        logger = logging.getLogger("DataWarehouseETL")
        logger.setLevel(logging.INFO)
        
        # Handler para consola
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Handler para archivo
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            f"{log_dir}/etl_warehouse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        file_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        
        return logger
    
    def connect(self):
        """Conectar a NeonDB"""
        try:
            self.logger.info(f"Conectando a NeonDB ({self.environment})...")
            self.conn = psycopg2.connect(get_connection_string(self.environment))
            self.conn.autocommit = False  # Usar transacciones
            self.logger.info("✅ Conexión establecida")
            return True
        except Exception as e:
            self.logger.error(f"❌ Error al conectar: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar de NeonDB"""
        if self.conn:
            self.conn.close()
            self.logger.info("🔌 Conexión cerrada")
    
    def clean_value(self, value):
        """
        Limpia y normaliza un valor
        - Convierte nan a None
        - Limpia strings vacíos
        """
        if pd.isna(value):
            return None
        if isinstance(value, str) and value.strip() == '':
            return None
        return value
    
    def parse_json_field(self, value):
        """
        Parsea un campo JSON string a objeto Python
        """
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return None
        return value
    
    def extract_outcome_prices(self, outcome_prices_str):
        """
        Desanida los precios del array outcomePrices
        Retorna: (price_yes, price_no)
        """
        prices = self.parse_json_field(outcome_prices_str)
        if not prices or not isinstance(prices, list):
            return None, None
        
        price_yes = float(prices[0]) if len(prices) > 0 else None
        price_no = float(prices[1]) if len(prices) > 1 else None
        
        return price_yes, price_no
    
    def load_dim_time(self, start_date='2021-01-01', end_date='2026-12-31'):
        """
        Carga la dimensión de tiempo con todas las fechas en el rango
        """
        self.logger.info("📅 Cargando dimensión de tiempo...")
        
        cursor = self.conn.cursor()
        
        # Generar rango de fechas
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        records = []
        for dt in dates:
            record = (
                dt.date(),
                dt.year,
                (dt.month - 1) // 3 + 1,  # Quarter
                dt.month,
                dt.strftime('%B'),
                dt.isocalendar()[1],  # Week of year
                dt.day,
                dt.dayofweek,
                dt.strftime('%A'),
                dt.dayofweek >= 5,  # is_weekend
                dt.day == 1,  # is_month_start
                dt.day == pd.Period(dt, 'M').days_in_month,  # is_month_end
                dt.day == 1 and dt.month in [1, 4, 7, 10],  # is_quarter_start
                dt.day == pd.Period(dt, 'M').days_in_month and dt.month in [3, 6, 9, 12],  # is_quarter_end
                dt.day == 1 and dt.month == 1,  # is_year_start
                dt.day == 31 and dt.month == 12,  # is_year_end
                dt.year,  # fiscal_year (same as calendar year)
                (dt.month - 1) // 3 + 1  # fiscal_quarter
            )
            records.append(record)
        
        # Insertar en batch
        query = """
            INSERT INTO dim_time (
                date_value, year, quarter, month, month_name, week_of_year,
                day_of_month, day_of_week, day_name, is_weekend,
                is_month_start, is_month_end, is_quarter_start, is_quarter_end,
                is_year_start, is_year_end, fiscal_year, fiscal_quarter
            ) VALUES %s
            ON CONFLICT (date_value) DO NOTHING
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Dimensión tiempo cargada: {count} registros")
        cursor.close()
    
    def get_time_key(self, date_value):
        """
        Obtiene el time_key para una fecha
        """
        if pd.isna(date_value) or date_value is None:
            return None
        
        # Convertir a date si es datetime
        if isinstance(date_value, str):
            try:
                date_value = pd.to_datetime(date_value).date()
            except:
                return None
        elif isinstance(date_value, pd.Timestamp) or isinstance(date_value, datetime):
            date_value = date_value.date()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT time_key FROM dim_time WHERE date_value = %s", (date_value,))
        result = cursor.fetchone()
        cursor.close()
        
        return result[0] if result else None
    
    def load_dim_series(self, df_series):
        """
        Carga la dimensión de series
        """
        self.logger.info("📁 Cargando dimensión de series...")
        
        cursor = self.conn.cursor()
        records = []
        
        for _, row in df_series.iterrows():
            record = (
                self.clean_value(row.get('id')),
                self.clean_value(row.get('slug')),
                self.clean_value(row.get('title')),
                self.clean_value(row.get('description')),
                self.clean_value(row.get('image')),
                self.clean_value(row.get('icon')),
                self.clean_value(row.get('seriesType')),
                self.clean_value(row.get('recurrence')),
                self.clean_value(row.get('active')),
                self.clean_value(row.get('closed')),
                self.clean_value(row.get('archived')),
                self.clean_value(row.get('restricted')),
                self.clean_value(row.get('featured')),
                self.clean_value(row.get('layout')),
                self.clean_value(row.get('startDate')),
                self.clean_value(row.get('publishedAt')),
                self.clean_value(row.get('createdAt')),
                self.clean_value(row.get('updatedAt')),
                self.clean_value(row.get('createdBy')),
                self.clean_value(row.get('updatedBy'))
            )
            records.append(record)
        
        query = """
            INSERT INTO dim_series (
                series_id, slug, title, description, image, icon,
                series_type, recurrence, active, closed, archived, restricted,
                featured, layout, start_date, published_at, created_at_source,
                updated_at_source, created_by, updated_by
            ) VALUES %s
            ON CONFLICT (series_id) DO UPDATE SET
                slug = EXCLUDED.slug,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                image = EXCLUDED.image,
                icon = EXCLUDED.icon,
                series_type = EXCLUDED.series_type,
                recurrence = EXCLUDED.recurrence,
                active = EXCLUDED.active,
                closed = EXCLUDED.closed,
                archived = EXCLUDED.archived,
                restricted = EXCLUDED.restricted,
                featured = EXCLUDED.featured,
                layout = EXCLUDED.layout,
                start_date = EXCLUDED.start_date,
                published_at = EXCLUDED.published_at,
                updated_at_source = EXCLUDED.updated_at_source,
                updated_by = EXCLUDED.updated_by
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Dimensión series cargada: {count} registros")
        cursor.close()
    
    def load_dim_tag(self, df_tags):
        """
        Carga la dimensión de tags con jerarquía
        """
        self.logger.info("🏷️  Cargando dimensión de tags...")
        
        cursor = self.conn.cursor()
        records = []
        
        for _, row in df_tags.iterrows():
            tag_id = self.clean_value(row.get('id'))
            slug = self.clean_value(row.get('slug'))
            
            # Por ahora, todos los tags son nivel 1 (sin jerarquía)
            # Se puede expandir después si hay datos de parent_tag
            path = f"/{slug}" if slug else None
            
            record = (
                tag_id,
                self.clean_value(row.get('label')),
                slug,
                None,  # parent_tag_id
                1,     # level
                path,  # path
                self.clean_value(row.get('forceShow')),
                self.clean_value(row.get('forceHide')),
                self.clean_value(row.get('isCarousel')),
                self.clean_value(row.get('requiresTranslation')),
                self.clean_value(row.get('publishedAt')),
                self.clean_value(row.get('createdAt')),
                self.clean_value(row.get('updatedAt')),
                self.clean_value(row.get('createdBy')),
                self.clean_value(row.get('updatedBy'))
            )
            records.append(record)
        
        query = """
            INSERT INTO dim_tag (
                tag_id, label, slug, parent_tag_id, level, path,
                force_show, force_hide, is_carousel, requires_translation,
                published_at, created_at_source, updated_at_source,
                created_by, updated_by
            ) VALUES %s
            ON CONFLICT (tag_id) DO UPDATE SET
                label = EXCLUDED.label,
                slug = EXCLUDED.slug,
                force_show = EXCLUDED.force_show,
                force_hide = EXCLUDED.force_hide,
                is_carousel = EXCLUDED.is_carousel,
                requires_translation = EXCLUDED.requires_translation,
                updated_at_source = EXCLUDED.updated_at_source,
                updated_by = EXCLUDED.updated_by
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Dimensión tags cargada: {count} registros")
        cursor.close()
    
    def load_dim_event(self, df_events):
        """
        Carga la dimensión de eventos
        """
        self.logger.info("📰 Cargando dimensión de eventos...")
        
        cursor = self.conn.cursor()
        records = []
        
        for _, row in df_events.iterrows():
            record = (
                self.clean_value(row.get('id')),
                self.clean_value(row.get('ticker')),
                self.clean_value(row.get('slug')),
                self.clean_value(row.get('title')),
                self.clean_value(row.get('description')),
                self.clean_value(row.get('category')),
                self.clean_value(row.get('subcategory')),
                self.clean_value(row.get('image')),
                self.clean_value(row.get('icon')),
                self.clean_value(row.get('resolutionSource')),
                self.clean_value(row.get('active')),
                self.clean_value(row.get('closed')),
                self.clean_value(row.get('archived')),
                self.clean_value(row.get('new')),
                self.clean_value(row.get('featured')),
                self.clean_value(row.get('restricted')),
                self.clean_value(row.get('cyom')),
                self.clean_value(row.get('competitive')),
                self.clean_value(row.get('startDate')),
                self.clean_value(row.get('creationDate')),
                self.clean_value(row.get('endDate')),
                self.clean_value(row.get('closedTime')),
                self.clean_value(row.get('published_at')),
                self.clean_value(row.get('createdAt')),
                self.clean_value(row.get('updatedAt')),
                self.clean_value(row.get('showAllOutcomes')),
                self.clean_value(row.get('showMarketImages')),
                self.clean_value(row.get('enableNegRisk')),
                self.clean_value(row.get('enableOrderBook')),
                self.clean_value(row.get('negRiskAugmented')),
                self.clean_value(row.get('pendingDeployment')),
                self.clean_value(row.get('deploying')),
                self.clean_value(row.get('requiresTranslation')),
                self.clean_value(row.get('commentsEnabled')),
                self.clean_value(row.get('seriesSlug')),
                self.clean_value(row.get('parentEventId')),
                self.clean_value(row.get('sport')),
                self.clean_value(row.get('eventDate')),
                self.clean_value(row.get('eventWeek')),
                self.clean_value(row.get('gameId')),
                self.clean_value(row.get('gameStatus'))
            )
            records.append(record)
        
        query = """
            INSERT INTO dim_event (
                event_id, ticker, slug, title, description, category, subcategory,
                image, icon, resolution_source, active, closed, archived, new,
                featured, restricted, cyom, competitive,
                start_date, creation_date, end_date, closed_time, published_at,
                created_at_source, updated_at_source,
                show_all_outcomes, show_market_images, enable_neg_risk,
                enable_order_book, neg_risk_augmented, pending_deployment,
                deploying, requires_translation, comments_enabled,
                series_slug, parent_event_id, sport, event_date, event_week,
                game_id, game_status
            ) VALUES %s
            ON CONFLICT (event_id) DO UPDATE SET
                ticker = EXCLUDED.ticker,
                slug = EXCLUDED.slug,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                subcategory = EXCLUDED.subcategory,
                image = EXCLUDED.image,
                icon = EXCLUDED.icon,
                resolution_source = EXCLUDED.resolution_source,
                active = EXCLUDED.active,
                closed = EXCLUDED.closed,
                archived = EXCLUDED.archived,
                updated_at_source = EXCLUDED.updated_at_source,
                show_all_outcomes = EXCLUDED.show_all_outcomes,
                show_market_images = EXCLUDED.show_market_images
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Dimensión eventos cargada: {count} registros")
        cursor.close()
    
    def load_dim_market(self, df_markets):
        """
        Carga la dimensión de mercados
        """
        self.logger.info("💹 Cargando dimensión de mercados...")
        
        cursor = self.conn.cursor()
        records = []
        
        for _, row in df_markets.iterrows():
            # Parsear outcomes como JSONB
            outcomes = self.parse_json_field(row.get('outcomes'))
            outcomes_json = json.dumps(outcomes) if outcomes else None
            
            record = (
                str(self.clean_value(row.get('id'))),
                self.clean_value(row.get('conditionId')),
                self.clean_value(row.get('slug')),
                self.clean_value(row.get('question')),
                self.clean_value(row.get('description')),
                self.clean_value(row.get('marketType')),
                self.clean_value(row.get('category')),
                self.clean_value(row.get('subcategory')),
                outcomes_json,
                self.clean_value(row.get('active')),
                self.clean_value(row.get('closed')),
                self.clean_value(row.get('archived')),
                self.clean_value(row.get('restricted')),
                self.clean_value(row.get('new')),
                self.clean_value(row.get('featured')),
                self.clean_value(row.get('enableOrderBook')),
                self.clean_value(row.get('clearBookOnStart')),
                self.clean_value(row.get('fppmLive')),
                self.clean_value(row.get('rfqEnabled')),
                self.clean_value(row.get('startDate')),
                self.clean_value(row.get('endDate')),
                self.clean_value(row.get('closedTime')),
                self.clean_value(row.get('createdAt')),
                self.clean_value(row.get('updatedAt')),
                self.clean_value(row.get('image')),
                self.clean_value(row.get('icon')),
                self.clean_value(row.get('resolutionSource')),
                self.clean_value(row.get('negRisk')),
                self.clean_value(row.get('negRiskMarketID')),
                self.clean_value(row.get('formatType')),
                self.clean_value(row.get('wideFormat')),
                self.clean_value(row.get('lowerBound')),
                self.clean_value(row.get('upperBound')),
                self.clean_value(row.get('questionID')),
                self.clean_value(row.get('marketMakerAddress'))
            )
            records.append(record)
        
        query = """
            INSERT INTO dim_market (
                market_id, condition_id, slug, question, description,
                market_type, category, subcategory, outcomes,
                active, closed, archived, restricted, new, featured,
                enable_order_book, clear_book_on_start, fppm_live, rfq_enabled,
                start_date, end_date, closed_time, created_at_source, updated_at_source,
                image, icon, resolution_source,
                neg_risk, neg_risk_market_id, format_type, wide_format,
                lower_bound, upper_bound, question_id, market_maker_address
            ) VALUES %s
            ON CONFLICT (market_id) DO UPDATE SET
                slug = EXCLUDED.slug,
                question = EXCLUDED.question,
                description = EXCLUDED.description,
                active = EXCLUDED.active,
                closed = EXCLUDED.closed,
                archived = EXCLUDED.archived,
                updated_at_source = EXCLUDED.updated_at_source
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Dimensión mercados cargada: {count} registros")
        cursor.close()
    
    def load_bridge_market_tag(self, df_markets):
        """
        Carga la tabla puente market-tag (relación many-to-many)
        """
        self.logger.info("🔗 Cargando tabla puente market-tag...")
        
        cursor = self.conn.cursor()
        
        # Primero, obtener mapeo de IDs a keys
        cursor.execute("SELECT market_id, market_key FROM dim_market")
        market_map = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT tag_id, tag_key FROM dim_tag")
        tag_map = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        # Limpiar tabla puente existente
        cursor.execute("TRUNCATE bridge_market_tag")
        
        records = []
        for _, row in df_markets.iterrows():
            market_id = str(self.clean_value(row.get('id')))
            market_key = market_map.get(market_id)
            
            if not market_key:
                continue
            
            # Parsear tags (puede estar en la columna events si hay relación)
            # Por ahora, asumimos que los markets no tienen tags directos
            # Esta lógica se puede expandir según la estructura real
        
        if records:
            query = """
                INSERT INTO bridge_market_tag (market_key, tag_key)
                VALUES %s
                ON CONFLICT (market_key, tag_key) DO NOTHING
            """
            execute_values(cursor, query, records)
        
        self.conn.commit()
        
        count = cursor.rowcount if records else 0
        self.logger.info(f"✅ Tabla puente market-tag cargada: {count} registros")
        cursor.close()
    
    def load_fact_market_metrics(self, df_markets):
        """
        Carga la tabla de hechos con métricas de mercado
        """
        self.logger.info("📊 Cargando tabla de hechos (market metrics)...")
        
        cursor = self.conn.cursor()
        
        # Obtener mapeos de dimensiones
        cursor.execute("SELECT market_id, market_key FROM dim_market")
        market_map = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT event_id, event_key FROM dim_event")
        event_map = {int(row[0]): row[1] for row in cursor.fetchall()}
        
        cursor.execute("SELECT series_id, series_key FROM dim_series")
        series_map = {str(row[0]): row[1] for row in cursor.fetchall()}
        
        records = []
        for _, row in df_markets.iterrows():
            market_id = str(self.clean_value(row.get('id')))
            market_key = market_map.get(market_id)
            
            if not market_key:
                continue
            
            # Obtener event_key y series_key (si están relacionados)
            event_key = None  # Se puede obtener de la relación events
            series_key = None  # Se puede obtener de la relación series
            
            # Fechas
            snapshot_date = self.clean_value(row.get('_extraction_date'))
            if snapshot_date and isinstance(snapshot_date, str):
                snapshot_date = pd.to_datetime(snapshot_date).date()
            snapshot_date_key = self.get_time_key(snapshot_date) if snapshot_date else None
            
            start_date_key = self.get_time_key(self.clean_value(row.get('startDate')))
            end_date_key = self.get_time_key(self.clean_value(row.get('endDate')))
            closed_date_key = self.get_time_key(self.clean_value(row.get('closedTime')))
            
            if not snapshot_date_key:
                continue  # Skip si no tenemos snapshot_date
            
            # Desanidar precios
            price_yes, price_no = self.extract_outcome_prices(row.get('outcomePrices'))
            
            record = (
                market_key,
                event_key,
                series_key,
                snapshot_date_key,
                start_date_key,
                end_date_key,
                closed_date_key,
                self.clean_value(row.get('liquidity')),
                self.clean_value(row.get('liquidityAmm')),
                self.clean_value(row.get('liquidityClob')),
                self.clean_value(row.get('volume')),
                self.clean_value(row.get('volume24hr')),
                self.clean_value(row.get('volume1wk')),
                self.clean_value(row.get('volume1mo')),
                self.clean_value(row.get('volume1yr')),
                self.clean_value(row.get('volumeAmm')),
                self.clean_value(row.get('volumeClob')),
                self.clean_value(row.get('volume24hrAmm')),
                self.clean_value(row.get('volume24hrClob')),
                self.clean_value(row.get('volume1wkAmm')),
                self.clean_value(row.get('volume1wkClob')),
                self.clean_value(row.get('volume1moAmm')),
                self.clean_value(row.get('volume1moClob')),
                self.clean_value(row.get('volume1yrAmm')),
                self.clean_value(row.get('volume1yrClob')),
                self.clean_value(row.get('openInterest')),  # Nota: no está en markets, podría estar en events
                price_yes,
                price_no,
                self.clean_value(row.get('lastTradePrice')),
                self.clean_value(row.get('bestBid')),
                self.clean_value(row.get('bestAsk')),
                self.clean_value(row.get('spread')),
                self.clean_value(row.get('oneHourPriceChange')),
                self.clean_value(row.get('oneDayPriceChange')),
                self.clean_value(row.get('oneWeekPriceChange')),
                self.clean_value(row.get('oneMonthPriceChange')),
                self.clean_value(row.get('oneYearPriceChange')),
                None,  # comment_count - buscar en events
                None,  # tweet_count - buscar en events
                self.clean_value(row.get('fee')),
                self.clean_value(row.get('takerBaseFee')),
                self.clean_value(row.get('makerBaseFee')),
                self.clean_value(row.get('competitive')),
                self.clean_value(row.get('_extraction_timestamp'))
            )
            records.append(record)
        
        query = """
            INSERT INTO fact_market_metrics (
                market_key, event_key, series_key, snapshot_date_key,
                start_date_key, end_date_key, closed_date_key,
                liquidity, liquidity_amm, liquidity_clob,
                volume, volume_24hr, volume_1wk, volume_1mo, volume_1yr,
                volume_amm, volume_clob, volume_24hr_amm, volume_24hr_clob,
                volume_1wk_amm, volume_1wk_clob, volume_1mo_amm, volume_1mo_clob,
                volume_1yr_amm, volume_1yr_clob, open_interest,
                outcome_price_yes, outcome_price_no,
                last_trade_price, best_bid, best_ask, spread,
                price_change_1h, price_change_1d, price_change_1wk,
                price_change_1mo, price_change_1yr,
                comment_count, tweet_count,
                fee, taker_base_fee, maker_base_fee, competitive,
                extraction_timestamp
            ) VALUES %s
            ON CONFLICT (market_key, snapshot_date_key) DO UPDATE SET
                liquidity = EXCLUDED.liquidity,
                volume = EXCLUDED.volume,
                volume_24hr = EXCLUDED.volume_24hr,
                outcome_price_yes = EXCLUDED.outcome_price_yes,
                outcome_price_no = EXCLUDED.outcome_price_no,
                last_trade_price = EXCLUDED.last_trade_price,
                best_bid = EXCLUDED.best_bid,
                best_ask = EXCLUDED.best_ask
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        
        count = cursor.rowcount
        self.logger.info(f"✅ Tabla de hechos cargada: {count} registros")
        cursor.close()
    
    def run_full_load(self):
        """
        Ejecuta la carga completa del Data Warehouse
        """
        self.logger.info("\n" + "="*60)
        self.logger.info("INICIANDO CARGA COMPLETA DEL DATA WAREHOUSE")
        self.logger.info("="*60 + "\n")
        
        try:
            # Conectar a NeonDB
            if not self.connect():
                return False
            
            # 1. Cargar dimensión de tiempo
            self.load_dim_time()
            
            # 2. Leer datos de Delta Lake
            self.logger.info("\n📖 Leyendo datos de Delta Lake...")
            
            df_series = self.delta_manager.read_delta_table('series')
            df_tags = self.delta_manager.read_delta_table('tags')
            df_events = self.delta_manager.read_delta_table('events')
            df_markets = self.delta_manager.read_delta_table('markets')
            
            if df_series is None or df_tags is None or df_events is None or df_markets is None:
                self.logger.error("❌ Error al leer datos de Delta Lake")
                return False
            
            self.logger.info(f"   Series: {len(df_series)} registros")
            self.logger.info(f"   Tags: {len(df_tags)} registros")
            self.logger.info(f"   Events: {len(df_events)} registros")
            self.logger.info(f"   Markets: {len(df_markets)} registros")
            
            # 3. Cargar dimensiones
            self.load_dim_series(df_series)
            self.load_dim_tag(df_tags)
            self.load_dim_event(df_events)
            self.load_dim_market(df_markets)
            
            # 4. Cargar tabla puente
            self.load_bridge_market_tag(df_markets)
            
            # 5. Cargar tabla de hechos
            self.load_fact_market_metrics(df_markets)
            
            self.logger.info("\n" + "="*60)
            self.logger.info("✅ CARGA COMPLETA FINALIZADA EXITOSAMENTE")
            self.logger.info("="*60 + "\n")
            
            return True
            
        except Exception as e:
            self.logger.error(f"\n❌ ERROR durante la carga: {str(e)}")
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            self.disconnect()

def main():
    """Función principal"""
    import sys
    
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    if environment not in ['development', 'production']:
        print("❌ Ambiente inválido. Use 'development' o 'production'")
        sys.exit(1)
    
    etl = DataWarehouseETL(environment)
    success = etl.run_full_load()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
