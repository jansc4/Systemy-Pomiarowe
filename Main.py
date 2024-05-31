import time
import gpiod
import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Inicjalizacja GPIO
trig_pin = 17
echo_pin = 24
global  running 
running = False
min_distance_entry_val_def = 10
max_distance_entry_val_def = 100


global min_distance_entry_val 
min_distance_entry_val =  min_distance_entry_val_def
global max_distance_entry_val 
max_distance_entry_val = max_distance_entry_val_def


chip = gpiod.Chip('gpiochip4')  # Zaktualizuj numer chipu, jeśli potrzebne
trig_line = chip.get_line(trig_pin)
echo_line = chip.get_line(echo_pin)

# Konfiguracja pinów
trig_line.request(consumer="trigger", type=gpiod.LINE_REQ_DIR_OUT)
echo_line.request(consumer="echo", type=gpiod.LINE_REQ_DIR_IN)

# Funkcja do pomiaru odległości
def measure_distance():
    # Wysłanie sygnału
    trig_line.set_value(0)
    time.sleep(0.3)  # Czas na stabilizację

    trig_line.set_value(1)
    time.sleep(0.00001)
    trig_line.set_value(0)

    # Odczyt czasu trwania sygnału ECHO
    start_time = time.time()
    end_time = time.time()
    while echo_line.get_value() == 0:
        start_time = time.time()
    while echo_line.get_value() == 1:
        end_time = time.time()

    # Obliczenie czasu trwania sygnału ECHO w sekundach
    duration = end_time - start_time

    # Obliczenie odległości (prędkość dźwięku = 343 m/s)
    distance = (duration * 34300) / 2  # Dzielone przez 2, bo dźwięk podróżuje tam i z powrotem
    return distance

# Funkcja do rysowania wykresu na elemencie canvas Tkinter
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    return figure_canvas_agg

# Funkcja do aktualizacji interfejsu i wykresu
def update():
    if running:
        dist = measure_distance()
        data.append(dist)

        # Aktualizacja wykresu
        line.set_xdata(range(len(data)))
        line.set_ydata(data)
        ax.set_xlim(0, len(data))
        ax.set_ylim(0, max(data) + 10)
        fig_agg.draw()

        # Aktualizacja tekstu
        output_label.config(text=f"Odległość: {dist:.2f} cm")

        # Obliczenie statystyk
        max_dist = max(data)
        if any(x > 0 for x in data):
            min_dist = min(x for x in data if x > 0)
        else:
            min_dist = max(data)
        avg_dist = sum(data) / len(data)


        # Aktualizacja etykiet statystyk
        max_label.config(text=f"Największa odległość: {max_dist:.2f} cm")
        min_label.config(text=f"Najmniejsza odległość: {min_dist:.2f} cm")
        avg_label.config(text=f"Średnia odległość: {avg_dist:.2f} cm")

        # Sprawdzenie, czy odległość mieści się w zadanym zakresie
        if min_distance_entry_val <= dist <= max_distance_entry_val:
            in_range_label.config(text="Wynik mieści się w zakresie", fg="green")
        else:
            in_range_label.config(text="Wynik nie mieści się w zakresie", fg="red")

    root.after(500, update)  # Aktualizacja co pół sekundy
def on_entry_finished(event):
    try:
        global min_distance_entry_val 
        min_distance_entry_val = float(min_distance_entry.get())  # Pobierz wartość wprowadzoną przez użytkownika
        global max_distance_entry_val 
        max_distance_entry_val = float(max_distance_entry.get())
    except Exception as e:
        min_distance_entry_val = min_distance_entry_val_def
        max_distance_entry_val = max_distance_entry_val_def

# Funkcja uruchamiana po wciśnięciu przycisku "Start"
def start_measurement():
    global running
    running = True

# Funkcja uruchamiana po wciśnięciu przycisku "Stop"
def stop_measurement():
    global running
    running = False

# Tworzenie głównego okna
root = tk.Tk()
root.title("Pomiar odległości")

# Tworzenie widgetów interfejsu
output_label = tk.Label(root, text="Odległość: ", font=("Arial", 16))
output_label.pack(pady=10)

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack(side=tk.LEFT, padx=10)

# Ustawienia wykresu
fig = Figure(figsize=(5, 4), dpi=100)
ax = fig.add_subplot(111)
line, = ax.plot([], [])
ax.set_xlim(0, 100)
ax.set_ylim(0, 200)  # Zmień zakresy według swoich potrzeb

fig_agg = draw_figure(canvas, fig)

# Kolejka do przechowywania danych
data = deque([0] * 100, maxlen=100)

# Panel ustawień zakresu
settings_frame = tk.Frame(root)
settings_frame.pack(side=tk.LEFT, padx=10)

min_distance_label = tk.Label(settings_frame, text="Odległość minimalna:")
min_distance_label.grid(row=0, column=0)
min_distance_entry = tk.Entry(settings_frame)
min_distance_entry.insert(0, min_distance_entry_val_def)  # Wartość startowa równa 10
min_distance_entry.bind("<Return>", on_entry_finished)
min_distance_entry.grid(row=0, column=1)

max_distance_label = tk.Label(settings_frame, text="Odległość maksymalna:")
max_distance_label.grid(row=1, column=0)
max_distance_entry = tk.Entry(settings_frame)
max_distance_entry.insert(0, max_distance_entry_val_def)  # Wartość startowa równa 100
max_distance_entry.bind("<Return>", on_entry_finished)
max_distance_entry.grid(row=1, column=1)

# Etykiety statystyk
max_label = tk.Label(settings_frame, text="Największa odległość: ", font=("Arial", 10))
max_label.grid(row=2, columnspan=2, pady=5)

min_label = tk.Label(settings_frame, text="Najmniejsza odległość: ", font=("Arial", 10))
min_label.grid(row=3, columnspan=2, pady=5)

avg_label = tk.Label(settings_frame, text="Średnia odległość: ", font=("Arial", 10))
avg_label.grid(row=4, columnspan=2, pady=5)

# Etykieta sygnalizująca, czy wynik mieści się w zakresie
in_range_label = tk.Label(settings_frame, text="", font=("Arial", 10))
in_range_label.grid(row=5, columnspan=2, pady=5)
# Przycisk start i stop
start_button = tk.Button(settings_frame, text="Start", command=start_measurement)
start_button.grid(row=6, column=0, pady=5, padx=5)
stop_button = tk.Button(settings_frame, text="Stop", command=stop_measurement)
stop_button.grid(row=6, column=1, pady=5, padx=5)

# Uruchomienie funkcji aktualizacji
root.after(1000, update)

try:
    root.mainloop()
finally:
    trig_line.release()
    echo_line.release()
