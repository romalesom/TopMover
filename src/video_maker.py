# src/video_maker.py

import cv2
import numpy as np
import os
import logging
from datetime import datetime
import subprocess # Für FFmpeg Aufrufe

# --- Konfiguration ---
# Video-Dimensionen für TikTok (Hochformat)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 24 # Bilder pro Sekunde für das Ausgabevideo

# Schriftart und -größe für OpenCV-Text
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE_TITLE = 3.0
FONT_SCALE_CHANGE = 2.5
THICKNESS = 4 # Linienstärke des Textes

# Farben (BGR-Format für OpenCV)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0) # BGR
RED = (0, 0, 255)   # BGR

def create_tiktok_video(
    chart_image_paths: list,
    output_filepath: str,
    background_music_path: str,
    chart_display_duration: int,
    movers_info: dict # Dictionary: {ticker: {'change': float, 'type': 'gainer'/'loser'}}
):
    """
    Erstellt ein TikTok-kompatibles Video aus einer Liste von Chart-Bildern,
    fügt Text-Overlays hinzu und integriert Hintergrundmusik.
    Verwendet OpenCV für die Videogenerierung und subprocess für FFmpeg-Audio-Merging.
    """
    logging.info(f"Starte Videogenerierung mit OpenCV. Anzahl Charts: {len(chart_image_paths)}")

    # Temporäre Datei für Video ohne Audio
    temp_video_filepath = output_filepath.replace(".mp4", "_no_audio.mp4")

    # VideoWriter initialisieren
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec für .mp4
    out = cv2.VideoWriter(temp_video_filepath, fourcc, FPS, (VIDEO_WIDTH, VIDEO_HEIGHT))

    if not out.isOpened():
        logging.error(f"Fehler: VideoWriter konnte nicht geöffnet werden für {temp_video_filepath}")
        return

    # --- Intro-Clip erstellen ---
    line1 = "Die 10 DAX Highlights des Tages!"
    line2 = f"Ist ihr Portfolio betroffen?"
    intro_duration_frames = int(2 * FPS)  # 2 Sekunden Intro

    # Schwarzer Hintergrund für das Intro
    intro_frame = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)

    # Einheitlicher Skalierungsfaktor für Intro-Text
    FONT_SCALE_INTRO = FONT_SCALE_TITLE * 0.5

    # Textgrößen berechnen mit korrektem Skalierungsfaktor
    (text_w1, text_h1), _ = cv2.getTextSize(line1, FONT, FONT_SCALE_INTRO, THICKNESS)
    (text_w2, text_h2), _ = cv2.getTextSize(line2, FONT, FONT_SCALE_INTRO, THICKNESS)

    # Abstand und Gesamthöhe
    line_spacing = int(text_h1 * 1.5)
    total_text_height = text_h1 + line_spacing

    # Start-Y für vertikale Zentrierung
    start_y = (VIDEO_HEIGHT - total_text_height) // 2

    # Positionen berechnen (horizontal zentriert)
    x1 = (VIDEO_WIDTH - text_w1) // 2
    y1 = start_y + text_h1  # y-Koordinate ist bei Baseline

    x2 = (VIDEO_WIDTH - text_w2) // 2
    y2 = y1 + line_spacing

    # Zeilen zeichnen mit identischem Skalierungsfaktor
    cv2.putText(intro_frame, line1, (x1, y1), FONT, FONT_SCALE_INTRO, WHITE, THICKNESS, cv2.LINE_AA)
    cv2.putText(intro_frame, line2, (x2, y2), FONT, FONT_SCALE_INTRO, WHITE, THICKNESS, cv2.LINE_AA)

    for _ in range(intro_duration_frames):
        out.write(intro_frame)

    logging.info("Intro-Clip hinzugefügt.")

    # --- Chart-Clips ---
    frames_per_chart = int(chart_display_duration * FPS)

    for i, chart_path in enumerate(chart_image_paths):
        logging.info(f"Verarbeite Chart: {chart_path}")
        # Bild laden
        chart_image = cv2.imread(chart_path)
        if chart_image is None:
            logging.error(f"Fehler: Bild konnte nicht geladen werden von {chart_path}. Überspringe.")
            continue

        # Bild auf Video-Dimensionen anpassen (resizen)
        chart_image_resized = cv2.resize(chart_image, (VIDEO_WIDTH, VIDEO_HEIGHT))

        # # Ticker aus Dateipfad extrahieren (z.B. "BAS_30_day_chart.png" -> "BAS")
        # base_name = os.path.basename(chart_path)
        # ticker_name = base_name.split('_')[0]

        # # Informationen für den Text-Overlay abrufen
        # percentage_change = movers_info.get(ticker_name, {}).get('change', 0.0)
        # display_text_change = f"{percentage_change:.2f}%"
        # text_color = GREEN if percentage_change >= 0 else RED

        # Füge Text-Overlays zu jedem Frame hinzu
        for frame_num in range(frames_per_chart):
            frame_to_write = chart_image_resized.copy() # Kopie, um Text hinzuzufügen

            # Ticker-Text (oben zentriert)
            # (text_w_ticker, text_h_ticker), _ = cv2.getTextSize(ticker_name, FONT, FONT_SCALE_TITLE, THICKNESS)
            # text_x_ticker = (VIDEO_WIDTH - text_w_ticker) // 2
            # text_y_ticker = int(VIDEO_HEIGHT * 0.1) + text_h_ticker // 2 # Position anpassen

            # cv2.putText(frame_to_write, ticker_name, (text_x_ticker, text_y_ticker),
            #             FONT, FONT_SCALE_TITLE, WHITE, THICKNESS, cv2.LINE_AA)

            # Prozentuale Veränderung (etwas darunter zentriert)
            # (text_w_change, text_h_change), _ = cv2.getTextSize(display_text_change, FONT, FONT_SCALE_CHANGE, THICKNESS)
            # text_x_change = (VIDEO_WIDTH - text_w_change) // 2
            # text_y_change = int(VIDEO_HEIGHT * 0.25) + text_h_change // 2 # Position anpassen

            # cv2.putText(frame_to_write, display_text_change, (text_x_change, text_y_change),
            #             FONT, FONT_SCALE_CHANGE, text_color, THICKNESS, cv2.LINE_AA)

            out.write(frame_to_write)
    logging.info("Chart-Clips hinzugefügt.")

    # --- Outro-Clip erstellen ---
    line1 = "Daily DAX-Updates!"
    line2 = "Follow us!"
    outro_duration_frames = int(3 * FPS)  # 3 Sekunden Outro

    outro_frame = np.zeros((VIDEO_HEIGHT, VIDEO_WIDTH, 3), dtype=np.uint8)

    # Textgrößen berechnen
    (text_w1, text_h1), _ = cv2.getTextSize(line1, FONT, FONT_SCALE_TITLE * 0.8, THICKNESS)
    (text_w2, text_h2), _ = cv2.getTextSize(line2, FONT, FONT_SCALE_TITLE * 0.8, THICKNESS)

    # Y-Startpunkt mittig mit etwas Abstand
    line_spacing = int(text_h1 * 1.5)
    total_text_height = line_spacing + text_h2
    start_y = (VIDEO_HEIGHT - total_text_height) // 2

    # Zeile 1 zentrieren
    x1 = (VIDEO_WIDTH - text_w1) // 2
    y1 = start_y

    # Zeile 2 zentrieren
    x2 = (VIDEO_WIDTH - text_w2) // 2
    y2 = y1 + line_spacing

    # Texte zeichnen
    cv2.putText(outro_frame, line1, (x1, y1), FONT, FONT_SCALE_TITLE * 0.8, WHITE, THICKNESS, cv2.LINE_AA)
    cv2.putText(outro_frame, line2, (x2, y2), FONT, FONT_SCALE_TITLE * 0.8, WHITE, THICKNESS, cv2.LINE_AA)

    for _ in range(outro_duration_frames):
        out.write(outro_frame)
    logging.info("Outro-Clip hinzugefügt.")

    out.release() # VideoWriter schließen
    logging.info(f"Temporäres Video ohne Audio erstellt: {temp_video_filepath}")

    # --- Hintergrundmusik hinzufügen mit FFmpeg ---
    try:
        if not os.path.exists(background_music_path):
            raise FileNotFoundError(f"Hintergrundmusikdatei nicht gefunden: {background_music_path}")

        logging.info(f"Füge Hintergrundmusik '{os.path.basename(background_music_path)}' hinzu...")

        # FFmpeg-Befehl zum Kombinieren von Video und Audio
        # -i für Eingabedateien, -map um Spuren auszuwählen, -c:v Videocodec, -c:a Audiocodec, -shortest kürzere Dauer
        # -y überschreibt Ausgabedatei, falls vorhanden
        ffmpeg_command = [
            'ffmpeg',
            '-i', temp_video_filepath,
            '-i', background_music_path,
            '-map', '0:v:0', # Video-Stream von erster Eingabe
            '-map', '1:a:0', # Audio-Stream von zweiter Eingabe
            '-c:v', 'copy',  # Video nicht rekodieren (schneller, keine Qualitätsverlust)
            '-c:a', 'aac',   # Audio zu AAC kodieren
            '-b:a', '192k',  # Audio-Bitrate
            '-shortest',     # Beendet das Video, wenn die kürzere Spur endet
            '-y',            # Überschreibt Ausgabedatei ohne Nachfrage
            output_filepath
        ]
        
        # subprocess.run wird den Befehl ausführen und auf dessen Beendigung warten
        # capture_output=True, text=True hilft beim Debugging
        result = subprocess.run(ffmpeg_command, capture_output=True, text=True, check=True)
        
        logging.info(f"FFmpeg stdout: {result.stdout}")
        if result.stderr:
            logging.info(f"FFmpeg stderr: {result.stderr}") # FFmpeg gibt viel Info nach stderr aus

        logging.info(f"Hintergrundmusik '{os.path.basename(background_music_path)}' erfolgreich hinzugefügt.")

    except FileNotFoundError:
        logging.error("Fehler: FFmpeg wurde nicht gefunden. Stellen Sie sicher, dass FFmpeg installiert und im System PATH ist.")
        logging.warning("Video wurde ohne Musik erstellt.")
    except subprocess.CalledProcessError as e:
        logging.error(f"FFmpeg-Fehler beim Hinzufügen der Musik: {e}")
        logging.error(f"FFmpeg stdout: {e.stdout}")
        logging.error(f"FFmpeg stderr: {e.stderr}")
        logging.warning("Video wurde ohne Musik erstellt.")
    except Exception as e:
        logging.warning(f"Konnte Hintergrundmusik nicht hinzufügen (anderer Fehler): {e}. Video wird ohne Musik erstellt.")

    #Temporäre Videodatei ohne Audio löschen
    if os.path.exists(temp_video_filepath):
        try:
            os.remove(temp_video_filepath)
            logging.info(f"Temporäre Datei gelöscht: {temp_video_filepath}")
        except Exception as e:
            logging.warning(f"Konnte temporäre Videodatei nicht löschen {temp_video_filepath}: {e}")

    logging.info(f"Video-Export abgeschlossen: {output_filepath}")