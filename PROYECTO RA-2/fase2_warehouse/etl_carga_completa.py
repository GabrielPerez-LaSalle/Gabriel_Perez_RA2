"""
ETL Completo y Optimizado: CSV → NeonDB Data Warehouse
Carga todos los datos sin límites
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

class ETLCompleto:
    """ETL optimizado para carga completa"""
    
    def __init__(self, environment=DEFAULT_ENVIRONMENT, batch_size=5000):
        self.environment = environment
        self.conn = None
        self.data_dir = "data/exported"
        self.batch_size = batch_size
        
    def connect(self):
        """Conectar a NeonDB"""
        try:
            print(f"\nConectando a NeonDB ({self.environment})...")
            self.conn = psycopg2.connect(get_connection_string(self.environment))
            self.conn.autocommit = False
            print("OK: Conexion establecida\n")
            return True
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return False
    
    def disconnect(self):
        """Desconectar"""
        if self.conn:
            self.conn.close()
            print("\nOK: Conexion cerrada")
    
    def clean_numeric(self, value, max_val=9999999999):
        """Limpia valores numéricos y valida rangos"""
        if pd.isna(value) or value is None:
            return None
        try:
            num = float(value)
            # Validar rango para NUMERIC(20,10): abs(value) < 10^10
            if abs(num) >= max_val:
                return None  # Valor fuera de rango, tratar como NULL
            return num
        except:
            return None
    
    def clean_value(self, value):
        """Limpia valores"""
        if pd.isna(value):
            return None
        if isinstance(value, str) and value.strip() == '':
            return None
        return value
    
    def parse_json_field(self, value):
        """Parsea JSON con manejo robusto"""
        if pd.isna(value) or value is None:
            return None
        if isinstance(value, str):
            try:
                # Intentar parsear como JSON primero
                return json.loads(value)
            except:
                try:
                    # Intentar con comillas simples reemplazadas
                    return json.loads(value.replace("'", '"'))
                except:
                    try:
                        # Evaluar como expresión Python (seguro para listas/dicts)
                        import ast
                        return ast.literal_eval(value)
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
    
    def load_all(self):
        """Carga completa"""
        print("="*70)
        print("CARGA COMPLETA DEL DATA WAREHOUSE - SIN LIMITES")
        print("="*70)
        
        try:
            if not self.connect():
                return False
            
            cursor = self.conn.cursor()
            
            # Leer CSVs
            print("[1/9] Leyendo archivos CSV...")
            csv_files = {
                'series': f"{self.data_dir}/series_20260216_193759.csv",
                'tags': f"{self.data_dir}/tags_20260216_193829.csv",
                'events': f"{self.data_dir}/events_20260216_193533.csv",
                'markets': f"{self.data_dir}/markets_20260216_193645.csv"
            }
            
            df_series = pd.read_csv(csv_files['series'], low_memory=False)
            print(f"  - Series: {len(df_series):,} registros")
            
            df_tags = pd.read_csv(csv_files['tags'], low_memory=False)
            print(f"  - Tags: {len(df_tags):,} registros")
            
            df_events = pd.read_csv(csv_files['events'], low_memory=False)
            print(f"  - Events: {len(df_events):,} registros")
            
            df_markets = pd.read_csv(csv_files['markets'], low_memory=False)
            print(f"  - Markets: {len(df_markets):,} registros")
            
            # LIMPIAR tablas FAC y BRIDGE solamente para recarga limpia
            # NO limpiar dimensiones para permitir ejecuciones incrementales
            print("\n[2/9] Preparando carga...")
            cursor.execute("TRUNCATE fact_market_metrics CASCADE")
            cursor.execute("TRUNCATE bridge_market_tag CASCADE")
            self.conn.commit()
            print("  OK: Tablas fact/bridge limpiadas (dimensiones se actualizaran)")
            
            # DIM_SERIES
            print("\n[3/9] Cargando dim_series...")
            # Deduplicar por series_id
            df_series_unique = df_series.drop_duplicates(subset=['id'], keep='first')
            print(f"  - Series unicas: {len(df_series_unique):,} (de {len(df_series):,} totales)")
            
            series_records = []
            for _, row in df_series_unique.iterrows():
                record = (
                    self.clean_value(row.get('id')),
                    self.clean_value(row.get('slug')),
                    self.clean_value(row.get('title')),
                    None, None, None, None, None,
                    self.clean_value(row.get('active')),
                    False, False, False, False, None, None,
                    None, None, None, None, None
                )
                series_records.append(record)
            
            if series_records:
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
                print(f"  OK: {cursor.rowcount:,} registros")
            
            # DIM_TAG
            print("\n[4/9] Cargando dim_tag...")
            # Deduplicar tags por tag_id (tomar el primero)
            df_tags_unique = df_tags.drop_duplicates(subset=['id'], keep='first')
            print(f"  - Tags unicos: {len(df_tags_unique):,} (de {len(df_tags):,} totales)")
            
            tag_records = []
            for _, row in df_tags_unique.iterrows():
                tag_id = self.clean_value(row.get('id'))
                slug = self.clean_value(row.get('slug'))
                path = f"/{slug}" if slug else None
                
                record = (
                    tag_id, self.clean_value(row.get('label')), slug,
                    None, 1, path, False, False, False, False,
                    None, None, None, None, None
                )
                tag_records.append(record)
            
            if tag_records:
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
                print(f"  OK: {cursor.rowcount:,} registros")
            
            # DIM_EVENT - TODOS LOS DATOS
            print(f"\n[5/9] Cargando dim_event (COMPLETO - {len(df_events):,} registros)...")
            print("  Procesando en batches...")
            
            total_events = 0
            for i in range(0, len(df_events), self.batch_size):
                batch = df_events.iloc[i:i+self.batch_size]
                event_records = []
                
                for _, row in batch.iterrows():
                    record = (
                        int(self.clean_value(row.get('id')) or 0),
                        self.clean_value(row.get('ticker')),
                        self.clean_value(row.get('slug')),
                        self.clean_value(row.get('title')),
                        None,  # description
                        self.clean_value(row.get('category')),
                        None,  # subcategory
                        None,  # image
                        None,  # icon
                        None,  # resolution_source
                        self.clean_value(row.get('active')),
                        self.clean_value(row.get('closed')),
                        False, False, False, False, False, 0,
                        None, None, None, None, None, None, None,
                        False, False, False, False, False, False, False, False, False,
                        None, None, None, None, None, None, None
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
                    total_events += len(batch)
                    
                if (i + self.batch_size) % 50000 == 0 or (i + self.batch_size) >= len(df_events):
                    print(f"    Procesados: {min(i + self.batch_size, len(df_events)):,} de {len(df_events):,} ({100*(i+self.batch_size)/len(df_events):.1f}%)")
            
            # Verificar cuántos se insertaron realmente
            cursor.execute("SELECT COUNT(*) FROM dim_event WHERE event_key > 0")
            count_db = cursor.fetchone()[0]
            print(f"  OK: {count_db:,} registros en base de datos")
            
            # DIM_MARKET - TODOS LOS DATOS
            print(f"\n[6/9] Cargando dim_market (COMPLETO - {len(df_markets):,} registros)...")
            print("  Procesando en batches...")
            
            total_markets = 0
            for i in range(0, len(df_markets), self.batch_size):
                batch = df_markets.iloc[i:i+self.batch_size]
                market_records = []
                
                for _, row in batch.iterrows():
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
                        False, False, False, False, False, False, False, False,
                        None, None, None, None, None, None, None, None,
                        False, None, None, False, None, None, None, None
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
                    execute_values(cursor, query, market_records, page_size=1000)
                    self.conn.commit()
                    total_markets += len(batch)
                    
                if (i + self.batch_size) % 25000 == 0 or (i + self.batch_size) >= len(df_markets):
                    cursor.execute("SELECT COUNT(*) FROM dim_market WHERE market_key > 0")
                    count_db = cursor.fetchone()[0]
                    pct = 100 * (i + self.batch_size) / len(df_markets)
                    print(f"    Procesados: {min(i + self.batch_size, len(df_markets)):,} de {len(df_markets):,} ({pct:.1f}%) | DB: {count_db:,}")
            
            # Count final
            cursor.execute("SELECT COUNT(*) FROM dim_market WHERE market_key > 0")
            count_db = cursor.fetchone()[0]
            print(f"  OK: {count_db:,} registros en base de datos")
            
            # BRIDGE_MARKET_TAG
            print(f"\n[7/9] Cargando bridge_market_tag...")
            
            # Obtener mapeos
            cursor.execute("SELECT market_id, market_key FROM dim_market")
            market_map = {str(row[0]): row[1] for row in cursor.fetchall()}
            print(f"  - Mapeando {len(market_map):,} markets")
            
            cursor.execute("SELECT tag_id, tag_key FROM dim_tag")
            tag_map = {str(row[0]): row[1] for row in cursor.fetchall()}
            print(f"  - Mapeando {len(tag_map):,} tags")
            
            # Extraer relaciones de los events (tienen tags)
            bridge_records = set()  # Usar set para evitar duplicados
            events_with_tags = 0
            events_with_markets = 0
            events_with_both = 0
            
            print(f"  - Procesando {len(df_events):,} events...")
            
            for idx, row in df_events.iterrows():
                # Parsear tags del evento
                tags_str = self.clean_value(row.get('tags'))
                tags_list = None
                
                if tags_str:
                    tags_list = self.parse_json_field(tags_str)
                    if isinstance(tags_list, list) and len(tags_list) > 0:
                        events_with_tags += 1
                
                # Parsear markets del evento
                markets_str = self.clean_value(row.get('markets'))
                markets_list = None
                
                if markets_str:
                    markets_list = self.parse_json_field(markets_str)
                    if isinstance(markets_list, list) and len(markets_list) > 0:
                        events_with_markets += 1
                
                # Solo si tiene ambos
                if isinstance(tags_list, list) and isinstance(markets_list, list):
                    if len(tags_list) > 0 and len(markets_list) > 0:
                        events_with_both += 1
                        
                        for market_dict in markets_list:
                            if isinstance(market_dict, dict):
                                market_id = str(market_dict.get('id', ''))
                                market_key = market_map.get(market_id)
                                
                                if market_key:
                                    for tag_dict in tags_list:
                                        if isinstance(tag_dict, dict):
                                            tag_id = str(tag_dict.get('id', ''))
                                            tag_key = tag_map.get(tag_id)
                                            
                                            if tag_key:
                                                bridge_records.add((market_key, tag_key))
                
                # Progreso cada 50k
                if (idx + 1) % 50000 == 0:
                    print(f"    Procesados: {idx + 1:,} events | {len(bridge_records):,} relaciones encontradas")
            
            print(f"  - Events con tags: {events_with_tags:,}")
            print(f"  - Events con markets: {events_with_markets:,}")
            print(f"  - Events con ambos: {events_with_both:,}")
            print(f"  - Total relaciones unicas: {len(bridge_records):,}")
            
            if bridge_records:
                query = """
                    INSERT INTO bridge_market_tag (market_key, tag_key)
                    VALUES %s
                    ON CONFLICT (market_key, tag_key) DO NOTHING
                """
                execute_values(cursor, query, list(bridge_records))
                self.conn.commit()
                print(f"  OK: {cursor.rowcount:,} relaciones insertadas")
            else:
                print("  WARN: No se encontraron relaciones market-tag")
            
            # FACT_MARKET_METRICS
            print(f"\n[8/9] Cargando fact_market_metrics...")
            print("  Procesando en batches...")
            
            # Obtener snapshot_date_key actual
            cursor.execute("SELECT time_key FROM dim_time WHERE date_value = CURRENT_DATE")
            result = cursor.fetchone()
            snapshot_date_key = result[0] if result else None
            
            if not snapshot_date_key:
                print("  ERROR: No se encontro time_key para fecha actual")
            else:
                total_facts = 0
                for i in range(0, len(df_markets), self.batch_size):
                    batch = df_markets.iloc[i:i+self.batch_size]
                    fact_records = []
                    
                    for _, row in batch.iterrows():
                        market_id = str(self.clean_value(row.get('id')))
                        market_key = market_map.get(market_id)
                        
                        if not market_key:
                            continue
                        
                        price_yes, price_no = self.extract_outcome_prices(row.get('outcomePrices'))
                        
                        # Limpiar precios que parecen valores sentinela (>100 no tiene sentido para precios 0-1)
                        if price_yes and price_yes > 10:
                            price_yes = None
                        if price_no and price_no > 10:
                            price_no = None
                        
                        record = (
                            market_key, None, None, snapshot_date_key, None, None, None,
                            self.clean_numeric(row.get('liquidity')),
                            self.clean_numeric(row.get('liquidityAmm')),
                            self.clean_numeric(row.get('liquidityClob')),
                            self.clean_numeric(row.get('volume')),
                            self.clean_numeric(row.get('volume24hr')),
                            self.clean_numeric(row.get('volume1wk')),
                            self.clean_numeric(row.get('volume1mo')),
                            self.clean_numeric(row.get('volume1yr')),
                            self.clean_numeric(row.get('volumeAmm')),
                            self.clean_numeric(row.get('volumeClob')),
                            self.clean_numeric(row.get('volume24hrAmm')),
                            self.clean_numeric(row.get('volume24hrClob')),
                            self.clean_numeric(row.get('volume1wkAmm')),
                            self.clean_numeric(row.get('volume1wkClob')),
                            self.clean_numeric(row.get('volume1moAmm')),
                            self.clean_numeric(row.get('volume1moClob')),
                            self.clean_numeric(row.get('volume1yrAmm')),
                            self.clean_numeric(row.get('volume1yrClob')),
                            0,  # open_interest
                            price_yes, price_no,
                            self.clean_numeric(row.get('lastTradePrice'), 1),  # Prices should be 0-1
                            self.clean_numeric(row.get('bestBid'), 1),
                            self.clean_numeric(row.get('bestAsk'), 1),
                            self.clean_numeric(row.get('spread'), 1),
                            self.clean_numeric(row.get('oneHourPriceChange'), 10),
                            self.clean_numeric(row.get('oneDayPriceChange'), 10),
                            self.clean_numeric(row.get('oneWeekPriceChange'), 10),
                            self.clean_numeric(row.get('oneMonthPriceChange'), 10),
                            self.clean_numeric(row.get('oneYearPriceChange'), 10),
                            0, 0,  # comment_count, tweet_count
                            self.clean_numeric(row.get('fee'), 1000),  # Fee should be reasonable (<1000%)
                            self.clean_numeric(row.get('takerBaseFee'), 1000),
                            self.clean_numeric(row.get('makerBaseFee'), 1000),
                            self.clean_numeric(row.get('competitive'), 1),
                            None  # extraction_timestamp
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
                        total_facts += cursor.rowcount
                    
                    if (i + self.batch_size) % 50000 == 0:
                        print(f"    Procesados: {i + self.batch_size:,}...")
                
                print(f"  OK: {total_facts:,} registros")
            
            cursor.close()
            
            # Resumen final
            print("\n[9/9] Resumen de carga...")
            cursor = self.conn.cursor()
            
            tables = ['dim_series', 'dim_tag', 'dim_event', 'dim_market', 
                     'bridge_market_tag', 'fact_market_metrics']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table:25s} {count:>10,} registros")
            
            cursor.close()
            
            print("\n" + "="*70)
            print("CARGA COMPLETA FINALIZADA CON EXITO")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\nERROR: {str(e)}")
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
    
    etl = ETLCompleto(environment, batch_size=5000)
    success = etl.load_all()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
