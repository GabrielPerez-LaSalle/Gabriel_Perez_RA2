"""
ETL Simplificado: CSV Exports → NeonDB Data Warehouse
Versión alternativa que lee desde los CSVs exportados
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fase2_warehouse.neondb_config import get_connection_string, DEFAULT_ENVIRONMENT
import logging

class CSVtoWarehouseETL:
    """
    ETL simplificado que lee desde CSV
    """
    
    def __init__(self, environment=DEFAULT_ENVIRONMENT):
        self.environment = environment
        self.conn = None
        self.data_dir = "data/exported"
        
    def connect(self):
        """Conectar a NeonDB"""
        try:
            print(f"Conectando a NeonDB ({self.environment})...")
            self.conn = psycopg2.connect(get_connection_string(self.environment))
            self.conn.autocommit = False
            print("Conexion establecida")
            return True
        except Exception as e:
            print(f"Error al conectar: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar"""
        if self.conn:
            self.conn.close()
            print("Conexion cerrada")
    
    def clean_value(self, value):
        """Limpia valores"""
        if pd.isna(value):
            return None
        if isinstance(value, str) and value.strip() == '':
            return None
        return value
    
    def parse_json_field(self, value):
        """Parsea JSON"""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, str):
            try:
                return json.loads(value.replace("'", '"'))
            except:
                return None
        return value
    
    def extract_outcome_prices(self, outcome_prices_str):
        """Desanida precios"""
        prices = self.parse_json_field(outcome_prices_str)
        if not prices or not isinstance(prices, list):
            return None, None
        
        try:
            price_yes = float(prices[0]) if len(prices) > 0 else None
            price_no = float(prices[1]) if len(prices) > 1 else None
            return price_yes, price_no
        except:
            return None, None
    
    def load_dim_time(self):
        """Carga dimension de tiempo"""
        print("Cargando dimension de tiempo...")
        
        cursor = self.conn.cursor()
        dates = pd.date_range(start='2021-01-01', end='2026-12-31', freq='D')
        
        records = []
        for dt in dates:
            record = (
                dt.date(), dt.year, (dt.month - 1) // 3 + 1, dt.month,
                dt.strftime('%B'), dt.isocalendar()[1], dt.day, dt.dayofweek,
                dt.strftime('%A'), dt.dayofweek >= 5,
                dt.day == 1, dt.day == pd.Period(dt, 'M').days_in_month,
                dt.day == 1 and dt.month in [1, 4, 7, 10],
                dt.day == pd.Period(dt, 'M').days_in_month and dt.month in [3, 6, 9, 12],
                dt.day == 1 and dt.month == 1, dt.day == 31 and dt.month == 12,
                dt.year, (dt.month - 1) // 3 + 1
            )
            records.append(record)
        
        query = """
            INSERT INTO dim_time (
                date_value, year, quarter, month, month_name, week_of_year,
                day_of_month, day_of_week, day_name, is_weekend,
                is_month_start, is_month_end, is_quarter_start, is_quarter_end,
                is_year_start, is_year_end, fiscal_year,fiscal_quarter
            ) VALUES %s ON CONFLICT (date_value) DO NOTHING
        """
        
        execute_values(cursor, query, records)
        self.conn.commit()
        print(f"Dimension tiempo cargada: {cursor.rowcount} registros")
        cursor.close()
    
    def get_time_key(self, date_value):
        """Obtiene time_key"""
        if pd.isna(date_value) or date_value is None:
            return None
        
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
    
    def load_all(self):
        """Carga completa"""
        print("\n" + "="*60)
        print("INICIANDO CARGA COMPLETA DEL DATA WAREHOUSE")
        print("="*60 + "\n")
        
        try:
            if not self.connect():
                return False
            
            # 1. Cargar dimension tiempo
            self.load_dim_time()
            
            # 2. Leer CSVs
            print("\nLeyendo archivos CSV...")
            
            csv_files = {
                'series': f"{self.data_dir}/series_20260216_193759.csv",
                'tags': f"{self.data_dir}/tags_20260216_193829.csv",
                'events': f"{self.data_dir}/events_20260216_193533.csv",
                'markets': f"{self.data_dir}/markets_20260216_193645.csv"
            }
            
            # Verificar que existan
            for name, path in csv_files.items():
                if not os.path.exists(path):
                    print(f"ERROR: No se encontro {path}")
                    return False
            
            # Leer con manejo de errores
            print("Leyendo series...")
            df_series = pd.read_csv(csv_files['series'], low_memory=False)
            print(f"  Series: {len(df_series)} registros")
            
            print("Leyendo tags...")
            df_tags = pd.read_csv(csv_files['tags'], low_memory=False)
            print(f"  Tags: {len(df_tags)} registros")
            
            print("Leyendo events...")
            df_events = pd.read_csv(csv_files['events'], low_memory=False)
            print(f"  Events: {len(df_events)} registros")
            
            print("Leyendo markets...")
            df_markets = pd.read_csv(csv_files['markets'], low_memory=False)
            print(f"  Markets: {len(df_markets)} registros")
            
            # 3. Cargar dimensiones
            print("\nCargando dimensiones...")
            
            # Series
            print("Cargando dim_series...")
            cursor = self.conn.cursor()
            series_records = []
            for _, row in df_series.iterrows():
                record = (
                    self.clean_value(row.get('id')),
                    self.clean_value(row.get('slug')),
                    self.clean_value(row.get('title')),
                    None,  # description
                    self.clean_value(row.get('image')),
                    self.clean_value(row.get('icon')),
                    None,  # series_type
                    None,  # recurrence
                    self.clean_value(row.get('active')),
                    False,  # closed
                    False,  # archived
                    False,  # restricted
                    False,  # featured
                    None,  # layout
                    None,  # start_date
                    None,  # published_at
                    None,  # created_at
                    None,  # updated_at
                    None,  # created_by
                    None   # updated_by
                )
                series_records.append(record)
            
            query = """
                INSERT INTO dim_series (
                    series_id, slug, title, description, image, icon,
                    series_type, recurrence, active, closed, archived, restricted,
                    featured, layout, start_date, published_at, created_at_source,
                    updated_at_source, created_by, updated_by
                ) VALUES %s
                ON CONFLICT (series_id) DO NOTHING
            """
            execute_values(cursor, query, series_records)
            self.conn.commit()
            print(f"  dim_series: {cursor.rowcount} registros")
            
            # Tags
            print("Cargando dim_tag...")
            tag_records = []
            for _, row in df_tags.iterrows():
                tag_id = self.clean_value(row.get('id'))
                slug = self.clean_value(row.get('slug'))
                path = f"/{slug}" if slug else None
                
                record = (
                    tag_id,
                    self.clean_value(row.get('label')),
                    slug,
                    None,  # parent_tag_id
                    1,     # level
                    path,
                    False,  # force_show
                    False,  # force_hide
                    False,  # is_carousel
                    False,  # requires_translation
                    None,  # published_at
                    None,  # created_at
                    None,  # updated_at
                    None,  # created_by
                    None   # updated_by
                )
                tag_records.append(record)
            
            query = """
                INSERT INTO dim_tag (
                    tag_id, label, slug, parent_tag_id, level, path,
                    force_show, force_hide, is_carousel, requires_translation,
                    published_at, created_at_source, updated_at_source,
                    created_by, updated_by
                ) VALUES %s
                ON CONFLICT (tag_id) DO NOTHING
            """
            execute_values(cursor, query, tag_records)
            self.conn.commit()
            print(f"  dim_tag: {cursor.rowcount} registros")
            
            # Events - tomar una muestra si son muchos
            print("Cargando dim_event...")
            event_records = []
            for idx, row in df_events.head(1000).iterrows():  # Limitar a 1000 para prueba
                record = (
                    int(self.clean_value(row.get('id')) or 0),
                    self.clean_value(row.get('ticker')),
                    self.clean_value(row.get('slug')),
                    self.clean_value(row.get('title')),
                    self.clean_value(row.get('description')),
                    self.clean_value(row.get('category')),
                    None,  # subcategory
                    self.clean_value(row.get('image')),
                    self.clean_value(row.get('icon')),
                    None,  # resolution_source
                    self.clean_value(row.get('active')),
                    self.clean_value(row.get('closed')),
                    False,  # archived
                    False,  # new
                    False,  # featured
                    False,  # restricted
                    False,  # cyom
                    0,  # competitive
                    None,  # start_date
                    None,  # creation_date
                    None,  # end_date
                    None,  # closed_time
                    None,  # published_at
                    None,  # created_at
                    None,  # updated_at
                    False,  # show_all_outcomes
                    False,  # show_market_images
                    False,  # enable_neg_risk
                    False,  # enable_order_book
                    False,  # neg_risk_augmented
                    False,  # pending_deployment
                    False,  # deploying
                    False,  # requires_translation
                    False,  # comments_enabled
                    None,  # series_slug
                    None,  # parent_event_id
                    None,  # sport
                    None,  # event_date
                    None,  # event_week
                    None,  # game_id
                    None   # game_status
                )
                event_records.append(record)
            
            if event_records:
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
                    ON CONFLICT (event_id) DO NOTHING
                """
                execute_values(cursor, query, event_records)
                self.conn.commit()
                print(f"  dim_event: {cursor.rowcount} registros")
            
            # Markets - muestra
            print("Cargando dim_market...")
            market_records = []
            for idx, row in df_markets.head(1000).iterrows():
                outcomes = self.parse_json_field(row.get('outcomes'))
                outcomes_json = json.dumps(outcomes) if outcomes else None
                
                record = (
                    str(self.clean_value(row.get('id'))),
                    self.clean_value(row.get('conditionId')),
                    self.clean_value(row.get('slug')),
                    self.clean_value(row.get('question')),
                    None,  # description
                    None,  # market_type
                    self.clean_value(row.get('category')),
                    None,  # subcategory
                    outcomes_json,
                    self.clean_value(row.get('active')),
                    self.clean_value(row.get('closed')),
                    False,  # archived
                    False,  # restricted
                    False,  # new
                    False,  # featured
                    False,  # enable_order_book
                    False,  # clear_book_on_start
                    False,  # fppm_live
                    False,  # rfq_enabled
                    None,  # start_date
                    None,  # end_date
                    None,  # closed_time
                    None,  # created_at
                    None,  # updated_at
                    self.clean_value(row.get('image')),
                    None,  # icon
                    None,  # resolution_source
                    False,  # neg_risk
                    None,  # neg_risk_market_id
                    None,  # format_type
                    False,  # wide_format
                    None,  # lower_bound
                    None,  # upper_bound
                    None,  # question_id
                    None   # market_maker_address
                )
                market_records.append(record)
            
            if market_records:
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
                    ON CONFLICT (market_id) DO NOTHING
                """
                execute_values(cursor, query, market_records)
                self.conn.commit()
                print(f"  dim_market: {cursor.rowcount} registros")
            
            # Fact table - muestra
            print("Cargando fact_market_metrics...")
            
            # Obtener mapeos
            cursor.execute("SELECT market_id, market_key FROM dim_market")
            market_map = {str(row[0]): row[1] for row in cursor.fetchall()}
            
            fact_records = []
            for idx, row in df_markets.head(1000).iterrows():
                market_id = str(self.clean_value(row.get('id')))
                market_key = market_map.get(market_id)
                
                if not market_key:
                    continue
                
                snapshot_date = datetime.now().date()
                snapshot_date_key = self.get_time_key(snapshot_date)
                
                if not snapshot_date_key:
                    continue
                
                price_yes, price_no = self.extract_outcome_prices(row.get('outcomePrices'))
                
                record = (
                    market_key, None, None, snapshot_date_key, None, None, None,
                    self.clean_value(row.get('liquidity')), None, None,
                    self.clean_value(row.get('volume')), None, None, None, None,
                    None, None, None, None, None, None, None, None, None, None,
                    0,  # open_interest
                    price_yes, price_no,
                    None, None, None, None, None, None, None, None, None,
                    0, 0,  # comment_count, tweet_count
                    None, None, None, 0, None
                )
                fact_records.append(record)
            
            if fact_records:
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
                    ON CONFLICT (market_key, snapshot_date_key) DO NOTHING
                """
                execute_values(cursor, query, fact_records)
                self.conn.commit()
                print(f"  fact_market_metrics: {cursor.rowcount} registros")
            
            cursor.close()
            
            print("\n" + "="*60)
            print("CARGA COMPLETA FINALIZADA EXITOSAMENTE")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"\nERROR durante la carga: {str(e)}")
            import traceback
            traceback.print_exc()
            if self.conn:
                self.conn.rollback()
            return False
            
        finally:
            self.disconnect()

def main():
    environment = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ENVIRONMENT
    
    if environment not in ['development', 'production']:
        print("Ambiente invalido. Use 'development' o 'production'")
        sys.exit(1)
    
    etl = CSVtoWarehouseETL(environment)
    success = etl.load_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
