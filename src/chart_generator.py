from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime, timedelta

# Zuordnung Ticker → Unternehmensname (DAX 40)
ticker_to_name = {
    "ADS.DE": "Adidas", "AIR.DE": "Airbus", "ALV.DE": "Allianz", "BAS.DE": "BASF",
    "BAYN.DE": "Bayer", "BEI.DE": "Beiersdorf", "BMW.DE": "BMW", "BNR.DE": "Brenntag",
    "CON.DE": "Continental", "1COV.DE": "Covestro", "DB1.DE": "Deutsche Börse",
    "DBK.DE": "Deutsche Bank", "DTG.DE": "Delivery Hero", "DTE.DE": "Deutsche Telekom",
    "DPW.DE": "Deutsche Post", "EOAN.DE": "E.ON", "ENR.DE": "Siemens Energy",
    "FRE.DE": "Fresenius", "FME.DE": "Fresenius Medical Care", "HEI.DE": "Heidelberg Materials",
    "HEN3.DE": "Henkel", "IFX.DE": "Infineon", "JEN.DE": "Jenoptik", "LIN.DE": "Linde",
    "LHA.DE": "Lufthansa", "MBG.DE": "Mercedes-Benz", "MRK.DE": "Merck", "MTX.DE": "MTU Aero Engines",
    "MUV2.DE": "Munich Re", "P911.DE": "Porsche AG", "PAH3.DE": "Porsche SE", "PUM.DE": "Puma",
    "QIA.DE": "Qiagen", "RHM.DE": "Rheinmetall", "RWE.DE": "RWE", "SAP.DE": "SAP",
    "SIE.DE": "Siemens", "SRT3.DE": "Sartorius", "SY1.DE": "Symrise", "VOW3.DE": "Volkswagen",
    "VNA.DE": "Vonovia", "ZAL.DE": "Zalando"
}

def create_30_day_chart(ticker: str, historical_data: pd.Series, percentage_change: float, output_dir: str = "charts"):
    os.makedirs(output_dir, exist_ok=True)
    df = historical_data.copy()
    df.index = pd.to_datetime(df.index)

    # Farbe basierend auf Kursverlauf
    if percentage_change > 0:
        line_color = 'limegreen'
        change_text = f"+{percentage_change:.2f}%"
    elif percentage_change < 0:
        line_color = 'red'
        change_text = f"{percentage_change:.2f}%"
    else:
        line_color = 'gray'
        change_text = f"{percentage_change:.2f}%"

    # Namen aus Mapping holen
    company_name = ticker_to_name.get(ticker, ticker)

    # Plot vorbereiten
    fig, ax = plt.subplots(figsize=(1080/100, 1920/100), dpi=100)
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.plot(df.index, df.values, color=line_color, linewidth=4)

    # Linksbündig oben: 1. Zeile → Unternehmensname + Ticker
    ax.text(0.01, 0.98, f"{company_name}  ({ticker})",
    transform=ax.transAxes,
    ha='left', va='top',
    fontsize=42, color=line_color, weight='bold')

    # Linksbündig darunter: 2. Zeile → prozentuale Veränderung
    ax.text(0.01, 0.925, f"{change_text}",
    transform=ax.transAxes,
    ha='left', va='top',
    fontsize=42, color=line_color, weight='bold')


     # Achsen & Labels
    ax.set_xlabel("Date", fontsize=14, color='white')
    ax.set_ylabel("Price (EUR)", fontsize=14, color='white')
    ax.tick_params(axis='x', colors='white', labelsize=12, width=2, length=6)  # Dickere Ticks
    ax.tick_params(axis='y', colors='white', labelsize=12, width=2, length=6)  # Dickere Ticks

    # Achsenlinien dicker machen
    ax.spines['bottom'].set_color('white')
    ax.spines['bottom'].set_linewidth(2.5)  # Dicke der unteren Achse
    ax.spines['left'].set_color('white')
    ax.spines['left'].set_linewidth(2.5)    # Dicke der linken Achse
    ax.spines['top'].set_color('black')     # Ausgeblendete obere Achse bleibt schwarz
    ax.spines['top'].set_linewidth(0)
    ax.spines['right'].set_color('black')   # Ausgeblendete rechte Achse bleibt schwarz
    ax.spines['right'].set_linewidth(0)

    ax.grid(True, linestyle='--', alpha=0.2, color='white')

    # X-Ticks reduzieren
    num_ticks = 5
    tick_indices = [int(i) for i in range(0, len(df), len(df) // num_ticks)][:num_ticks]
    tick_indices.append(len(df) - 1)
    unique_tick_indices = sorted(set(tick_indices))
    ax.set_xticks([df.index[i] for i in unique_tick_indices])
    ax.set_xticklabels([df.index[i].strftime('%d.%m.') for i in unique_tick_indices], rotation=45, ha='right')

    # Y-Achse mit Puffer
    y_min, y_max = df.min(), df.max()
    padding = (y_max - y_min) * 0.1
    ax.set_ylim(y_min - padding, y_max + padding)

    plt.tight_layout()
    safe_ticker = ticker.replace(".DE", "").replace(".DEX", "").replace("^", "")
    filename = os.path.join(output_dir, f"{safe_ticker}_30_day_chart.png")
    plt.savefig(filename, facecolor=fig.get_facecolor())
    plt.close(fig)

    print(f"Chart für {company_name} gespeichert unter: {filename}")
    return filename