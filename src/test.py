import matplotlib.pyplot as plt
import numpy as np

# Beispiel-Daten
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Diagramm erstellen
fig, ax = plt.subplots(figsize=(6, 12))  # Hochformat, ähnlich wie Handy

# Linie plotten
ax.plot(x, y, color='black', linewidth=1)

# Titel und Prozentwert
plt.title("\nAktienname (Kürzel)\nxx.x%", fontsize=14, ha='left', loc='left', pad=40)

# Design anpassen
ax.set_facecolor("white")
fig.patch.set_facecolor('white')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['left'].set_linewidth(0.5)
ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)

plt.tight_layout()
plt.show()
