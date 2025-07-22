# src/video_maker.py

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip # type: ignore
from moviepy.config import change_settings # Nötig, um ImageMagick Pfad zu setzen
import os
import logging
from datetime import datetime

# --- Konfiguration für MoviePy und ImageMagick ---
# Stellen Sie sicher, dass ImageMagick installiert ist
# und der Pfad hier korrekt gesetzt ist, falls er nicht in Ihrem System PATH liegt.
# Beispiel (Windows): change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})
# Beispiel (Linux/macOS): change_settings({"IMAGEMAGICK_BINARY": "/opt/ImageMagick/bin/magick"})
# Wenn ImageMagick im System PATH ist, ist diese Zeile oft nicht nötig.
# Prüfen Sie Ihre ImageMagick Installation mit 'magick -version' im Terminal.
try:
    # Versucht, ImageMagick zu finden. Wenn nicht gefunden, kann ein Fehler auftreten.
    # remove this line if you have issues with ImageMagick and set the path explicitly above
    # Or install ImageMagick and ensure it's in your system's PATH
    pass
except Exception as e:
    logging.warning(f"ImageMagick Konfiguration fehlgeschlagen: {e}. Versuche ohne explizite Pfadangabe.")


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

    Args:
        chart_image_paths (list): Liste der Dateipfade zu den generierten Chart-Bildern.
        output_filepath (str): Der vollständige Pfad und Dateiname für das Ausgabevideo (.mp4).
        background_music_path (str): Der Pfad zur Hintergrundmusik-Datei.
        chart_display_duration (int): Wie lange jeder Chart im Video angezeigt werden soll (in Sekunden).
        movers_info (dict): Informationen über die Mover zur Anzeige der prozentualen Veränderung.
    """
    logging.info(f"Starte Videogenerierung. Anzahl Charts: {len(chart_image_paths)}")

    # Video-Dimensionen für TikTok (Hochformat)
    VIDEO_WIDTH = 1080
    VIDEO_HEIGHT = 1920

    final_clips = []
    current_time = 0 # Um die Startzeit für Text-Clips zu verfolgen

    # --- Intro-Clip ---
    intro_text = f"DAX Top Mover vom {datetime.now().strftime('%d.%m.%Y')}"
    intro_clip = TextClip(intro_text, fontsize=80, color='white', bg_color='black',
                          size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    intro_clip = intro_clip.set_duration(3).set_position('center') # 3 Sekunden Intro
    final_clips.append(intro_clip)
    current_time += 3

    # --- Chart-Clips ---
    for i, chart_path in enumerate(chart_image_paths):
        # Bild-Clip erstellen
        chart_clip = ImageClip(chart_path, duration=chart_display_duration)
        chart_clip = chart_clip.resize(newsize=(VIDEO_WIDTH, VIDEO_HEIGHT)) # Sicherstellen, dass es die volle Größe ausfüllt

        # Ticker aus Dateipfad extrahieren (z.B. "BAS_30_day_chart.png" -> "BAS")
        base_name = os.path.basename(chart_path)
        ticker_name = base_name.split('_')[0]

        # Informationen für den Text-Overlay abrufen
        percentage_change = movers_info.get(ticker_name, {}).get('change', 0.0)
        display_text_change = f"{percentage_change:.2f}%"
        text_color = 'green' if percentage_change >= 0 else 'red'

        # Text-Overlay für Aktie und prozentuale Veränderung
        ticker_text_clip = TextClip(ticker_name, fontsize=100, color='white', font='Arial-Bold',
                                    stroke_color='black', stroke_width=2)
        ticker_text_clip = ticker_text_clip.set_position(("center", VIDEO_HEIGHT * 0.1)).set_duration(chart_display_duration)

        change_text_clip = TextClip(display_text_change, fontsize=80, color=text_color, font='Arial-Bold',
                                    stroke_color='black', stroke_width=2)
        change_text_clip = change_text_clip.set_position(("center", VIDEO_HEIGHT * 0.25)).set_duration(chart_display_duration)

        # Kombiniere Chart-Clip mit Text-Overlays
        composite_chart_clip = CompositeVideoClip([
            chart_clip,
            ticker_text_clip,
            change_text_clip
        ], size=(VIDEO_WIDTH, VIDEO_HEIGHT))

        final_clips.append(composite_chart_clip)
        current_time += chart_display_duration

    # --- Outro-Clip ---
    outro_text = "Tägliche DAX-Updates! Folge uns!"
    outro_clip = TextClip(outro_text, fontsize=70, color='white', bg_color='black',
                         size=(VIDEO_WIDTH, VIDEO_HEIGHT))
    outro_clip = outro_clip.set_duration(3).set_position('center') # 3 Sekunden Outro
    final_clips.append(outro_clip)
    current_time += 3

    # Kombiniere alle Clips
    final_video = concatenate_videoclips(final_clips)

    # Hintergrundmusik hinzufügen
    try:
        audio_clip = AudioFileClip(background_music_path)
        # Die Musik muss auf die Länge des Videos zugeschnitten oder geloopt werden
        if audio_clip.duration < final_video.duration:
            # Loop-Musik, wenn kürzer als Video
            audio_clip = audio_clip.loop(duration=final_video.duration)
        else:
            # Schneide Musik, wenn länger als Video
            audio_clip = audio_clip.subclip(0, final_video.duration)

        final_video = final_video.set_audio(audio_clip)
        logging.info(f"Hintergrundmusik '{os.path.basename(background_music_path)}' hinzugefügt.")
    except Exception as e:
        logging.warning(f"Konnte Hintergrundmusik nicht hinzufügen: {e}. Video wird ohne Musik erstellt.")

    # Video exportieren
    logging.info(f"Exportiere Video nach: {output_filepath}")
    final_video.write_videofile(output_filepath, fps=24, codec="libx264", audio_codec="aac")
    logging.info("Video-Export abgeschlossen.")
