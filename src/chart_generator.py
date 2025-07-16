import matplotlib.pyplot as plt
import pandas as pd
import os

def create_30_day_chart(ticker: str, historical_data: pd.Series, percentage_change: float, output_dir: str = "charts"):
    """
    Erstellt einen 30-Tages-Liniendiagramm der Aktie und speichert ihn als Bild.

    Args:
        ticker (str): Das Ticker-Symbol der Aktie (z.B. "BAS.DE").
        historical_data (pd.Series): Eine Pandas Series mit den historischen 'Adj Close' Preisen
                                     für die letzten 30 Handelstage. Der Index sollte Datumsangaben sein.
        percentage_change (float): Die prozentuale Veränderung des Vortages für diese Aktie.
        output_dir (str): Das Verzeichnis, in dem die Charts gespeichert werden sollen.
    """
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)

    # DataFrame für Matplotlib vorbereiten (optional, Series geht auch direkt)
    df = historical_data.copy()
    df.index = pd.to_datetime(df.index) # Sicherstellen, dass der Index Datumszeit-Objekte sind

    # Farbgebung basierend auf der prozentualen Veränderung
    if percentage_change > 0:
        line_color = 'green'
        change_text = f"+{percentage_change:.2f}%"
    elif percentage_change < 0:
        line_color = 'red'
        change_text = f"{percentage_change:.2f}%"
    else:
        line_color = 'blue'
        change_text = f"{percentage_change:.2f}%"

    # Diagramm erstellen
    fig, ax = plt.subplots(figsize=(1080/100, 1920/100), dpi=100) # TikTok Hochformat (1080x1920 Pixel)

    ax.plot(df.index, df.values, color=line_color, linewidth=2)

    # Titel anpassen: Aktie, Veränderung und Zeitraum
    ax.set_title(f"{ticker}: {change_text} (letzte 30 Handelstage)", fontsize=16, color='black', weight='bold')

    # Achsenbeschriftungen und Gitter
    ax.set_xlabel("Datum", fontsize=12)
    ax.set_ylabel("Kurs (EUR)", fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)

    # Datumsformatierung auf der X-Achse
    # plt.xticks(rotation=45, ha='right')
    # Vereinfachte Achsenbeschriftung für bessere Lesbarkeit auf TikTok
    num_ticks = 5
    tick_indices = [int(i) for i in range(0, len(df), len(df) // num_ticks)][:num_ticks]
    tick_indices.append(len(df) - 1) # Immer den letzten Tag anzeigen
    unique_tick_indices = sorted(list(set(tick_indices)))

    ax.set_xticks([df.index[i] for i in unique_tick_indices])
    ax.set_xticklabels([df.index[i].strftime('%d.%m.') for i in unique_tick_indices], rotation=45, ha='right', fontsize=10)

    # Y-Achsen-Limits anpassen, um den Verlauf besser darzustellen
    ax.autoscale_view()
    # Etwas Puffer über und unter den Daten hinzufügen
    y_min, y_max = df.min(), df.max()
    padding = (y_max - y_min) * 0.1
    ax.set_ylim(y_min - padding, y_max + padding)


    # Layout anpassen, um Beschriftungen nicht zu überlappen
    plt.tight_layout()

    # Dateinamen für das Bild
    # Ersetze ungültige Zeichen im Ticker für Dateinamen
    safe_ticker = ticker.replace(".DE", "").replace(".DEX", "").replace("^", "")
    filename = os.path.join(output_dir, f"{safe_ticker}_30_day_chart.png")

    # Diagramm speichern
    plt.savefig(filename)
    plt.close(fig) # Schließt die Abbildung, um Speicher freizugeben

    print(f"Chart für {ticker} gespeichert unter: {filename}")
    return filename

# --- Beispielhafte Nutzung (wenn dieses Modul direkt ausgeführt wird) ---
if __name__ == "__main__":
    # Dies ist ein Beispiel, um die Funktion zu testen.
    # Im echten Szenario würden Sie `dax_movers.py` ausführen und die Daten hierher übergeben.

    # Erzeuge fiktive historische Daten (letzte 30 Tage)
    today = datetime.now()
    dates = [today - timedelta(days=i) for i in reversed(range(30))]
    # Simuliere einen positiven Verlauf
    positive_data = pd.Series([100 + i * 2 + (i % 5) * 3 for i in range(30)], index=dates)
    # Simuliere einen negativen Verlauf
    negative_data = pd.Series([150 - i * 3 - (i % 4) * 2 for i in range(30)], index=dates)
    # Simuliere einen neutralen Verlauf
    neutral_data = pd.Series([75 + (i % 3) for i in range(30)], index=dates)

    # Test für einen Gewinner
    print("\nTeste Chart-Erstellung für einen Gewinner...")
    create_30_day_chart("WINNER.DE", positive_data, 2.55)

    # Test für einen Verlierer
    print("\nTeste Chart-Erstellung für einen Verlierer...")
    create_30_day_chart("LOSER.DE", negative_data, -1.87)

    # Test für neutralen Wert
    print("\nTeste Chart-Erstellung für neutralen Wert...")
    create_30_day_chart("NEUTRAL.DE", neutral_data, 0.00)

    print("\nBeispiel-Charts erstellt (wenn keine Fehler aufgetreten sind).")
