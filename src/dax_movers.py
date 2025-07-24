import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_dax_tickers():
    """
    Gibt eine Liste der aktuellen DAX 40 Ticker-Symbole zurück.
    Beachten Sie: Diese Liste muss manuell aktualisiert werden,
    wenn sich die Zusammensetzung des DAX ändert.
    """
    # Aktuelle DAX 40 Ticker-Symbole (Stand Mitte 2025)
    # Beachten Sie die ".DE" Endung für deutsche Börsenplätze bei Yahoo Finance
    dax_tickers = [
        "ADS.DE", "AIR.DE", "ALV.DE", "BAS.DE", "BAYN.DE", "BEI.DE", "BMW.DE", "BNR.DE",
        "CON.DE", "1COV.DE", "DB1.DE", "DBK.DE", "DTG.DE", "DTE.DE", "DPW.DE", "EOAN.DE",
        "ENR.DE", "FRE.DE", "FME.DE", "HEI.DE", "HEN3.DE", "IFX.DE", "JEN.DE", "LIN.DE",
        "LHA.DE", "MBG.DE", "MRK.DE", "MTX.DE", "MUV2.DE", "P911.DE", "PAH3.DE", "PUM.DE",
        "QIA.DE", "RHM.DE", "RWE.DE", "SAP.DE", "SIE.DE", "SRT3.DE", "SY1.DE", "VOW3.DE",
        "VNA.DE", "ZAL.DE"
    ]
    # Einige Ticker, die je nach Quelle variieren können, hier als Beispiel
    # Fügen Sie hier alle 40 hinzu, wenn die vollständige Liste verfügbar ist.
    # Für dieses Beispiel sind 35 Ticker enthalten.
    return dax_tickers

def get_dax_movers(num_movers=5):
    """
    Ermittelt die Top N Gewinner und Verlierer des DAX vom Vortag
    und ruft historische Daten für eine Monatsansicht ab.
    """
    dax_tickers = get_dax_tickers()

    today = datetime.now()
    # Der Vortag ist entscheidend, da die Daten nach Börsenschluss verfügbar sind
    # oder am nächsten Morgen abgerufen werden.
    yesterday = today - timedelta(days=1)
    # Stellen Sie sicher, dass 'yesterday' ein Handelstag war.
    # Für diesen einfachen Fall gehen wir davon aus, dass wir Daten für gestern erhalten.
    # Für robustere Lösungen müsste man Wochenenden/Feiertage prüfen.

    # Zeitraum für die Monatsansicht (ca. 30 Handelstage)
    # Wir holen etwas mehr, um sicherzustellen, dass wir 30 Handelstage haben
    start_date_month = today - timedelta(days=45) # 45 Tage für ca. 30 Handelstage
    end_date_month = today # Bis heute, damit der letzte Kurs der Vortag ist

    # Daten für alle DAX-Aktien abrufen
    # Nur 'Adj Close' und 'Volume' sind Standard, aber wir brauchen nur 'Adj Close'
    try:
        # Laden der Daten für den Vortag und für die Monatsansicht
        # Wir laden alle Daten einmal und filtern dann.
        # periods "1d" würde nur den letzten Tag holen, wir brauchen aber 2 Tage für die Berechnung
        # und zusätzlich 30 Tage für den Chart. Daher holen wir einen längeren Zeitraum
        # und wählen die benötigten Tage aus.
        data = yf.download(dax_tickers, start=start_date_month.strftime('%Y-%m-%d'),
                           end=end_date_month.strftime('%Y-%m-%d'))

        if data.empty:
            print("Fehler: Keine Daten für die angegebenen Ticker und den Zeitraum gefunden.")
            return None, None, None

        # Wir benötigen die 'Close' Spalte
        adj_close_data = data['Close']

        # Berechnung der prozentualen Veränderung des Vortages
        # Wir nehmen den vorletzten und letzten Handelstag aus den abgerufenen Daten
        # (da end_date_month = today, ist der letzte verfügbare Handelstag der Vortag)
        if len(adj_close_data) < 2:
            print("Nicht genügend Handelstage in den abgerufenen Daten für die Berechnung der Veränderung.")
            return None, None, None

        # Die letzten beiden Handelstage
        latest_trading_day = adj_close_data.index[-1]
        second_latest_trading_day = adj_close_data.index[-2]

        yesterday_prices = adj_close_data.loc[latest_trading_day]
        day_before_yesterday_prices = adj_close_data.loc[second_latest_trading_day]

        # Vermeidung von Division durch Null, falls ein Kurs 0 war
        percentage_changes = ((yesterday_prices - day_before_yesterday_prices) / day_before_yesterday_prices) * 100
        percentage_changes = percentage_changes.dropna() # Entferne Ticker ohne Daten

        # Sortieren für Top Gewinner und Verlierer
        top_gainers = percentage_changes.nlargest(num_movers)
        top_losers = percentage_changes.nsmallest(num_movers)

        # Historische Daten für die Monatsansicht für alle relevanten Mover
        # Wir sammeln die Ticker der Mover
        mover_tickers = top_gainers.index.tolist() + top_losers.index.tolist()
        mover_tickers = list(set(mover_tickers)) # Doppelte Ticker entfernen

        historical_data_for_charts = {}
        for ticker in mover_tickers:
            # Wir extrahieren die letzten 30 Handelstage (Adjusted Close)
            # Stellen Sie sicher, dass wir wirklich 30 Handelstage haben
            if ticker in adj_close_data.columns:
                # Wir nehmen die letzten 30 verfügbaren Handelstage
                historical_data_for_charts[ticker] = adj_close_data[ticker].tail(30)
            else:
                print(f"Warnung: Daten für {ticker} nicht in den Hauptdaten gefunden.")

        return top_gainers, top_losers, historical_data_for_charts

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None, None, None

# --- Ausführung des Skripts ---
if __name__ == "__main__":
    print("Starte die Ermittlung der DAX Top Mover...")
    top_gainers, top_losers, historical_chart_data = get_dax_movers(num_movers=5)

    if top_gainers is not None and top_losers is not None and historical_chart_data is not None:
        print("\n--- DAX Top 5 Gewinner vom Vortag ---")
        print(top_gainers.to_string()) # to_string() für bessere Formatierung bei Pandas Series

        print("\n--- DAX Top 5 Verlierer vom Vortag ---")
        print(top_losers.to_string())

        print("\n--- Historische Daten für Monatscharts der Mover ---")
        for ticker, data in historical_chart_data.items():
            print(f"\n{ticker} (letzte 30 Handelstage):")
            print(data.to_string())
    else:
        print("\nFehler bei der Ermittlung der Mover.")
