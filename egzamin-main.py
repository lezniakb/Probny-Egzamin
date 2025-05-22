import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
import os
import time
from datetime import datetime


# LICENCJA BEERWARE

class QuizApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # Stan aplikacji
        self.questions = []
        self.total_available_questions = 0
        self.current_question_index = 0
        self.current_question_data = None
        self.correct_indices = []
        self.points = 0.0
        self.total_questions_answered = 0
        self.question_answered = False
        self.current_question_vars = []
        self.checkboxes = []
        
        # Timer i statystyki
        self.exam_start_time = None
        self.question_start_time = None
        self.question_times = []
        self.timer_visible = False
        
        # Elementy GUI
        self.setup_gui()
        
        # Załaduj pytania i rozpocznij
        self.load_questions_and_start()
    
    def setup_window(self):
        """Konfiguracja okna głównego z proporcjami 2:3"""
        self.root.title("Egzamin Współbiegi 2025")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Oblicz wymiary okna w proporcji 2:3
        # Znajdź maksymalne wymiary zachowujące proporcje
        max_width = int(screen_width * 0.8)
        max_height = int(screen_height * 0.8)
        
        # Sprawdź które ograniczenie jest aktywne
        if max_width / 2 * 3 <= max_height:
            # Ogranicza szerokość
            window_width = max_width
            window_height = int(max_width / 2 * 3)
        else:
            # Ogranicza wysokość
            window_height = max_height
            window_width = int(max_height / 3 * 2)
        
        position_right = int((screen_width - window_width) / 2)
        position_down = int((screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
        self.root.config(bg="#101524")
        
        self.window_width = window_width
        self.window_height = window_height
    def setup_gui(self):
        """Tworzenie interfejsu użytkownika z fixed positioning"""
        self.main_frame = tk.Frame(self.root, bg="#101524")
        self.main_frame.pack(fill='both', expand=True)
        self.main_frame.pack_propagate(False)

        # Górne przyciski
        self.top_button_frame = tk.Frame(self.main_frame, bg='#101524', height=60)
        self.top_button_frame.pack(fill='x', padx=10, pady=5)
        self.top_button_frame.pack_propagate(False)

        self.preview_button = tk.Button(
            self.top_button_frame,
            text="Podgląd wszystkich pytań",
            command=self.show_all_questions,
            font=("Arial", 12),
            padx=15, pady=5,
            bg='#4a5568', fg='white',
            relief="raised", bd=2
        )
        self.preview_button.pack(side='left', padx=5, pady=10)

        self.finish_exam_button = tk.Button(
            self.top_button_frame,
            text="Zakończ Egzamin",
            command=self.finish_exam,
            font=("Arial", 12),
            padx=15, pady=5,
            bg='#dc2626', fg='white',
            relief="raised", bd=2
        )
        self.finish_exam_button.pack(side='left', padx=5, pady=10)

        self.new_exam_button = tk.Button(
            self.top_button_frame,
            text="Nowy Egzamin",
            command=self.start_new_exam,
            font=("Arial", 12),
            padx=15, pady=5,
            bg='#2d3748', fg='white',
            relief="raised", bd=2
        )
        self.new_exam_button.pack(side='left', padx=5, pady=10)

        self.timer_toggle_button = tk.Button(
            self.top_button_frame,
            text="Pokaż Timer",
            command=self.toggle_timer,
            font=("Arial", 12),
            padx=15, pady=5,
            bg='#4a5568', fg='white',
            relief="raised", bd=2
        )
        self.timer_toggle_button.pack(side='right', padx=5, pady=10)

        # Licznik pytań
        self.counter_frame = tk.Frame(self.main_frame, bg="#101524", height=40)
        self.counter_frame.pack(fill='x', padx=10)
        self.counter_frame.pack_propagate(False)

        self.question_counter_label = tk.Label(
            self.counter_frame,
            text="",
            font=("Arial", 14),
            fg='white',
            bg="#101524"
        )
        self.question_counter_label.pack(pady=5)

        # Pytanie
        self.question_frame = tk.Frame(self.main_frame, bg="#101524", height=100)
        self.question_frame.pack(fill='x', padx=10, pady=5)
        self.question_frame.pack_propagate(False)

        self.question_label = tk.Label(
            self.question_frame,
            text="",
            font=("Arial", 18),
            wraplength=self.window_width - 60,
            justify="left",
            bg="#101524",
            fg='white',
            anchor="nw"
        )
        self.question_label.pack(fill='both', expand=True, padx=10)

        # Odpowiedzi
        self.answer_frame = tk.Frame(self.main_frame, bg="#101524")
        self.answer_frame.pack(fill='both', expand=False, padx=10, pady=5)


        # Przyciski Sprawdź / Następne — teraz zaraz pod odpowiedziami
        self.button_frame = tk.Frame(self.main_frame, bg='#101524', height=120)
        self.button_frame.pack(fill='x', padx=10, pady=5)
        self.button_frame.pack_propagate(False)

        self.check_button = tk.Button(
            self.button_frame,
            text="Sprawdź",
            command=self.check_answer,
            font=("Arial", 16),
            padx=25, pady=10,
            bg='#2b6cb0', fg='white',
            relief="raised", bd=4
        )

        self.next_button = tk.Button(
            self.button_frame,
            text="Następne",
            command=self.skip_question,
            font=("Arial", 16),
            padx=25, pady=10,
            bg='#6b7280', fg='white',
            relief="raised", bd=4
        )

        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, minsize=10)
        self.button_frame.columnconfigure(2, weight=1)

        self.check_button.grid(row=0, column=0, padx=0, pady=0, sticky='e')
        self.next_button.grid(row=0, column=2, padx=0, pady=0, sticky='w')

        # Wyniki — teraz poniżej przycisków
        self.results_frame = tk.Frame(self.main_frame, bg="#101524", height=100)
        self.results_frame.pack(fill='x', padx=10, pady=5)
        self.results_frame.pack_propagate(False)

        self.score_counter_label = tk.Label(
            self.results_frame,
            text="",
            font=("Arial", 16),
            fg='black',
            bg='#ff9a00',
            relief="solid",
            bd=2,
            padx=10,
            pady=5
        )
        self.score_counter_label.pack(pady=2)

        self.score_label = tk.Label(
            self.results_frame,
            text="",
            font=("Arial", 18),
            fg='white',
            bg="#101524"
        )
        self.score_label.pack(pady=2)

        # Poprawne odpowiedzi — widoczne po sprawdzeniu
        self.bottom_correct_answers_frame = tk.Frame(self.main_frame, bg="#101524", height=150)

        self.bottom_correct_answers_inner_frame = tk.Frame(
            self.bottom_correct_answers_frame,
            bg="#ff9a00",
            relief="solid",
            bd=2
        )
        self.bottom_correct_answers_inner_frame.pack(expand=True, fill='both', padx=20, pady=10)

        self.bottom_correct_answers_label = tk.Label(
            self.bottom_correct_answers_inner_frame,
            text="",
            font=("Arial", 14, "bold"),
            justify="left",
            anchor="nw",
            bg="#ff9a00",
            fg="black",
            wraplength=int(self.window_width * 0.8)
        )
        self.bottom_correct_answers_label.pack(fill='both', expand=True, padx=15, pady=10)

        # Timer — ukryty, pokazuje się tylko po kliknięciu
        self.timer_frame = tk.Frame(self.main_frame, bg="#101524", height=40)

        self.timer_label = tk.Label(
            self.timer_frame,
            text="",
            font=("Arial", 14),
            fg='white',
            bg='#2d3748',
            relief="solid",
            bd=2,
            padx=10,
            pady=5
        )
        self.timer_label.pack(pady=5)


    def create_sample_questions_file(self):
        """Tworzy przykładowy plik pytań"""
        sample_content = """Jakie są podstawowe właściwości współbieżności?;1Współdzielenie zasobów;1Synchronizacja;0Sekwencyjność;1Równoległość
Co to jest deadlock?;1Zakleszczenie procesów;0Przyśpieszenie wykonania;0Brak synchronizacji;1Cykliczne oczekiwanie na zasoby
Które mechanizmy służą do synchronizacji?;1Mutex;1Semafor;0Buffer;1Monitor;0Thread
Co charakteryzuje model Actor?;1Przekazywanie komunikatów;0Współdzielenie pamięci;1Izolacja stanów;1Asynchroniczność
Jakie są rodzaje schedulingu?;1Preemptive;1Non-preemptive;0Sequential;1Round-robin;0Linear
Co to jest race condition?;1Nieokreślony wynik operacji;1Zależność od kolejności wykonania;0Optymalizacja kodu;0Przyspieszenie programu"""
        
        with open("pytania.txt", "w", encoding='utf-8') as file:
            file.write(sample_content)
    
    def load_questions(self, filename):
        """Ładuje pytania z pliku"""
        if not os.path.exists(filename):
            self.create_sample_questions_file()
            messagebox.showinfo(
                "Utworzono plik pytań", 
                f"Plik '{filename}' nie istniał, więc został utworzony z przykładowymi pytaniami. "
                "Możesz go edytować dodając własne pytania w formacie:\n"
                "Pytanie;1Poprawna odpowiedź;0Błędna odpowiedź;1Kolejna poprawna\n\n"
                "Gdzie '1' oznacza odpowiedź poprawną, a '0' błędną."
            )
        
        questions = []
        try:
            with open(filename, "r", encoding='utf-8') as file:
                lines = [line.strip() for line in file if line.strip()]
                for line_num, line in enumerate(lines, 1):
                    try:
                        parts = line.split(';')
                        if len(parts) >= 2:
                            question = parts[0].strip()
                            answers = parts[1:]
                            correct_indices = []
                            clean_answers = []
                            
                            for i, ans in enumerate(answers):
                                ans = ans.strip()
                                if ans.startswith('1'):
                                    correct_indices.append(i)
                                    clean_answers.append(ans[1:].strip())
                                elif ans.startswith('0'):
                                    clean_answers.append(ans[1:].strip())
                                else:
                                    clean_answers.append(ans)
                            
                            if question and clean_answers:
                                questions.append((question, clean_answers, correct_indices))
                    except Exception as e:
                        print(f"Błąd w linii {line_num}: {e}")
                        continue
                        
        except Exception as e:
            messagebox.showerror("Błąd", f"Nie można załadować pytań: {e}")
            return []
        
        return questions
    
    def load_questions_and_start(self):
        """Ładuje pytania i rozpoczyna quiz"""
        self.questions = self.load_questions("pytania.txt")
        if not self.questions:
            messagebox.showerror("Błąd", "Brak pytań do załadowania!")
            return
        
        self.total_available_questions = len(self.questions)
        random.shuffle(self.questions)
        self.update_score_display()
        self.load_random_question()
    
    def start_new_exam(self):
        """Rozpoczyna nowy egzamin"""
        if messagebox.askyesno("Nowy egzamin", "Czy na pewno chcesz rozpocząć nowy egzamin? Obecny postęp zostanie utracony."):
            self.reset_quiz()
            self.load_questions_and_start()
    
    def reset_quiz(self):
        """Resetuje stan quizu"""
        self.current_question_index = 0
        self.points = 0.0
        self.total_questions_answered = 0
        self.question_answered = False
        self.exam_start_time = None
        self.question_start_time = None
        self.question_times = []
        
        # Wyczyść checkboxy
        for chk in self.checkboxes:
            chk.destroy()
        self.checkboxes.clear()
        self.current_question_vars.clear()
        
        # Resetuj labele
        self.score_label.config(text="")
        self.bottom_correct_answers_label.config(text="")
        self.question_counter_label.config(text="")
        
        # Ukryj box z poprawnymi odpowiedziami
        self.bottom_correct_answers_frame.pack_forget()
        
        # Resetuj przyciski
        self.check_button.config(state='normal')
        self.next_button.config(state='normal')
    
    def load_random_question(self):
        """Ładuje następne pytanie"""
        self.question_answered = False
        
        # Zapisz czas poprzedniego pytania
        if self.question_start_time:
            question_time = time.time() - self.question_start_time
            self.question_times.append(question_time)
        
        # Rozpocznij timer egzaminu przy pierwszym pytaniu
        if self.exam_start_time is None:
            self.exam_start_time = time.time()
        
        # Rozpocznij timer dla tego pytania
        self.question_start_time = time.time()
        
        # Wyczyść poprzednie dane
        self.score_label.config(text="")
        self.bottom_correct_answers_label.config(text="")
        
        # Ukryj box z poprawnymi odpowiedziami
        self.bottom_correct_answers_frame.pack_forget()
        
        # Usuń poprzednie checkboxy
        for chk in self.checkboxes:
            chk.destroy()
        self.checkboxes.clear()
        self.current_question_vars.clear()
        
        # Sprawdź czy są jeszcze pytania
        if self.current_question_index >= len(self.questions):
            self.finish_exam()
            return
        
        # Pobierz następne pytanie
        self.current_question_data = self.questions[self.current_question_index]
        question_text, answers_list, correct_indices = self.current_question_data
        
        # Aktualizuj wyświetlanie
        self.question_label.config(text=f"{question_text}")
        self.question_counter_label.config(
            text=f"Pytanie {self.current_question_index + 1} z {self.total_available_questions}"
        )
        
        # Pomieszaj odpowiedzi
        combined = list(zip(answers_list, range(len(answers_list))))
        random.shuffle(combined)
        shuffled_answers, original_indices = zip(*combined)
        
        # Zaktualizuj indeksy poprawnych odpowiedzi
        self.correct_indices = [original_indices.index(i) for i in correct_indices if i in original_indices]
        
        # Utwórz checkboxy
        for idx, answer_text in enumerate(shuffled_answers):
            var = tk.IntVar()
            chk = tk.Checkbutton(
                self.answer_frame,
                text=answer_text,
                variable=var,
                font=("Arial", 14),
                anchor="w",
                justify="left",
                padx=15,
                pady=8,
                bg='white',
                fg='black',
                selectcolor='lightgray',
                borderwidth=2,
                relief="solid",
                wraplength=self.window_width - 100
            )
            chk.pack(fill='x', padx=20, pady=3)
            self.current_question_vars.append(var)
            self.checkboxes.append(chk)
        
        # Resetuj przyciski
        self.check_button.config(state='normal')
        self.next_button.config(state='normal')
        
        self.current_question_index += 1
    
    def check_answer(self):
        """Sprawdza odpowiedź użytkownika"""
        if self.question_answered:
            return
        
        self.question_answered = True
        
        # Pobierz wybory użytkownika
        user_selection = [var.get() for var in self.current_question_vars]
        selected_indices = [i for i, val in enumerate(user_selection) if val == 1]
        
        # Podświetl odpowiedzi
        for idx, chk in enumerate(self.checkboxes):
            if idx in selected_indices and idx in self.correct_indices:
                chk.config(bg="#4ade80", fg="black", borderwidth=3)  # Poprawnie wybrane
            elif idx in selected_indices and idx not in self.correct_indices:
                chk.config(bg="#f87171", fg="black", borderwidth=3)  # Błędnie wybrane
            elif idx in self.correct_indices:
                chk.config(bg="#84cc16", fg="black", borderwidth=3) 
            else:
                chk.config(bg="#e5e7eb", fg="black")  # Neutralne
        
        # Oblicz punkty
        question_score = self.calculate_score(selected_indices, self.correct_indices)
        self.points += question_score
        self.total_questions_answered += 1
        
        # Aktualizuj wyświetlanie
        self.update_score_display()
        self.score_label.config(text=f"Punkty za to pytanie: {question_score:.2f}")
        
        
        # Zmień stan przycisków
        self.check_button.config(state='disabled')
        if self.current_question_index >= len(self.questions):
            # To było ostatnie pytanie - zmień przycisk na "Zakończ egzamin"
            self.next_button.config(text="Przejdź do wyników", command=self.finish_exam, bg='#dc2626')
    def calculate_score(self, selected, correct):
        """Uproszczona funkcja obliczania punktów"""
        if not correct:  # Brak poprawnych odpowiedzi
            return 0.0 if not selected else -0.5
        
        if not selected:  # Nie wybrano żadnej odpowiedzi
            return 0.0
        
        correct_selected = len(set(selected) & set(correct))
        wrong_selected = len(selected) - correct_selected
        total_correct = len(correct)
        
        # Podstawowy wynik: % poprawnie wybranych
        base_score = correct_selected / total_correct
        
        # Kara za błędne wybory
        penalty = wrong_selected * 0.25
        
        # Końcowy wynik
        final_score = base_score - penalty
        
        # Ogranicz do zakresu [-1.0, 1.0]
        return max(min(final_score, 1.0), -1.0)
    
    def skip_question(self):
        """Pomija pytanie zapisując 0 punktów"""
        if self.question_answered:
            # Jeśli pytanie już sprawdzone, przejdź do następnego
            self.next_question()
            return
        
        # Zapisz 0 punktów za pominięte pytanie
        self.points += 0.0
        self.total_questions_answered += 1
        
        # Aktualizuj wyświetlanie
        self.update_score_display()
        self.score_label.config(text="Pytanie pominięte: 0.00 punktów")
        
        # Przejdź do następnego pytania
        self.next_question()
    
    def next_question(self):
        """Przechodzi do następnego pytania"""
        # Resetuj przycisk na wypadek gdyby był zmieniony
        self.next_button.config(text="Następne", command=self.skip_question, bg='#6b7280')
        self.load_random_question()
    
    def finish_exam(self):
        """Kończy egzamin i zapisuje wyniki"""
        # Zapisz czas ostatniego pytania
        if self.question_start_time:
            question_time = time.time() - self.question_start_time
            self.question_times.append(question_time)
        
        # Oblicz całkowity czas egzaminu
        total_exam_time = time.time() - self.exam_start_time if self.exam_start_time else 0
        
        # Znajdź pytanie z najdłuższym czasem
        longest_question_index = 0
        longest_time = 0
        if self.question_times:
            longest_time = max(self.question_times)
            longest_question_index = self.question_times.index(longest_time) + 1
        
        # Formatuj czas
        hours = int(total_exam_time // 3600)
        minutes = int((total_exam_time % 3600) // 60)
        seconds = int(total_exam_time % 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        # Zapisz wyniki do pliku
        self.save_results_to_file(total_exam_time, time_str, longest_question_index, longest_time)
        
        # Pokaż wynik końcowy
        result_message = (
            f"Wynik końcowy: {self.points:.2f}/{self.total_available_questions}\n"
            f"Procent: {(self.points/self.total_available_questions)*100:.1f}%\n"
            f"Czas egzaminu: {time_str}\n"
            f"Najdłużej nad pytaniem {longest_question_index}: {longest_time:.1f}s"
        )
        
        messagebox.showinfo("Koniec egzaminu", result_message)
        
        # Zresetuj przycisk następne
        self.next_button.config(text="Następne", command=self.skip_question, bg='#6b7280')
    
    def save_results_to_file(self, total_time, time_str, longest_question_num, longest_time):
        """Zapisuje wyniki do pliku"""
        try:
            with open("wyniki_log.txt", "a", encoding='utf-8') as file:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file.write(f"\n--- Egzamin z {timestamp} ---\n")
                file.write(f"Wynik: {self.points:.2f}/{self.total_available_questions}\n")
                file.write(f"Procent: {(self.points/self.total_available_questions)*100:.1f}%\n")
                file.write(f"Czas egzaminu: {time_str}\n")
                file.write(f"Najdłużej nad pytaniem {longest_question_num}: {longest_time:.1f}s\n")
                file.write("-" * 40 + "\n")
        except Exception as e:
            print(f"Błąd zapisu wyników: {e}")
    
    def update_score_display(self):
        """Aktualizuje wyświetlanie wyniku"""
        self.score_counter_label.config(
            text=f"Wynik: {self.points:.2f}/{self.total_available_questions} | "
                 f"Pytanie: {self.total_questions_answered}/{self.total_available_questions}"
        )
    
    def show_all_questions(self):
        """Pokazuje podgląd wszystkich pytań"""
        if not self.questions:
            messagebox.showwarning("Brak pytań", "Nie załadowano jeszcze pytań!")
            return
        
        # Utwórz nowe okno
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Podgląd wszystkich pytań")
        preview_window.geometry("800x600")
        preview_window.config(bg="#101524")
        
        # Dodaj scrollowany tekst
        text_widget = scrolledtext.ScrolledText(
            preview_window,
            wrap=tk.WORD,
            font=("Arial", 11),
            bg="white",
            fg="black"
        )
        text_widget.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Wypełnij pytaniami
        for i, (question, answers, correct_indices) in enumerate(self.questions, 1):
            text_widget.insert(tk.END, f"{i}. {question}\n")
            for j, answer in enumerate(answers):
                marker = "✓" if j in correct_indices else "×"
                text_widget.insert(tk.END, f"   {marker} {answer}\n")
            text_widget.insert(tk.END, "\n")
        
        text_widget.config(state='disabled')  # Tylko do odczytu
    
    def toggle_timer(self):
        """Przełącza widoczność timera"""
        if self.timer_visible:
            self.timer_frame.pack_forget()
            self.timer_toggle_button.config(text="Pokaż Timer")
            self.timer_visible = False
        else:
            self.timer_frame.pack(side='bottom', fill='x', padx=10)
            self.timer_frame.pack_propagate(False)
            self.timer_toggle_button.config(text="Ukryj Timer")
            self.timer_visible = True
            self.update_timer()
    
    def update_timer(self):
        """Aktualizuje timer"""
        if self.timer_visible and self.exam_start_time:
            elapsed = time.time() - self.exam_start_time
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"Czas: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        # Zaplanuj następną aktualizację
        if self.timer_visible:
            self.root.after(1000, self.update_timer)
    
    def run(self):
        """Uruchamia aplikację"""
        self.root.mainloop()


# Główna część programu
if __name__ == "__main__":
    app = QuizApp()
    app.run()
