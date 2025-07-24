# src/main.py

import os
from datetime import datetime
import logging
import sys

# Importieren der Module
from dax_movers import get_dax_movers
from chart_generator import create_30_day_chart
from video_maker import create_tiktok_video

# --- Konfiguration ---
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)) # src-Ordner
PROJECT_ROOT = os.path.dirname(PROJECT_ROOT) # Eine Ebene höher zum Projekt-Root

CHARTS_DIR = os.path.join(PROJECT_ROOT, "charts")
VIDEOS_DIR = os.path.join(PROJECT_ROOT, "videos")
MUSIC_DIR = os.path.join(PROJECT_ROOT, "music")
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")

BACKGROUND_MUSIC_FILE = os.path.join(MUSIC_DIR, "background_music.mp3")
VIDEO_DURATION_PER_CHART = 4 # Sekunden pro Chart

# --- Logging Konfiguration ---
os.makedirs(LOGS_DIR, exist_ok=True)
log_filename = os.path.join(LOGS_DIR, f"daily_tiktok_generation_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout) # Auch auf Konsole ausgeben
    ]
)

def run_daily_process():
    logging.info("--- Start der täglichen TikTok-Generierung ---")
    current_date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. Daten abrufen und Mover ermitteln
    logging.info("Schritt 1: DAX Top Mover ermitteln...")
    top_gainers, top_losers, historical_chart_data = get_dax_movers(num_movers=5)

    if top_gainers is None or top_losers is None or historical_chart_data is None:
        logging.error("Fehler beim Abrufen der DAX Mover-Daten. Prozess abgebrochen.")
        return

    # NEU: Erstelle eine geordnete Liste von Movern, die zuerst Gewinner und dann Verlierer enthält.
    # Dies stellt die Reihenfolge der Charts im Video sicher.
    ordered_movers_for_charts = []
    # Außerdem ein Dictionary für video_maker, das die Infos für die Overlays bereitstellt.
    movers_info_for_video_maker = {}

    # Füge Top-Gewinner hinzu (bereits absteigend sortiert nach Performance von get_dax_movers)
    for ticker, change in top_gainers.items():
        ordered_movers_for_charts.append((ticker, change, 'gainer'))
        movers_info_for_video_maker[ticker] = {'change': change, 'type': 'gainer'}

    # Füge Top-Verlierer hinzu (bereits aufsteigend sortiert nach Performance von get_dax_movers)
    for ticker, change in top_losers.items():
        ordered_movers_for_charts.append((ticker, change, 'loser'))
        movers_info_for_video_maker[ticker] = {'change': change, 'type': 'loser'}

    if not ordered_movers_for_charts:
        logging.warning("Keine Mover gefunden. Kein Video wird generiert.")
        return

    # 2. Charts generieren
    logging.info("Schritt 2: Charts generieren...")
    generated_chart_files = []

    # Iteriere über die geordnete Liste, um die Charts in der gewünschten Reihenfolge zu erstellen
    for ticker, percentage_change, mover_type in ordered_movers_for_charts:
        if ticker in historical_chart_data:
            try:
                chart_filename = create_30_day_chart(ticker, historical_chart_data[ticker], percentage_change, CHARTS_DIR)
                generated_chart_files.append(chart_filename)
                logging.info(f"Chart für {ticker} ({mover_type}) erstellt: {chart_filename}")
            except Exception as e:
                logging.error(f"Fehler beim Erstellen des Charts für {ticker}: {e}")
        else:
            logging.warning(f"Keine historischen Daten für {ticker} gefunden, Chart kann nicht erstellt werden.")

    if not generated_chart_files:
        logging.error("Keine Charts generiert. Video kann nicht erstellt werden. Prozess abgebrochen.")
        return

    # 3. Video generieren
    logging.info("Schritt 3: Video generieren...")
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    output_video_filename = os.path.join(VIDEOS_DIR, f"dax_top_movers_{current_date_str}.mp4")

    try:
        create_tiktok_video(
            chart_image_paths=generated_chart_files,
            output_filepath=output_video_filename,
            background_music_path=BACKGROUND_MUSIC_FILE,
            chart_display_duration=VIDEO_DURATION_PER_CHART,
            movers_info=movers_info_for_video_maker # Übergabe des Dictionaries für Text-Overlays
        )
        logging.info(f"TikTok-Video erfolgreich erstellt: {output_video_filename}")
    except FileNotFoundError as e:
        logging.error(f"Fehler: Musikdatei oder FFmpeg nicht gefunden. {e}")
        logging.error("Stellen Sie sicher, dass FFmpeg korrekt installiert und im PATH ist, und die Musikdatei existiert.")
    except Exception as e:
        logging.error(f"Ein unerwarteter Fehler bei der Videogenerierung ist aufgetreten: {e}", exc_info=True)
    finally:
        # Optional: Aufräumen der generierten Charts nach Videoerstellung
        logging.info("Schritt 4: Aufräumen der temporären Chart-Bilder...")
        for chart_file in generated_chart_files:
            try:
                os.remove(chart_file)
                logging.info(f"Gelöscht: {chart_file}")
            except Exception as e:
                logging.warning(f"Konnte Chart-Datei nicht löschen {chart_file}: {e}")

    logging.info("--- Ende der täglichen TikTok-Generierung ---")

if __name__ == "__main__":
    run_daily_process()