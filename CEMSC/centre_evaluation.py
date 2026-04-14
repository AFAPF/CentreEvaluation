import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import json
import os
from datetime import datetime
import math
from collections import defaultdict, Counter

# ============================================================
# CLASSE PRINCIPALE : CENTRE D'ÉVALUATION
# ============================================================

class CentreEvaluation:
    def __init__(self):
        self.fenetre = tk.Tk()
        self.fenetre.title("🎮 CENTRE D'ÉVALUATION - Souris & Clavier")
        self.fenetre.geometry("1400x900")
        self.fenetre.configure(bg='#1a1a2e')
        self.fenetre.state('zoomed')
        self.fullscreen = False
        self.fenetre.bind('<F11>', self.toggle_fullscreen)

        self.colors = {
            'bg': '#1a1a2e',
            'secondary': '#16213e',
            'accent': '#0f3460',
            'highlight': '#e94560',
            'success': '#2ecc71',
            'warning': '#f1c40f',
            'text': '#ecf0f1',
            'gold': '#ffd700'
        }

        self.profils = {}
        self.profil_actuel = None
        self.charger_tous_profils()
        self.selectionner_profil()

        if not self.profil_actuel:
            self.fenetre.destroy()
            return

        self.charger_profil()
        self.charger_scores_globaux()
        self.charger_succes()
        self.init_badges()

        self.creer_interface()
        self.afficher_accueil()

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        self.fenetre.attributes('-fullscreen', self.fullscreen)
        if not self.fullscreen:
            self.fenetre.state('zoomed')

    def init_badges(self):
        self.badges_definitions = [
            {"id": "maitre_clic_gauche", "nom": "Maître du clic gauche", "description": "Réussir l'exercice Clic Gauche sans erreur", "xp": 100},
            {"id": "maitre_clic_droit", "nom": "Maître du clic droit", "description": "Réussir l'exercice Clic Droit sans erreur", "xp": 100},
            {"id": "maitre_double_clic", "nom": "Double Clic Pro", "description": "Réussir l'exercice Double Clic sans erreur", "xp": 150},
            {"id": "as_glisser_deposer", "nom": "As du Glisser-Déposer", "description": "Réussir l'exercice Glisser-Déposer sans erreur", "xp": 150},
            {"id": "speed_click_niveau5", "nom": "Speed Click Niveau 5", "description": "Atteindre le niveau 5 en Speed Click", "xp": 200},
            {"id": "keyboard_niveau10", "nom": "Maître du Clavier", "description": "Atteindre le niveau 10 en Keyboard Master", "xp": 300},
            {"id": "dactylo_50wpm", "nom": "Dactylo Rapide", "description": "Atteindre 50 WPM en Dactylo", "xp": 250},
            {"id": "combo_20", "nom": "Combo x20", "description": "Atteindre un combo de 20", "xp": 150},
        ]

    def selectionner_profil(self):
        if not self.profils:
            self.creer_profil("Joueur")
            self.profil_actuel = "Joueur"
            return

        dialog = tk.Toplevel(self.fenetre)
        dialog.title("👤 Sélection du profil")
        dialog.geometry("500x450")
        dialog.configure(bg=self.colors['secondary'])
        dialog.transient(self.fenetre)
        dialog.grab_set()

        tk.Label(dialog, text="CHOISISSEZ VOTRE PROFIL", font=('Arial', 18, 'bold'),
                bg=self.colors['secondary'], fg=self.colors['gold']).pack(pady=20)

        list_frame = tk.Frame(dialog, bg=self.colors['secondary'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.liste_profils = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                          bg=self.colors['bg'], fg=self.colors['text'],
                          font=('Arial', 14), height=8, selectbackground=self.colors['accent'])
        self.liste_profils.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.liste_profils.yview)

        for nom in sorted(self.profils.keys()):
            self.liste_profils.insert(tk.END, f"👤 {nom}")

        def choisir():
            selection = self.liste_profils.curselection()
            if selection:
                nom = self.liste_profils.get(selection[0]).replace("👤 ", "")
                self.profil_actuel = nom
                dialog.destroy()

        def nouveau():
            dialog2 = tk.Toplevel(dialog)
            dialog2.title("Nouveau profil")
            dialog2.geometry("300x150")
            dialog2.configure(bg=self.colors['secondary'])
            dialog2.transient(dialog)
            dialog2.grab_set()

            tk.Label(dialog2, text="Nom du profil:", font=('Arial', 12),
                    bg=self.colors['secondary'], fg=self.colors['text']).pack(pady=10)
            entry = tk.Entry(dialog2, font=('Arial', 14), width=20)
            entry.pack(pady=5)
            entry.focus()

            def creer():
                nom = entry.get().strip()
                if nom and nom not in self.profils:
                    self.creer_profil(nom)
                    dialog2.destroy()
                    dialog.destroy()
                    self.profil_actuel = nom
                else:
                    messagebox.showerror("Erreur", "Nom invalide ou déjà utilisé")

            tk.Button(dialog2, text="Créer", command=creer,
                     bg=self.colors['success'], fg='white', font=('Arial', 12),
                     padx=20, pady=5).pack(pady=10)
            entry.bind('<Return>', lambda e: creer())

        def supprimer():
            selection = self.liste_profils.curselection()
            if not selection:
                messagebox.showwarning("Suppression", "Veuillez sélectionner un profil.")
                return
            nom = self.liste_profils.get(selection[0]).replace("👤 ", "")
            if len(self.profils) <= 1:
                messagebox.showerror("Erreur", "Vous devez garder au moins un profil.")
                return
            if messagebox.askyesno("Confirmation", f"Supprimer définitivement le profil '{nom}' ?"):
                del self.profils[nom]
                self.sauvegarder_tous_profils()
                self.liste_profils.delete(selection[0])
                if self.profils:
                    self.liste_profils.selection_set(0)
                else:
                    self.creer_profil("Joueur")
                    self.liste_profils.insert(tk.END, "👤 Joueur")
                    self.liste_profils.selection_set(0)

        btn_frame = tk.Frame(dialog, bg=self.colors['secondary'])
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Choisir", command=choisir,
                 bg=self.colors['accent'], fg='white', font=('Arial', 12, 'bold'),
                 padx=20, pady=8).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Nouveau", command=nouveau,
                 bg=self.colors['success'], fg='white', font=('Arial', 12),
                 padx=20, pady=8).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Supprimer", command=supprimer,
                 bg=self.colors['highlight'], fg='white', font=('Arial', 12),
                 padx=20, pady=8).pack(side='left', padx=5)

        self.fenetre.wait_window(dialog)

    def creer_profil(self, nom):
        self.profils[nom] = {
            "niveau": 1,
            "xp": 0,
            "parties": 0,
            "succes": [],
            "badges": [],
            "stats_clavier": {"reussites": 0, "erreurs": 0, "touches": {}},
            "stats_souris": {"reussites": 0, "erreurs": 0},
            "date_creation": datetime.now().strftime("%d/%m/%Y")
        }
        self.sauvegarder_tous_profils()

    def charger_tous_profils(self):
        try:
            if os.path.exists("profils_evaluation.json"):
                with open("profils_evaluation.json", "r") as f:
                    self.profils = json.load(f)
        except:
            self.profils = {}

    def sauvegarder_tous_profils(self):
        try:
            with open("profils_evaluation.json", "w") as f:
                json.dump(self.profils, f, indent=2)
        except:
            pass

    def charger_profil(self):
        if self.profil_actuel in self.profils:
            p = self.profils[self.profil_actuel]
            self.niveau_global = p.get("niveau", 1)
            self.experience_totale = p.get("xp", 0)
            self.parties_jouees = p.get("parties", 0)
            self.succes_debloques = p.get("succes", [])
            self.badges_debloques = p.get("badges", [])
        else:
            self.niveau_global = 1
            self.experience_totale = 0
            self.parties_jouees = 0
            self.succes_debloques = []
            self.badges_debloques = []

    def sauvegarder_profil(self):
        if self.profil_actuel in self.profils:
            self.profils[self.profil_actuel].update({
                "niveau": self.niveau_global,
                "xp": self.experience_totale,
                "parties": self.parties_jouees,
                "succes": self.succes_debloques,
                "badges": self.badges_debloques
            })
            self.sauvegarder_tous_profils()

    def charger_scores_globaux(self):
        self.scores_globaux = []
        try:
            if os.path.exists("scores_globaux.json"):
                with open("scores_globaux.json", "r") as f:
                    self.scores_globaux = json.load(f)
        except:
            pass

    def sauvegarder_score(self, module, score, niveau, combo, details=None):
        try:
            self.scores_globaux.append({
                "module": module,
                "score": score,
                "niveau": niveau,
                "combo": combo,
                "joueur": self.profil_actuel,
                "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "details": details or {}
            })
            self.scores_globaux.sort(key=lambda x: x["score"], reverse=True)
            self.scores_globaux = self.scores_globaux[:50]
            with open("scores_globaux.json", "w") as f:
                json.dump(self.scores_globaux, f, indent=2)
        except:
            pass

    def charger_succes(self):
        self.liste_succes = [
            {"id": "premiere_partie", "nom": "Première partie", "description": "Terminer une partie", "xp": 50},
            {"id": "combo_10", "nom": "Combo x10", "description": "Atteindre un combo de 10", "xp": 100},
            {"id": "combo_25", "nom": "Combo x25", "description": "Atteindre un combo de 25", "xp": 250},
            {"id": "score_1000", "nom": "Score 1000", "description": "Dépasser 1000 points", "xp": 150},
            {"id": "score_5000", "nom": "Score 5000", "description": "Dépasser 5000 points", "xp": 500},
            {"id": "niveau_5", "nom": "Niveau 5", "description": "Atteindre le niveau global 5", "xp": 300},
            {"id": "tous_modules", "nom": "Explorateur", "description": "Jouer aux 4 modules", "xp": 200},
            {"id": "perfect_souris", "nom": "Souris Parfaite", "description": "10 clics réussis sans erreur", "xp": 150},
            {"id": "perfect_clavier", "nom": "Clavier Parfait", "description": "20 touches réussies sans erreur", "xp": 200},
        ]
        self.modules_joues = set()

    def verifier_succes(self, conditions):
        for s in self.liste_succes:
            if s["id"] in self.succes_debloques:
                continue
            if s["id"] == "premiere_partie" and conditions.get("partie_terminee"):
                self.debloquer_succes(s)
            elif s["id"] == "combo_10" and conditions.get("max_combo", 0) >= 10:
                self.debloquer_succes(s)
            elif s["id"] == "combo_25" and conditions.get("max_combo", 0) >= 25:
                self.debloquer_succes(s)
            elif s["id"] == "score_1000" and conditions.get("score", 0) >= 1000:
                self.debloquer_succes(s)
            elif s["id"] == "score_5000" and conditions.get("score", 0) >= 5000:
                self.debloquer_succes(s)
            elif s["id"] == "niveau_5" and self.niveau_global >= 5:
                self.debloquer_succes(s)
            elif s["id"] == "perfect_souris" and conditions.get("perfect_souris"):
                self.debloquer_succes(s)
            elif s["id"] == "perfect_clavier" and conditions.get("perfect_clavier"):
                self.debloquer_succes(s)

        if "module" in conditions:
            self.modules_joues.add(conditions["module"])
            if len(self.modules_joues) >= 4:
                for s in self.liste_succes:
                    if s["id"] == "tous_modules" and s["id"] not in self.succes_debloques:
                        self.debloquer_succes(s)

    def debloquer_succes(self, succes):
        self.succes_debloques.append(succes["id"])
        self.experience_totale += succes["xp"]
        self.animer_succes(succes["nom"], succes["description"], succes["xp"])
        self.sauvegarder_profil()

    def animer_succes(self, nom, description, xp):
        anim = tk.Toplevel(self.fenetre)
        anim.overrideredirect(True)
        anim.attributes('-topmost', True)
        anim.configure(bg='#2c3e50')
        w = 400
        h = 150
        x = self.fenetre.winfo_x() + (self.fenetre.winfo_width() - w) // 2
        y = self.fenetre.winfo_y() + (self.fenetre.winfo_height() - h) // 2
        anim.geometry(f"{w}x{h}+{x}+{y}")
        anim.attributes('-alpha', 0.0)

        frame = tk.Frame(anim, bg='#2c3e50')
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(frame, text="🏆 SUCCÈS DÉBLOQUÉ ! 🏆", font=('Arial', 16, 'bold'),
                fg='#ffd700', bg='#2c3e50').pack()
        tk.Label(frame, text=nom, font=('Arial', 14, 'bold'),
                fg='white', bg='#2c3e50').pack(pady=5)
        tk.Label(frame, text=description, font=('Arial', 10),
                fg='#ecf0f1', bg='#2c3e50').pack()
        tk.Label(frame, text=f"+{xp} XP", font=('Arial', 12, 'bold'),
                fg='#2ecc71', bg='#2c3e50').pack(pady=5)

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                anim.attributes('-alpha', alpha)
                anim.after(20, lambda: fade_in(alpha + 0.05))
            else:
                anim.after(2000, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                anim.attributes('-alpha', alpha)
                anim.after(20, lambda: fade_out(alpha - 0.05))
            else:
                anim.destroy()

        fade_in()

    def verifier_badges(self, conditions):
        for badge in self.badges_definitions:
            if badge["id"] in self.badges_debloques:
                continue
            if badge["id"] == "maitre_clic_gauche" and conditions.get("clic_gauche_perfect"):
                self.debloquer_badge(badge)
            elif badge["id"] == "maitre_clic_droit" and conditions.get("clic_droit_perfect"):
                self.debloquer_badge(badge)
            elif badge["id"] == "maitre_double_clic" and conditions.get("double_clic_perfect"):
                self.debloquer_badge(badge)
            elif badge["id"] == "as_glisser_deposer" and conditions.get("glisser_deposer_perfect"):
                self.debloquer_badge(badge)
            elif badge["id"] == "speed_click_niveau5" and conditions.get("speed_niveau", 0) >= 5:
                self.debloquer_badge(badge)
            elif badge["id"] == "keyboard_niveau10" and conditions.get("keyboard_niveau", 0) >= 10:
                self.debloquer_badge(badge)
            elif badge["id"] == "dactylo_50wpm" and conditions.get("wpm", 0) >= 50:
                self.debloquer_badge(badge)
            elif badge["id"] == "combo_20" and conditions.get("max_combo", 0) >= 20:
                self.debloquer_badge(badge)

    def debloquer_badge(self, badge):
        self.badges_debloques.append(badge["id"])
        self.experience_totale += badge["xp"]
        self.animer_badge(badge["nom"], badge["description"], badge["xp"])
        self.sauvegarder_profil()

    def animer_badge(self, nom, description, xp):
        anim = tk.Toplevel(self.fenetre)
        anim.overrideredirect(True)
        anim.attributes('-topmost', True)
        anim.configure(bg='#2c3e50')
        w = 400
        h = 150
        x = self.fenetre.winfo_x() + (self.fenetre.winfo_width() - w) // 2
        y = self.fenetre.winfo_y() + (self.fenetre.winfo_height() - h) // 2
        anim.geometry(f"{w}x{h}+{x}+{y}")
        anim.attributes('-alpha', 0.0)

        frame = tk.Frame(anim, bg='#2c3e50')
        frame.pack(expand=True, fill='both', padx=20, pady=20)

        tk.Label(frame, text="🥇 BADGE OBTENU ! 🥇", font=('Arial', 16, 'bold'),
                fg='#ffd700', bg='#2c3e50').pack()
        tk.Label(frame, text=nom, font=('Arial', 14, 'bold'),
                fg='white', bg='#2c3e50').pack(pady=5)
        tk.Label(frame, text=description, font=('Arial', 10),
                fg='#ecf0f1', bg='#2c3e50').pack()
        tk.Label(frame, text=f"+{xp} XP", font=('Arial', 12, 'bold'),
                fg='#2ecc71', bg='#2c3e50').pack(pady=5)

        def fade_in(alpha=0.0):
            if alpha < 1.0:
                anim.attributes('-alpha', alpha)
                anim.after(20, lambda: fade_in(alpha + 0.05))
            else:
                anim.after(2000, fade_out)

        def fade_out(alpha=1.0):
            if alpha > 0.0:
                anim.attributes('-alpha', alpha)
                anim.after(20, lambda: fade_out(alpha - 0.05))
            else:
                anim.destroy()

        fade_in()

    def creer_interface(self):
        self.creer_barre_superieure()
        self.contenu_principal = tk.Frame(self.fenetre, bg=self.colors['bg'])
        self.contenu_principal.pack(expand=True, fill='both', padx=20, pady=10)
        self.creer_barre_inferieure()

    def creer_barre_superieure(self):
        barre = tk.Frame(self.fenetre, bg=self.colors['secondary'], height=80)
        barre.pack(fill='x')
        barre.pack_propagate(False)

        titre = tk.Label(
            barre,
            text="🎮 CENTRE D'ÉVALUATION - MAÎTRISE SOURIS & CLAVIER 🎮",
            font=('Arial', 22, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['gold']
        )
        titre.pack(side='left', padx=20, pady=10)

        stats_frame = tk.Frame(barre, bg=self.colors['secondary'])
        stats_frame.pack(side='right', padx=20)

        self.label_niveau = tk.Label(
            stats_frame,
            text=f"⭐ Niveau {self.niveau_global}",
            font=('Arial', 12, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['warning']
        )
        self.label_niveau.pack(side='left', padx=10)

        self.label_xp = tk.Label(
            stats_frame,
            text=f"📊 XP: {self.experience_totale}",
            font=('Arial', 11),
            bg=self.colors['secondary'],
            fg=self.colors['text']
        )
        self.label_xp.pack(side='left', padx=10)

        btn_profil = tk.Button(
            stats_frame,
            text=f"👤 {self.profil_actuel}",
            command=self.ouvrir_profil,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 10),
            cursor='hand2',
            relief='flat',
            padx=15
        )
        btn_profil.pack(side='left', padx=10)

    def creer_barre_inferieure(self):
        barre = tk.Frame(self.fenetre, bg=self.colors['secondary'], height=40)
        barre.pack(fill='x', side='bottom')
        barre.pack_propagate(False)

        btn_accueil = tk.Button(
            barre,
            text="🏠 ACCUEIL",
            command=self.afficher_accueil,
            bg=self.colors['accent'],
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20
        )
        btn_accueil.pack(side='left', padx=10, pady=5)

        btn_classement = tk.Button(
            barre,
            text="🏆 CLASSEMENT GÉNÉRAL",
            command=self.afficher_classement,
            bg=self.colors['warning'],
            fg='black',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20
        )
        btn_classement.pack(side='left', padx=10, pady=5)

        btn_succes = tk.Button(
            barre,
            text="🎯 SUCCÈS",
            command=self.afficher_succes,
            bg=self.colors['success'],
            fg='white',
            font=('Arial', 10, 'bold'),
            cursor='hand2',
            relief='flat',
            padx=20
        )
        btn_succes.pack(side='left', padx=10, pady=5)

        copyright_label = tk.Label(
            barre,
            text="© 2026 - Arnaud Fourcade - Pôle d'Appui à la scolarité - MPA -",
            font=('Arial', 9),
            bg=self.colors['secondary'],
            fg='#7f8c8d'
        )
        copyright_label.pack(side='right', padx=20)

    def afficher_accueil(self):
        for widget in self.contenu_principal.winfo_children():
            widget.destroy()

        tk.Label(
            self.contenu_principal,
            text="CHOISISSEZ VOTRE MODULE D'ENTRAÎNEMENT",
            font=('Arial', 18, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['gold']
        ).pack(pady=20)

        cartes_frame = tk.Frame(self.contenu_principal, bg=self.colors['bg'])
        cartes_frame.pack(expand=True, fill='both', padx=50, pady=20)

        for i in range(4):
            cartes_frame.grid_columnconfigure(i, weight=1)

        self.creer_carte_module(
            cartes_frame, 0,
            "🖱️ SPEED CLICK",
            "Testez votre rapidité et précision\navec la souris (cibles de taille décroissante)",
            ["🎯 Clics gauche/droite", "⚡ Temps de réaction", "📏 Taille réduite avec le niveau"],
            "#3498db",
            self.lancer_speed_click
        )

        self.creer_carte_module(
            cartes_frame, 1,
            "⌨️ KEYBOARD MASTER",
            "Apprenez à taper rapidement\nsur tout le clavier",
            ["🔤 Alphabet", "✨ Accents", "⌨️ Raccourcis", "🌟 All Stars"],
            "#e74c3c",
            self.lancer_keyboard_master
        )

        self.creer_carte_module(
            cartes_frame, 2,
            "🐭 ATELIER SOURIS",
            "Exercices progressifs pour\nmaîtriser tous les clics",
            ["🖱️ Clic gauche/droit", "✋ Glisser-déposer", "⬆️ Double-clic"],
            "#2ecc71",
            self.lancer_atelier_souris
        )

        self.creer_carte_module(
            cartes_frame, 3,
            "📝 DACTYLO",
            "Entraînez-vous à taper du texte\navec précision et rapidité",
            ["📜 Texte de La Fontaine", "📊 WPM et précision", "📈 Analyse des erreurs"],
            "#9b59b6",
            self.lancer_dactylo
        )

        stats_frame = tk.Frame(self.contenu_principal, bg=self.colors['secondary'])
        stats_frame.pack(fill='x', padx=50, pady=20)

        tk.Label(
            stats_frame,
            text="📈 VOS STATISTIQUES GLOBALES",
            font=('Arial', 14, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['gold']
        ).pack(pady=10)

        stats_grid = tk.Frame(stats_frame, bg=self.colors['secondary'])
        stats_grid.pack()

        stats = [
            ("Parties jouées", str(self.parties_jouees)),
            ("Niveau global", str(self.niveau_global)),
            ("XP total", str(self.experience_totale)),
            ("Prochain niveau", f"{self.xp_necessaire() - self.experience_totale} XP")
        ]

        for i, (label, valeur) in enumerate(stats):
            frame = tk.Frame(stats_grid, bg=self.colors['secondary'])
            frame.grid(row=0, column=i, padx=30)

            tk.Label(
                frame, text=label,
                font=('Arial', 10),
                bg=self.colors['secondary'],
                fg='#7f8c8d'
            ).pack()

            tk.Label(
                frame, text=valeur,
                font=('Arial', 18, 'bold'),
                bg=self.colors['secondary'],
                fg=self.colors['text']
            ).pack()

        xp_frame = tk.Frame(stats_frame, bg=self.colors['secondary'])
        xp_frame.pack(fill='x', padx=20, pady=10)

        progression = (self.experience_totale % 1000) / 1000
        barre_xp = tk.Canvas(xp_frame, height=20, bg='#2c3e50', highlightthickness=0)
        barre_xp.pack(fill='x')

        barre_xp.create_rectangle(0, 0, 800 * progression, 20, fill=self.colors['success'])
        barre_xp.create_text(400, 10, text=f"XP: {self.experience_totale} / {self.xp_necessaire()}",
                            fill='white', font=('Arial', 10, 'bold'))

    def creer_carte_module(self, parent, colonne, titre, description, caracteristiques, couleur, commande):
        carte = tk.Frame(parent, bg=self.colors['secondary'], relief='raised', bd=2)
        carte.grid(row=0, column=colonne, padx=10, sticky='nsew')

        header = tk.Frame(carte, bg=couleur, height=60)
        header.pack(fill='x')
        header.pack_propagate(False)

        tk.Label(
            header, text=titre,
            font=('Arial', 14, 'bold'),
            bg=couleur,
            fg='white'
        ).pack(expand=True)

        contenu = tk.Frame(carte, bg=self.colors['secondary'])
        contenu.pack(fill='both', expand=True, padx=10, pady=10)

        tk.Label(
            contenu, text=description,
            font=('Arial', 9),
            bg=self.colors['secondary'],
            fg=self.colors['text'],
            justify='center'
        ).pack(pady=5)

        for carac in caracteristiques:
            tk.Label(
                contenu, text=f"• {carac}",
                font=('Arial', 8),
                bg=self.colors['secondary'],
                fg='#7f8c8d'
            ).pack(anchor='w', pady=1)

        btn = tk.Button(
            contenu,
            text="🚀 LANCER",
            command=commande,
            bg=couleur,
            fg='white',
            font=('Arial', 11, 'bold'),
            cursor='hand2',
            relief='flat',
            height=2
        )
        btn.pack(fill='x', pady=10)

    def afficher_classement(self):
        classement_window = tk.Toplevel(self.fenetre)
        classement_window.title("🏆 CLASSEMENT GÉNÉRAL")
        classement_window.geometry("800x600")
        classement_window.configure(bg=self.colors['secondary'])
        classement_window.state('zoomed')

        tk.Label(classement_window, text="🏆 CLASSEMENT GÉNÉRAL 🏆",
                font=('Arial', 24, 'bold'), bg=self.colors['secondary'],
                fg=self.colors['gold']).pack(pady=20)

        notebook = ttk.Notebook(classement_window)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        frame_general = tk.Frame(notebook, bg=self.colors['bg'])
        notebook.add(frame_general, text="Général")

        tree_general = ttk.Treeview(frame_general, columns=('joueur', 'module', 'score', 'date'), show='headings', height=20)
        tree_general.heading('joueur', text='Joueur')
        tree_general.heading('module', text='Module')
        tree_general.heading('score', text='Score')
        tree_general.heading('date', text='Date')
        tree_general.column('joueur', width=150)
        tree_general.column('module', width=150)
        tree_general.column('score', width=100)
        tree_general.column('date', width=150)
        tree_general.pack(fill='both', expand=True, padx=10, pady=10)

        for entry in self.scores_globaux[:50]:
            tree_general.insert('', 'end', values=(entry['joueur'], entry['module'], entry['score'], entry['date']))

        modules = ["Speed Click", "Keyboard Master", "Atelier Souris", "Dactylo"]
        for module in modules:
            frame = tk.Frame(notebook, bg=self.colors['bg'])
            notebook.add(frame, text=module)

            tree = ttk.Treeview(frame, columns=('joueur', 'score', 'niveau', 'combo', 'date'), show='headings', height=20)
            tree.heading('joueur', text='Joueur')
            tree.heading('score', text='Score')
            tree.heading('niveau', text='Niveau')
            tree.heading('combo', text='Combo')
            tree.heading('date', text='Date')
            tree.column('joueur', width=150)
            tree.column('score', width=100)
            tree.column('niveau', width=80)
            tree.column('combo', width=80)
            tree.column('date', width=150)
            tree.pack(fill='both', expand=True, padx=10, pady=10)

            for entry in self.scores_globaux:
                if entry['module'] == module:
                    tree.insert('', 'end', values=(entry['joueur'], entry['score'], entry.get('niveau', '-'), entry.get('combo', '-'), entry['date']))

        tk.Button(classement_window, text="Fermer", command=classement_window.destroy,
                 bg=self.colors['accent'], fg='white', font=('Arial', 12),
                 padx=30, pady=10).pack(pady=20)

    def afficher_succes(self):
        succes_window = tk.Toplevel(self.fenetre)
        succes_window.title("🎯 SUCCÈS")
        succes_window.geometry("700x600")
        succes_window.configure(bg=self.colors['secondary'])

        tk.Label(succes_window, text="🎯 VOS SUCCÈS 🎯",
                font=('Arial', 20, 'bold'), bg=self.colors['secondary'],
                fg=self.colors['gold']).pack(pady=20)

        main_frame = tk.Frame(succes_window, bg=self.colors['secondary'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)

        canvas = tk.Canvas(main_frame, bg=self.colors['secondary'], highlightthickness=0)
        scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['secondary'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for s in self.liste_succes:
            frame = tk.Frame(scrollable_frame, bg=self.colors['bg'], relief='ridge', bd=1)
            frame.pack(fill='x', padx=10, pady=5)

            if s["id"] in self.succes_debloques:
                emoji = "✅"
                couleur = self.colors['success']
            else:
                emoji = "🔒"
                couleur = '#7f8c8d'

            tk.Label(frame, text=f"{emoji} {s['nom']}", font=('Arial', 14, 'bold'),
                    bg=self.colors['bg'], fg=couleur).pack(anchor='w', padx=10, pady=5)
            tk.Label(frame, text=s['description'], font=('Arial', 10),
                    bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w', padx=20)
            tk.Label(frame, text=f"+{s['xp']} XP", font=('Arial', 10, 'italic'),
                    bg=self.colors['bg'], fg=self.colors['warning']).pack(anchor='w', padx=20, pady=(0,5))

        tk.Button(succes_window, text="Fermer", command=succes_window.destroy,
                 bg=self.colors['accent'], fg='white', font=('Arial', 12),
                 padx=30, pady=10).pack(pady=20)

    def lancer_speed_click(self):
        self.fenetre.withdraw()
        jeu = SpeedClickModule(self)
        jeu.demarrer()

    def lancer_keyboard_master(self):
        self.fenetre.withdraw()
        jeu = KeyboardMasterModule(self)
        jeu.demarrer()

    def lancer_atelier_souris(self):
        self.fenetre.withdraw()
        jeu = AtelierSourisModule(self)
        jeu.demarrer()

    def lancer_dactylo(self):
        self.fenetre.withdraw()
        jeu = DactyloModule(self)
        jeu.demarrer()

    def ajouter_experience(self, xp):
        self.experience_totale += xp
        self.parties_jouees += 1

        nouveau_niveau = self.calculer_niveau()
        if nouveau_niveau > self.niveau_global:
            self.niveau_global = nouveau_niveau
            messagebox.showinfo("Niveau supérieur !",
                              f"Félicitations ! Vous passez au niveau {self.niveau_global} !")

        self.sauvegarder_profil()
        self.label_niveau.config(text=f"⭐ Niveau {self.niveau_global}")
        self.label_xp.config(text=f"📊 XP: {self.experience_totale}")

    def calculer_niveau(self):
        return (self.experience_totale // 1000) + 1

    def xp_necessaire(self):
        return (self.calculer_niveau()) * 1000

    def ouvrir_profil(self):
        dialog = tk.Toplevel(self.fenetre)
        dialog.title("👤 Profil Joueur")
        dialog.geometry("600x600")
        dialog.configure(bg=self.colors['secondary'])

        tk.Label(
            dialog, text=f"PROFIL : {self.profil_actuel}",
            font=('Arial', 18, 'bold'),
            bg=self.colors['secondary'],
            fg=self.colors['gold']
        ).pack(pady=20)

        notebook = ttk.Notebook(dialog)
        notebook.pack(fill='both', expand=True, padx=20, pady=10)

        # Onglet Stats
        frame_stats = tk.Frame(notebook, bg=self.colors['secondary'])
        notebook.add(frame_stats, text="Statistiques")

        stats = self.profils.get(self.profil_actuel, {})
        stats_clavier = stats.get("stats_clavier", {})
        stats_souris = stats.get("stats_souris", {})

        tk.Label(frame_stats, text="⌨️ STATISTIQUES CLAVIER", font=('Arial', 14, 'bold'),
                bg=self.colors['secondary'], fg='#3498db').pack(anchor='w', pady=(10,5))

        reussites_c = stats_clavier.get("reussites", 0)
        erreurs_c = stats_clavier.get("erreurs", 0)
        total_c = reussites_c + erreurs_c
        precision_c = (reussites_c / total_c * 100) if total_c > 0 else 0

        tk.Label(frame_stats, text=f"Réussites : {reussites_c}", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(frame_stats, text=f"Erreurs : {erreurs_c}", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(frame_stats, text=f"Précision : {precision_c:.1f}%", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')

        tk.Label(frame_stats, text="🖱️ STATISTIQUES SOURIS", font=('Arial', 14, 'bold'),
                bg=self.colors['secondary'], fg='#2ecc71').pack(anchor='w', pady=(20,5))

        reussites_s = stats_souris.get("reussites", 0)
        erreurs_s = stats_souris.get("erreurs", 0)
        total_s = reussites_s + erreurs_s
        precision_s = (reussites_s / total_s * 100) if total_s > 0 else 0

        tk.Label(frame_stats, text=f"Réussites : {reussites_s}", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(frame_stats, text=f"Erreurs : {erreurs_s}", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')
        tk.Label(frame_stats, text=f"Précision : {precision_s:.1f}%", bg=self.colors['secondary'], fg=self.colors['text']).pack(anchor='w')

        # Onglet Badges
        frame_badges = tk.Frame(notebook, bg=self.colors['secondary'])
        notebook.add(frame_badges, text="🥇 Badges")

        canvas_b = tk.Canvas(frame_badges, bg=self.colors['secondary'], highlightthickness=0)
        scrollbar_b = tk.Scrollbar(frame_badges, orient='vertical', command=canvas_b.yview)
        scrollable_b = tk.Frame(canvas_b, bg=self.colors['secondary'])

        scrollable_b.bind("<Configure>", lambda e: canvas_b.configure(scrollregion=canvas_b.bbox("all")))
        canvas_b.create_window((0, 0), window=scrollable_b, anchor="nw")
        canvas_b.configure(yscrollcommand=scrollbar_b.set)

        canvas_b.pack(side="left", fill="both", expand=True)
        scrollbar_b.pack(side="right", fill="y")

        for badge in self.badges_definitions:
            frame = tk.Frame(scrollable_b, bg=self.colors['bg'], relief='ridge', bd=1)
            frame.pack(fill='x', padx=10, pady=5)

            if badge["id"] in self.badges_debloques:
                emoji = "🥇"
                couleur = self.colors['success']
            else:
                emoji = "🔒"
                couleur = '#7f8c8d'

            tk.Label(frame, text=f"{emoji} {badge['nom']}", font=('Arial', 14, 'bold'),
                    bg=self.colors['bg'], fg=couleur).pack(anchor='w', padx=10, pady=5)
            tk.Label(frame, text=badge['description'], font=('Arial', 10),
                    bg=self.colors['bg'], fg=self.colors['text']).pack(anchor='w', padx=20)
            tk.Label(frame, text=f"+{badge['xp']} XP", font=('Arial', 10, 'italic'),
                    bg=self.colors['bg'], fg=self.colors['warning']).pack(anchor='w', padx=20, pady=(0,5))

        def changer_profil():
            dialog.destroy()
            self.selectionner_profil()
            self.charger_profil()
            self.label_niveau.config(text=f"⭐ Niveau {self.niveau_global}")
            self.label_xp.config(text=f"📊 XP: {self.experience_totale}")

        tk.Button(dialog, text="Changer de profil", command=changer_profil,
                 bg=self.colors['warning'], fg='black', font=('Arial', 12),
                 padx=20, pady=10).pack(pady=10)

        tk.Button(dialog, text="Fermer", command=dialog.destroy,
                 bg=self.colors['accent'], fg='white', font=('Arial', 12),
                 padx=20, pady=10).pack(pady=10)

    def demarrer(self):
        self.fenetre.mainloop()


# ============================================================
# MODULE SPEED CLICK
# ============================================================

class SpeedClickModule:
    def __init__(self, parent):
        self.parent = parent
        self.fenetre = tk.Toplevel(parent.fenetre)
        self.fenetre.title("🖱️ SPEED CLICK - Test de Vitesse & Précision")
        self.fenetre.geometry("1200x800")
        self.fenetre.configure(bg='#1a2634')
        self.fenetre.state('zoomed')
        self.fenetre.bind('<F11>', lambda e: self.parent.toggle_fullscreen(e))

        self.en_jeu = False
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.niveau = 1
        self.vies = 3
        self.vies_max = 3
        self.cibles_touchees = 0
        self.cibles_ratees = 0
        self.temps_total = 0
        self.reussites_consecutives = 0

        self.cible_id = None
        self.type_cible = None
        self.position_cible = (600, 400)
        self.temps_apparition = 0
        self.timer_id = None

        self.config_niveaux = {
            1: {"vitesse": 3.0, "taille": 45},
            2: {"vitesse": 2.8, "taille": 38},
            3: {"vitesse": 2.5, "taille": 32},
            4: {"vitesse": 2.2, "taille": 26},
            5: {"vitesse": 1.8, "taille": 22},
            6: {"vitesse": 1.5, "taille": 18},
            7: {"vitesse": 1.2, "taille": 15},
            8: {"vitesse": 1.0, "taille": 12},
        }

        self.creer_interface()

    def creer_interface(self):
        barre = tk.Frame(self.fenetre, bg='#2c3e50', height=60)
        barre.pack(fill='x')

        self.score_label = tk.Label(barre, text="Score: 0", font=('Arial', 16, 'bold'),
                                    bg='#2c3e50', fg='#ffd700')
        self.score_label.pack(side='left', padx=20)

        self.combo_label = tk.Label(barre, text="Combo: x0", font=('Arial', 14),
                                    bg='#2c3e50', fg='#e74c3c')
        self.combo_label.pack(side='left', padx=20)

        self.niveau_label = tk.Label(barre, text="Niveau: 1", font=('Arial', 14),
                                     bg='#2c3e50', fg='#3498db')
        self.niveau_label.pack(side='left', padx=20)

        self.vies_label = tk.Label(barre, text="❤️ ❤️ ❤️", font=('Arial', 14),
                                   bg='#2c3e50', fg='#e74c3c')
        self.vies_label.pack(side='right', padx=20)

        self.zone_jeu = tk.Canvas(self.fenetre, bg='#1e2b3a', cursor='crosshair')
        self.zone_jeu.pack(expand=True, fill='both', padx=10, pady=10)

        barre_bas = tk.Frame(self.fenetre, bg='#2c3e50', height=50)
        barre_bas.pack(fill='x', side='bottom')

        self.btn_demarrer = tk.Button(barre_bas, text="🚀 DÉMARRER",
                                      command=self.demarrer_partie,
                                      bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                      padx=30, pady=10)
        self.btn_demarrer.pack(side='left', padx=20)

        tk.Button(barre_bas, text="🏠 QUITTER", command=self.quitter,
                 bg='#e74c3c', fg='white', font=('Arial', 12),
                 padx=30, pady=10).pack(side='right', padx=20)

        self.zone_jeu.bind('<Button-1>', self.on_clic_gauche)
        self.zone_jeu.bind('<Button-3>', self.on_clic_droit)

        self.afficher_accueil()

    def afficher_accueil(self):
        self.zone_jeu.delete("all")
        self.zone_jeu.create_text(
            600, 350,
            text="🖱️ SPEED CLICK 🖱️\n\n"
                 "🔵 Clic GAUCHE sur les carrés bleus\n"
                 "🔴 Clic DROIT sur les ronds rouges\n"
                 "📏 La taille des cibles diminue avec le niveau !\n\n"
                 "Cliquez sur DÉMARRER pour commencer !",
            fill='#ecf0f1',
            font=('Arial', 16),
            justify='center'
        )

    def demarrer_partie(self):
        self.en_jeu = True
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.niveau = 1
        self.vies = 3
        self.cibles_touchees = 0
        self.cibles_ratees = 0
        self.reussites_consecutives = 0

        self.btn_demarrer.config(text="⚡ EN JEU", bg='#e67e22', state='disabled')
        self.mettre_a_jour_interface()
        self.zone_jeu.delete("all")
        self.creer_cible()

    def creer_cible(self):
        if not self.en_jeu or self.vies <= 0:
            if self.vies <= 0:
                self.terminer_partie()
            return

        self.zone_jeu.delete("cible")

        x = random.randint(100, self.zone_jeu.winfo_width() - 100)
        y = random.randint(100, self.zone_jeu.winfo_height() - 100)
        self.position_cible = (x, y)

        self.type_cible = random.choice(['gauche', 'droit'])
        config = self.config_niveaux[self.niveau]
        taille = config["taille"]

        if self.type_cible == 'gauche':
            self.cible_id = self.zone_jeu.create_rectangle(
                x-taille, y-taille, x+taille, y+taille,
                fill='#3498db', outline='white', width=2, tags="cible"
            )
            self.zone_jeu.create_text(x, y, text="GAUCHE", fill='white',
                                     font=('Arial', max(8, taille//2), 'bold'), tags="cible")
        else:
            self.cible_id = self.zone_jeu.create_oval(
                x-taille, y-taille, x+taille, y+taille,
                fill='#e74c3c', outline='white', width=2, tags="cible"
            )
            self.zone_jeu.create_text(x, y, text="DROIT", fill='white',
                                     font=('Arial', max(8, taille//2), 'bold'), tags="cible")

        self.temps_apparition = time.time()

        if self.timer_id:
            self.fenetre.after_cancel(self.timer_id)
        self.timer_id = self.fenetre.after(int(config["vitesse"] * 1000), self.temps_ecoule)

    def temps_ecoule(self):
        if self.en_jeu:
            self.vies -= 1
            self.combo = 0
            self.reussites_consecutives = 0
            self.mettre_a_jour_interface()

            if self.vies > 0:
                self.creer_cible()
            else:
                self.terminer_partie()

    def on_clic_gauche(self, event):
        if not self.en_jeu or not self.cible_id:
            return

        x, y = event.x, event.y
        cx, cy = self.position_cible
        distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5

        taille = self.config_niveaux[self.niveau]["taille"]
        if distance < taille + 10:
            if self.type_cible == 'gauche':
                self.traiter_bon_clic()
            else:
                self.traiter_mauvais_clic()
        else:
            self.traiter_cible_loupee()

    def on_clic_droit(self, event):
        if not self.en_jeu or not self.cible_id:
            return

        x, y = event.x, event.y
        cx, cy = self.position_cible
        distance = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5

        taille = self.config_niveaux[self.niveau]["taille"]
        if distance < taille + 10:
            if self.type_cible == 'droit':
                self.traiter_bon_clic()
            else:
                self.traiter_mauvais_clic()
        else:
            self.traiter_cible_loupee()

    def traiter_bon_clic(self):
        if self.timer_id:
            self.fenetre.after_cancel(self.timer_id)

        temps_reaction = time.time() - self.temps_apparition
        self.temps_total += temps_reaction

        points = int(100 + self.combo * 50 + (45 - self.config_niveaux[self.niveau]["taille"]) * 2)
        if temps_reaction < 0.5:
            points += 100

        self.score += points
        self.cibles_touchees += 1
        self.combo += 1
        self.max_combo = max(self.max_combo, self.combo)
        self.reussites_consecutives += 1

        if self.cibles_touchees >= self.niveau * 5 and self.niveau < 8:
            self.niveau += 1
            self.cibles_touchees = 0

        self.mettre_a_jour_interface()
        self.creer_cible()

    def traiter_mauvais_clic(self):
        self.vies -= 1
        self.score -= 25
        self.cibles_ratees += 1
        self.combo = 0
        self.reussites_consecutives = 0

        self.mettre_a_jour_interface()

        if self.vies > 0:
            self.creer_cible()
        else:
            self.terminer_partie()

    def traiter_cible_loupee(self):
        self.score -= 10
        self.cibles_ratees += 1
        self.combo = 0
        self.reussites_consecutives = 0
        self.mettre_a_jour_interface()

    def mettre_a_jour_interface(self):
        self.score_label.config(text=f"Score: {self.score}")
        self.combo_label.config(text=f"Combo: x{self.combo}")
        self.niveau_label.config(text=f"Niveau: {self.niveau} (taille: {self.config_niveaux[self.niveau]['taille']})")

        vies_texte = "❤️ " * self.vies + "🖤 " * (self.vies_max - self.vies)
        self.vies_label.config(text=vies_texte.strip())

    def terminer_partie(self):
        self.en_jeu = False
        self.btn_demarrer.config(text="🚀 DÉMARRER", bg='#27ae60', state='normal')

        xp_gagne = max(10, self.score // 10 + self.max_combo * 5)
        self.parent.ajouter_experience(xp_gagne)
        self.parent.sauvegarder_score("Speed Click", self.score, self.niveau, self.max_combo)

        if self.parent.profil_actuel in self.parent.profils:
            stats = self.parent.profils[self.parent.profil_actuel].get("stats_souris", {"reussites": 0, "erreurs": 0})
            stats["reussites"] += self.cibles_touchees
            stats["erreurs"] += self.cibles_ratees
            self.parent.profils[self.parent.profil_actuel]["stats_souris"] = stats
            self.parent.sauvegarder_tous_profils()

        self.parent.verifier_succes({
            "partie_terminee": True,
            "max_combo": self.max_combo,
            "score": self.score,
            "module": "Speed Click",
            "perfect_souris": self.cibles_touchees >= 10 and self.cibles_ratees == 0
        })
        self.parent.verifier_badges({
            "speed_niveau": self.niveau,
            "max_combo": self.max_combo
        })

        self.zone_jeu.delete("all")
        self.zone_jeu.create_text(
            600, 300,
            text=f"PARTIE TERMINÉE !\n\n"
                 f"Score: {self.score}\n"
                 f"Niveau: {self.niveau}\n"
                 f"Combo max: x{self.max_combo}\n"
                 f"XP gagné: +{xp_gagne}\n\n"
                 f"Cliquez sur DÉMARRER pour rejouer",
            fill='#ecf0f1',
            font=('Arial', 16),
            justify='center'
        )

    def quitter(self):
        self.fenetre.destroy()
        self.parent.fenetre.deiconify()
        self.parent.afficher_accueil()
        self.parent.fenetre.state('zoomed')

    def demarrer(self):
        self.fenetre.protocol("WM_DELETE_WINDOW", self.quitter)
        self.fenetre.mainloop()


# ============================================================
# MODULE KEYBOARD MASTER (avec heatmap des touches)
# ============================================================

class KeyboardMasterModule:
    def __init__(self, parent):
        self.parent = parent
        self.fenetre = tk.Toplevel(parent.fenetre)
        self.fenetre.title("⌨️ KEYBOARD MASTER - Apprentissage du Clavier")
        self.fenetre.geometry("1400x850")
        self.fenetre.configure(bg='#1a2634')
        self.fenetre.state('zoomed')
        self.fenetre.bind('<F11>', lambda e: self.parent.toggle_fullscreen(e))

        self.en_jeu = False
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.meilleur_score = 0
        self.niveau = 1
        self.vies = 3
        self.vies_max = 3
        self.cibles_touchees = 0
        self.cibles_ratees = 0
        self.cibles_loupees = 0
        self.temps_total = 0
        self.parties_jouees = 0
        self.mode_actuel = "lettres"
        self.cible_actuelle = None
        self.couleur_actuelle = None
        self.derniere_couleur = None
        self.sequence_accent = ""

        self.stats_touches = defaultdict(lambda: {"reussites": 0, "erreurs": 0})

        self.bareme = {
            "reussite": 10,
            "bonus_combo": 2,
            "bonus_rapidite": 20,
            "erreur": -50,
            "trop_lent": -5
        }

        self.palette_couleurs = [
            "#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7",
            "#DDA0DD", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2",
            "#F8C471", "#82E0AA", "#F1948A", "#85C1E2", "#D7BDE2"
        ]

        self.config_modes = {
            "lettres": {
                "nom": "Alphabet",
                "cibles": [
                    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
                    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
                    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
                ],
                "description": "Tapez les lettres (majuscules et minuscules)"
            },
            "accents": {
                "nom": "Accents",
                "cibles": ['é', 'è', 'ê', 'à', 'â', 'ô', 'ç', 'û', 'ü'],
                "description": "Caractères accentués"
            },
            "ponctuation": {
                "nom": "Ponctuation",
                "cibles": ['!', '?', ';', ':', '/', '-', '.', ',', '(', ')'],
                "description": "Signes de ponctuation"
            },
            "raccourcis": {
                "nom": "Raccourcis",
                "cibles": [
                    {"nom": "Tout sélectionner", "raccourci": "Ctrl+A"},
                    {"nom": "Copier", "raccourci": "Ctrl+C"},
                    {"nom": "Couper", "raccourci": "Ctrl+X"},
                    {"nom": "Coller", "raccourci": "Ctrl+V"},
                    {"nom": "Annuler", "raccourci": "Ctrl+Z"},
                    {"nom": "Rétablir", "raccourci": "Ctrl+Y"}
                ],
                "description": "Raccourcis clavier"
            },
            "allstars": {
                "nom": "All Stars",
                "cibles": self.generer_all_stars(),
                "description": "Tout mélangé !"
            }
        }

        self.label_cible = None
        self.temps_apparition = 0
        self.timer_disparition_id = None
        self.chrono_id = None
        self.attente_saisie = False

        self.temps_par_niveau = {
            1: 5.0, 2: 4.5, 3: 4.0, 4: 3.5, 5: 3.0,
            6: 2.8, 7: 2.5, 8: 2.2, 9: 2.0, 10: 1.8
        }

        self.charger_statistiques()
        self.creer_interface()

    def generer_all_stars(self):
        all_cibles = []
        all_cibles.extend([
            'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
            'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
        ])
        all_cibles.extend(['é', 'è', 'ê', 'à', 'â', 'ô', 'ç', 'û', 'ü', 'ï', 'î'])
        all_cibles.extend(['!', '?', ';', ':', '/', '-', '.', ',', '(', ')'])
        all_cibles.extend([
            "Tout sélectionner", "Copier", "Couper", "Coller", "Annuler", "Rétablir"
        ])
        random.shuffle(all_cibles)
        return all_cibles

    def creer_interface(self):
        self.fenetre.grid_rowconfigure(0, weight=0)
        self.fenetre.grid_rowconfigure(1, weight=1)
        self.fenetre.grid_rowconfigure(2, weight=0)
        self.fenetre.grid_columnconfigure(0, weight=1)

        titre_frame = tk.Frame(self.fenetre, bg='#1a2634', height=70)
        titre_frame.grid(row=0, column=0, sticky='ew', pady=5)
        titre_frame.grid_propagate(False)

        titre = tk.Label(
            titre_frame,
            text="⌨️ KEYBOARD MASTER ⌨️",
            font=('Arial', 28, 'bold'),
            bg='#1a2634',
            fg='#ffd700'
        )
        titre.pack(expand=True)

        frame_principal = tk.Frame(self.fenetre, bg='#1a2634')
        frame_principal.grid(row=1, column=0, sticky='nsew', padx=5, pady=2)
        frame_principal.grid_columnconfigure(1, weight=1)
        frame_principal.grid_rowconfigure(0, weight=1)

        self.creer_panneau_gauche(frame_principal)
        self.creer_zone_jeu(frame_principal)
        self.creer_panneau_droit(frame_principal)
        self.creer_barre_information()

        self.fenetre.bind('<Key>', self.on_touche_pressee)
        self.fenetre.bind('<Control-a>', self.on_ctrl_a)
        self.fenetre.bind('<Control-c>', self.on_ctrl_c)
        self.fenetre.bind('<Control-v>', self.on_ctrl_v)
        self.fenetre.bind('<Control-x>', self.on_ctrl_x)
        self.fenetre.bind('<Control-z>', self.on_ctrl_z)
        self.fenetre.bind('<Control-y>', self.on_ctrl_y)

        for key in ['<Shift_L>', '<Shift_R>', '<Control_L>', '<Control_R>', '<Alt_L>', '<Alt_R>']:
            self.fenetre.bind(key, lambda e: 'break')

        self.afficher_accueil()

    def creer_panneau_gauche(self, parent):
        container = tk.Frame(parent, bg='#2c3e50', width=220)
        container.grid(row=0, column=0, sticky='ns', padx=(0, 5))
        container.grid_propagate(False)

        canvas = tk.Canvas(container, bg='#2c3e50', highlightthickness=0, width=220)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        self.frame_stats = tk.Frame(canvas, bg='#2c3e50', width=210)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_window = canvas.create_window((0, 0), window=self.frame_stats, anchor='nw', width=210)

        self.frame_stats.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        self.remplir_panneau_gauche()

    def remplir_panneau_gauche(self):
        tk.Label(
            self.frame_stats,
            text="STATS",
            font=('Arial', 12, 'bold'),
            bg='#2c3e50',
            fg='#ffd700'
        ).pack(pady=5)

        score_container = tk.Frame(self.frame_stats, bg='#34495e', relief='ridge', bd=1)
        score_container.pack(fill='x', padx=8, pady=2)

        tk.Label(score_container, text="SCORE", font=('Arial', 8),
                bg='#34495e', fg='#bdc3c7').pack()

        self.score_label = tk.Label(score_container, text="0",
                                   font=('Arial', 18, 'bold'),
                                   bg='#34495e', fg='#ffd700')
        self.score_label.pack()

        self.btn_demarrer = tk.Button(
            self.frame_stats,
            text="🚀 LANCER",
            command=self.demarrer_partie,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            height=1,
            relief='raised',
            bd=2,
            cursor='hand2'
        )
        self.btn_demarrer.pack(fill='x', padx=8, pady=5)

        mode_frame = tk.LabelFrame(self.frame_stats, text="MODE", bg='#2c3e50',
                                  fg='#ecf0f1', font=('Arial', 9, 'bold'))
        mode_frame.pack(fill='x', padx=8, pady=2)

        self.mode_var = tk.StringVar(value="lettres")
        self.mode_var.trace('w', self.afficher_regles_mode)

        modes = [
            ("🔤 Alphabet (maj/min)", "lettres"),
            ("✨ Accents", "accents"),
            ("📝 Ponctuation", "ponctuation"),
            ("⌨️ Raccourcis", "raccourcis"),
            ("🌟 All Stars", "allstars")
        ]

        for texte, valeur in modes:
            rb = tk.Radiobutton(
                mode_frame,
                text=texte,
                value=valeur,
                variable=self.mode_var,
                command=self.changer_mode,
                bg='#2c3e50',
                fg='#ecf0f1',
                selectcolor='#2c3e50',
                activebackground='#34495e',
                font=('Arial', 8)
            )
            rb.pack(anchor='w', padx=5)

        vie_frame = tk.LabelFrame(self.frame_stats, text="VIES", bg='#2c3e50',
                                 fg='#ecf0f1', font=('Arial', 9, 'bold'))
        vie_frame.pack(fill='x', padx=8, pady=2)

        self.vies_canvas = tk.Canvas(vie_frame, height=30, bg='#34495e', highlightthickness=0)
        self.vies_canvas.pack(fill='x', padx=5, pady=2)

        self.vies_label = tk.Label(vie_frame, text="3/3", font=('Arial', 8, 'bold'),
                                  bg='#2c3e50', fg='#e74c3c')
        self.vies_label.pack()

        niveau_frame = tk.LabelFrame(self.frame_stats, text="NIVEAU", bg='#2c3e50',
                                    fg='#ecf0f1', font=('Arial', 9, 'bold'))
        niveau_frame.pack(fill='x', padx=8, pady=2)

        self.niveau_label = tk.Label(niveau_frame, text="1",
                                    font=('Arial', 10, 'bold'),
                                    bg='#2c3e50', fg='#3498db')
        self.niveau_label.pack()

        self.progress_bar = tk.Canvas(niveau_frame, height=15, bg='#34495e', highlightthickness=0)
        self.progress_bar.pack(fill='x', padx=5, pady=2)

        combo_frame = tk.Frame(self.frame_stats, bg='#2c3e50')
        combo_frame.pack(fill='x', padx=8, pady=2)

        tk.Label(combo_frame, text="COMBO", font=('Arial', 8),
                bg='#2c3e50', fg='#bdc3c7').pack()
        self.combo_label = tk.Label(combo_frame, text="x0",
                                   font=('Arial', 12, 'bold'),
                                   bg='#2c3e50', fg='#e74c3c')
        self.combo_label.pack()

        quick_stats = tk.Frame(self.frame_stats, bg='#2c3e50')
        quick_stats.pack(fill='x', padx=8, pady=2)

        self.stats_precision = tk.Label(quick_stats, text="0%", bg='#2c3e50',
                                        fg='#f1c40f', font=('Arial', 8, 'bold'))
        self.stats_temps = tk.Label(quick_stats, text="0.0s", bg='#2c3e50',
                                    fg='#f1c40f', font=('Arial', 8, 'bold'))
        self.stats_meilleur = tk.Label(quick_stats, text="0", bg='#2c3e50',
                                       fg='#f1c40f', font=('Arial', 8, 'bold'))

        stats = [
            ("Précision:", self.stats_precision),
            ("Temps:", self.stats_temps),
            ("Record:", self.stats_meilleur)
        ]

        for label, value_label in stats:
            ligne = tk.Frame(quick_stats, bg='#2c3e50')
            ligne.pack(fill='x')
            tk.Label(ligne, text=label, bg='#2c3e50', fg='#bdc3c7',
                    width=8, anchor='w', font=('Arial', 7)).pack(side='left')
            value_label.pack(side='right')

        tk.Button(self.frame_stats, text="📊 Stats détaillées", command=self.afficher_stats_touches,
                 bg='#34495e', fg='white', font=('Arial', 8)).pack(fill='x', padx=8, pady=5)
        tk.Button(self.frame_stats, text="🔥 Heatmap", command=self.afficher_heatmap,
                 bg='#e67e22', fg='white', font=('Arial', 8)).pack(fill='x', padx=8, pady=2)

    def creer_zone_jeu(self, parent):
        jeu_container = tk.Frame(parent, bg='#2c3e50', relief='sunken', bd=2)
        jeu_container.grid(row=0, column=1, sticky='nsew', padx=5)
        jeu_container.grid_rowconfigure(0, weight=1)
        jeu_container.grid_columnconfigure(0, weight=1)

        self.zone_jeu = tk.Canvas(
            jeu_container,
            bg='#1e2b3a',
            highlightthickness=0
        )
        self.zone_jeu.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

    def creer_panneau_droit(self, parent):
        container = tk.Frame(parent, bg='#2c3e50', width=200)
        container.grid(row=0, column=2, sticky='ns', padx=(5, 0))
        container.grid_propagate(False)

        canvas = tk.Canvas(container, bg='#2c3e50', highlightthickness=0, width=200)
        canvas.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        self.frame_droit = tk.Frame(canvas, bg='#2c3e50', width=190)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas_window = canvas.create_window((0, 0), window=self.frame_droit, anchor='nw', width=190)

        self.frame_droit.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: canvas.itemconfig(canvas_window, width=e.width))

        self.remplir_panneau_droit()

    def remplir_panneau_droit(self):
        classement_frame = tk.LabelFrame(self.frame_droit, text="🏆 CLASSEMENT", bg='#2c3e50',
                                        fg='#ffd700', font=('Arial', 10, 'bold'))
        classement_frame.pack(fill='both', padx=5, pady=5, expand=True)

        self.scores_listbox = tk.Listbox(
            classement_frame,
            bg='#34495e',
            fg='#ecf0f1',
            font=('Arial', 8),
            height=6,
            relief='flat',
            selectbackground='#3498db'
        )
        self.scores_listbox.pack(fill='both', padx=2, pady=2, expand=True)

        regles_frame = tk.LabelFrame(self.frame_droit, text="RÈGLES", bg='#2c3e50',
                                     fg='#ecf0f1', font=('Arial', 9, 'bold'))
        regles_frame.pack(fill='x', padx=5, pady=5)

        self.regles_label = tk.Label(regles_frame,
                                     text="Sélectionnez un mode",
                                     bg='#2c3e50', fg='#ecf0f1',
                                     font=('Arial', 7), wraplength=170, justify='left')
        self.regles_label.pack(pady=2, padx=2)

        last_frame = tk.LabelFrame(self.frame_droit, text="DERNIER", bg='#2c3e50',
                                   fg='#ecf0f1', font=('Arial', 8, 'bold'))
        last_frame.pack(fill='x', padx=5, pady=5)

        self.last_score = tk.Label(last_frame, text="Score: -", bg='#2c3e50',
                                  fg='#bdc3c7', font=('Arial', 7))
        self.last_score.pack(anchor='w', padx=2)

        self.last_mode = tk.Label(last_frame, text="Mode: -", bg='#2c3e50',
                                  fg='#bdc3c7', font=('Arial', 7))
        self.last_mode.pack(anchor='w', padx=2)

    def creer_barre_information(self):
        info_barre = tk.Frame(self.fenetre, bg='#34495e', height=35)
        info_barre.grid(row=2, column=0, sticky='ew', padx=5, pady=2)

        self.instruction_label = tk.Label(
            info_barre,
            text="👆 Choisissez un mode et cliquez sur LANCER",
            font=('Arial', 9),
            bg='#34495e',
            fg='#ecf0f1'
        )
        self.instruction_label.pack(side='left', padx=10)

        self.timer_label = tk.Label(
            info_barre,
            text="⏱️ 0.0s",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#f1c40f'
        )
        self.timer_label.pack(side='right', padx=10)

        self.info_cible = tk.Label(
            info_barre,
            text="",
            font=('Arial', 9, 'italic'),
            bg='#34495e',
            fg='#ffd700'
        )
        self.info_cible.pack(side='right', padx=20)

        tk.Button(info_barre, text="🏠 QUITTER", command=self.quitter,
                 bg='#e74c3c', fg='white', font=('Arial', 9),
                 padx=10).pack(side='right', padx=10)

    def afficher_regles_mode(self, *args):
        mode = self.mode_var.get()
        config = self.config_modes[mode]
        nb_cibles = len(config["cibles"])
        self.regles_label.config(text=f"{config['nom']} ({nb_cibles}):\n{config['description']}")

    def afficher_accueil(self):
        self.zone_jeu.delete("all")
        width = self.zone_jeu.winfo_width() // 2
        height = self.zone_jeu.winfo_height() // 2

        if width < 10:
            width = 400
            height = 250

        self.zone_jeu.create_text(
            width, height - 50,
            text="⌨️ KEYBOARD MASTER ⌨️",
            fill='#ffd700',
            font=('Arial', 24, 'bold'),
            tags="accueil"
        )

        self.zone_jeu.create_text(
            width, height + 20,
            text="Sélectionnez un mode :\n\n"
                 "🔤 Alphabet : A à Z et a à z (majuscules et minuscules)\n"
                 "✨ Accents : é è ê à â ô ç û ü\n"
                 "📝 Ponctuation : ! ? ; : / - . , ( )\n"
                 "⌨️ Raccourcis : Tout sélectionner, Copier, etc.\n"
                 "🌟 All Stars : Tout mélangé !\n\n"
                 "Cliquez sur LANCER",
            fill='#ecf0f1',
            font=('Arial', 11),
            justify='center',
            tags="accueil"
        )

    def dessiner_vies(self):
        self.vies_canvas.delete("all")
        largeur = self.vies_canvas.winfo_width()
        if largeur < 10:
            return
        largeur_coeur = (largeur - 10) / self.vies_max
        for i in range(self.vies_max):
            x = 5 + i * largeur_coeur + largeur_coeur/2
            couleur = '#e74c3c' if i < self.vies else '#2c3e50'
            self.vies_canvas.create_text(x, 15, text="❤️", font=('Arial', 12), fill=couleur)

    def changer_mode(self):
        self.mode_actuel = self.mode_var.get()

    def nouvelle_couleur(self):
        couleurs_disponibles = [c for c in self.palette_couleurs if c != self.derniere_couleur]
        if not couleurs_disponibles:
            couleurs_disponibles = self.palette_couleurs
        self.couleur_actuelle = random.choice(couleurs_disponibles)
        self.derniere_couleur = self.couleur_actuelle
        return self.couleur_actuelle

    def demarrer_partie(self):
        self.arreter_timers()

        self.en_jeu = True
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.niveau = 1
        self.cibles_touchees = 0
        self.cibles_ratees = 0
        self.cibles_loupees = 0
        self.temps_total = 0
        self.vies = 3
        self.vies_max = 3
        self.derniere_couleur = None
        self.attente_saisie = False
        self.sequence_accent = ""
        self.stats_touches.clear()

        self.mettre_a_jour_interface()
        self.btn_demarrer.config(text="⚡ EN JEU", bg='#e67e22', state='disabled')

        mode = self.mode_actuel
        if mode == "raccourcis":
            self.instruction_label.config(text="🎯 Tapez le raccourci demandé")
        else:
            self.instruction_label.config(text="🎯 Tapez le caractère demandé")

        self.zone_jeu.delete("all")
        self.afficher_prochain_caractere()

    def arreter_timers(self):
        for timer in ['timer_disparition_id', 'chrono_id']:
            if hasattr(self, timer) and getattr(self, timer):
                self.fenetre.after_cancel(getattr(self, timer))
                setattr(self, timer, None)

    def afficher_prochain_caractere(self):
        if not self.en_jeu or self.vies <= 0:
            if self.vies <= 0:
                self.terminer_partie()
            return

        mode_config = self.config_modes[self.mode_actuel]
        self.cible_actuelle = random.choice(mode_config["cibles"])

        couleur = self.nouvelle_couleur()

        self.zone_jeu.delete("all")
        width = self.zone_jeu.winfo_width() // 2
        height = self.zone_jeu.winfo_height() // 2

        if width < 10:
            width = 400
            height = 250

        temps_max = self.temps_par_niveau.get(self.niveau, 3.0)
        self.zone_jeu.create_text(
            width, 50,
            text=f"NIVEAU {self.niveau} | ⏱️ {temps_max:.1f}s",
            fill='#f1c40f',
            font=('Arial', 16, 'bold'),
            tags="info_niveau"
        )

        if self.mode_actuel == "raccourcis":
            if isinstance(self.cible_actuelle, dict):
                texte = self.cible_actuelle["nom"]
                self.info_cible.config(text=f"Raccourci: {self.cible_actuelle['raccourci']}")
            else:
                texte = "?"
                self.info_cible.config(text="")
        elif self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle in ["Tout sélectionner", "Copier", "Couper", "Coller", "Annuler", "Rétablir"]:
            texte = self.cible_actuelle
            raccourcis_map = {
                "Tout sélectionner": "Ctrl+A",
                "Copier": "Ctrl+C",
                "Couper": "Ctrl+X",
                "Coller": "Ctrl+V",
                "Annuler": "Ctrl+Z",
                "Rétablir": "Ctrl+Y"
            }
            self.info_cible.config(text=f"Raccourci: {raccourcis_map.get(self.cible_actuelle, '?')}")
        else:
            texte = self.cible_actuelle
            self.info_cible.config(text="")

        font_size = 48 if (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and texte in ["Tout sélectionner", "Copier", "Couper", "Coller", "Annuler", "Rétablir"])) else 72
        self.zone_jeu.create_text(
            width, height - 50,
            text=texte,
            fill=couleur,
            font=('Arial', font_size, 'bold'),
            tags="cible"
        )

        if self.mode_actuel == "raccourcis" or (self.mode_actuel == "allstars" and texte in ["Tout sélectionner", "Copier", "Couper", "Coller", "Annuler", "Rétablir"]):
            self.zone_jeu.create_text(
                width, height + 50,
                text="Tapez le raccourci correspondant",
                fill='#ecf0f1',
                font=('Arial', 14),
                tags="cible"
            )
        else:
            self.zone_jeu.create_text(
                width, height + 50,
                text="Tapez cette touche",
                fill='#ecf0f1',
                font=('Arial', 14),
                tags="cible"
            )

        self.temps_apparition = time.time()
        self.timer_disparition_id = self.fenetre.after(int(temps_max * 1000), self.temps_ecoule)
        self.mettre_a_jour_chrono()
        self.attente_saisie = True
        self.sequence_accent = ""

    def temps_ecoule(self):
        if self.en_jeu and self.cible_actuelle and self.attente_saisie:
            self.attente_saisie = False
            self.cibles_loupees += 1
            self.combo = 0
            self.vies -= 1
            self.score += self.bareme["trop_lent"]

            if isinstance(self.cible_actuelle, str):
                self.stats_touches[self.cible_actuelle]["erreurs"] += 1

            self.zone_jeu.delete("info_niveau")

            width = self.zone_jeu.winfo_width() // 2
            self.zone_jeu.create_text(
                width, 150,
                text=f"⏰ Trop lent ! {self.bareme['trop_lent']}",
                fill='#e67e22',
                font=('Arial', 16, 'bold'),
                tags="feedback"
            )
            self.fenetre.after(500, lambda: self.zone_jeu.delete("feedback"))

            self.mettre_a_jour_interface()

            if self.vies > 0:
                self.afficher_prochain_caractere()
            else:
                self.terminer_partie()

    def on_touche_pressee(self, event):
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 'Alt_L', 'Alt_R']:
            return

        if not self.en_jeu or not self.cible_actuelle or not self.attente_saisie:
            return

        touche = event.char

        if not touche:
            return

        if event.keysym in ['dead_diaeresis', 'dead_circumflex', 'dead_grave', 'dead_acute']:
            if event.keysym == 'dead_diaeresis':
                self.sequence_accent = '¨'
            elif event.keysym == 'dead_circumflex':
                self.sequence_accent = '^'
            elif event.keysym == 'dead_grave':
                self.sequence_accent = '`'
            elif event.keysym == 'dead_acute':
                self.sequence_accent = '´'
            return

        if self.sequence_accent:
            if self.sequence_accent == '¨' and touche.lower() in ['e', 'i', 'u', 'y']:
                if touche == 'e': touche = 'ë'
                elif touche == 'E': touche = 'Ë'
                elif touche == 'i': touche = 'ï'
                elif touche == 'I': touche = 'Ï'
                elif touche == 'u': touche = 'ü'
                elif touche == 'U': touche = 'Ü'
                elif touche == 'y': touche = 'ÿ'
                elif touche == 'Y': touche = 'Ÿ'
            self.sequence_accent = ""

        self.verifier_saisie(touche)

    def on_ctrl_a(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Tout sélectionner")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+A")

    def on_ctrl_c(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Copier")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+C")

    def on_ctrl_v(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Coller")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+V")

    def on_ctrl_x(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Couper")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+X")

    def on_ctrl_z(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Annuler")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+Z")

    def on_ctrl_y(self, event):
        if self.en_jeu and (self.mode_actuel == "raccourcis" or
                           (self.mode_actuel == "allstars" and isinstance(self.cible_actuelle, str) and self.cible_actuelle == "Rétablir")) and self.attente_saisie:
            self.verifier_saisie("Ctrl+Y")

    def verifier_saisie(self, saisie):
        if not self.en_jeu or not self.cible_actuelle or not self.attente_saisie:
            return

        self.attente_saisie = False

        if self.timer_disparition_id:
            self.fenetre.after_cancel(self.timer_disparition_id)
            self.timer_disparition_id = None

        temps_reaction = time.time() - self.temps_apparition
        self.temps_total += temps_reaction

        cible = self.cible_actuelle
        success = False

        if self.mode_actuel == "raccourcis":
            if isinstance(cible, dict):
                success = (saisie == cible["raccourci"])
                if success:
                    self.stats_touches[cible["nom"]]["reussites"] += 1
                else:
                    self.stats_touches[cible["nom"]]["erreurs"] += 1
        elif self.mode_actuel == "allstars" and isinstance(cible, str) and cible in ["Tout sélectionner", "Copier", "Couper", "Coller", "Annuler", "Rétablir"]:
            raccourcis_map = {
                "Tout sélectionner": "Ctrl+A",
                "Copier": "Ctrl+C",
                "Couper": "Ctrl+X",
                "Coller": "Ctrl+V",
                "Annuler": "Ctrl+Z",
                "Rétablir": "Ctrl+Y"
            }
            success = (saisie == raccourcis_map.get(cible, ""))
            if success:
                self.stats_touches[cible]["reussites"] += 1
            else:
                self.stats_touches[cible]["erreurs"] += 1
        else:
            success = (saisie == cible)
            if success:
                self.stats_touches[cible]["reussites"] += 1
            else:
                self.stats_touches[cible]["erreurs"] += 1

        if success:
            points = self.bareme["reussite"]
            points += self.combo * self.bareme["bonus_combo"]

            temps_max = self.temps_par_niveau.get(self.niveau, 3.0)
            bonus_texte = ""
            if temps_reaction < temps_max * 0.5:
                points += self.bareme["bonus_rapidite"]
                bonus_texte = "RAPIDE !"

            self.score += points
            self.cibles_touchees += 1
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)

            if self.cibles_touchees % 5 == 0 and self.niveau < 10:
                self.niveau += 1
                self.afficher_message(f"NIVEAU {self.niveau} !")

            width = self.zone_jeu.winfo_width() // 2
            self.zone_jeu.create_text(
                width, 150,
                text=f"✅ +{points}" + (f" {bonus_texte}" if bonus_texte else ""),
                fill='#2ecc71',
                font=('Arial', 18, 'bold'),
                tags="feedback"
            )
        else:
            self.score += self.bareme["erreur"]
            self.cibles_ratees += 1
            self.combo = 0
            self.vies -= 1

            width = self.zone_jeu.winfo_width() // 2
            height = self.zone_jeu.winfo_height() // 2

            erreur_aleatoire = random.choice(["❌ FAUX!", "😞", "❌"])
            flash = self.zone_jeu.create_text(
                width, height,
                text=erreur_aleatoire,
                fill='#e74c3c',
                font=('Arial', 48, 'bold'),
                tags="flash"
            )

            def animer_flash(etape=0):
                if etape < 3:
                    if etape % 2 == 0:
                        self.zone_jeu.itemconfig(flash, fill='#e74c3c', font=('Arial', 52, 'bold'))
                    else:
                        self.zone_jeu.itemconfig(flash, fill='#c0392b', font=('Arial', 48, 'bold'))
                    self.fenetre.after(100, lambda: animer_flash(etape + 1))
                else:
                    self.zone_jeu.delete(flash)
            animer_flash()

            self.zone_jeu.create_text(
                width, 150,
                text=f"{self.bareme['erreur']} pts",
                fill='#e74c3c',
                font=('Arial', 16, 'bold'),
                tags="feedback"
            )

        self.fenetre.after(500, lambda: self.zone_jeu.delete("feedback"))
        self.mettre_a_jour_interface()

        if self.vies > 0:
            self.afficher_prochain_caractere()
        else:
            self.terminer_partie()

    def afficher_message(self, texte):
        width = self.zone_jeu.winfo_width() // 2
        msg = self.zone_jeu.create_text(
            width, 100,
            text=texte,
            fill='#ffd700',
            font=('Arial', 20, 'bold'),
            tags="message"
        )
        self.fenetre.after(1500, lambda: self.zone_jeu.delete(msg))

    def mettre_a_jour_interface(self):
        self.score_label.config(text=f"{self.score}")
        self.combo_label.config(text=f"x{self.combo}")
        self.niveau_label.config(text=f"{self.niveau}")
        self.vies_label.config(text=f"{self.vies}/{self.vies_max}")
        self.dessiner_vies()

        total = self.cibles_touchees + self.cibles_ratees + self.cibles_loupees
        if total > 0:
            precision = (self.cibles_touchees / total) * 100
            self.stats_precision.config(text=f"{precision:.0f}%")

        if self.cibles_touchees > 0:
            temps_moyen = self.temps_total / self.cibles_touchees
            self.stats_temps.config(text=f"{temps_moyen:.1f}s")

        self.progress_bar.delete("all")
        width = self.progress_bar.winfo_width()
        if width > 10:
            progression = (self.cibles_touchees % 5) / 5
            self.progress_bar.create_rectangle(0, 0, width * progression, 15,
                                              fill='#3498db', outline='')

        if self.score > self.meilleur_score:
            self.meilleur_score = self.score
            self.stats_meilleur.config(text=f"{self.meilleur_score}")

    def mettre_a_jour_chrono(self):
        if self.en_jeu and self.cible_actuelle and self.attente_saisie:
            temps = time.time() - self.temps_apparition
            temps_max = self.temps_par_niveau.get(self.niveau, 3.0)
            temps_restant = max(0, temps_max - temps)

            if temps_restant < 1:
                couleur = '#e74c3c'
            elif temps_restant < 2:
                couleur = '#e67e22'
            else:
                couleur = '#f1c40f'

            self.timer_label.config(text=f"⏱️ {temps_restant:.1f}s", fg=couleur)

            width = self.zone_jeu.winfo_width() // 2
            self.zone_jeu.delete("info_niveau")
            self.zone_jeu.create_text(
                width, 50,
                text=f"NIVEAU {self.niveau} | ⏱️ {temps_restant:.1f}s",
                fill=couleur,
                font=('Arial', 16, 'bold'),
                tags="info_niveau"
            )

            self.chrono_id = self.fenetre.after(100, self.mettre_a_jour_chrono)

    def afficher_stats_touches(self):
        if not self.stats_touches:
            messagebox.showinfo("Stats", "Aucune donnée disponible. Jouez d'abord !")
            return

        stats_window = tk.Toplevel(self.fenetre)
        stats_window.title("📊 Statistiques détaillées par touche")
        stats_window.geometry("500x600")
        stats_window.configure(bg='#2c3e50')

        tk.Label(stats_window, text="STATISTIQUES PAR TOUCHE", font=('Arial', 16, 'bold'),
                bg='#2c3e50', fg='#ffd700').pack(pady=10)

        frame = tk.Frame(stats_window, bg='#2c3e50')
        frame.pack(fill='both', expand=True, padx=20, pady=10)

        touches_stats = []
        for touche, stats in self.stats_touches.items():
            total = stats["reussites"] + stats["erreurs"]
            if total > 0:
                taux_erreur = (stats["erreurs"] / total) * 100
                touches_stats.append((touche, stats["reussites"], stats["erreurs"], taux_erreur))

        touches_stats.sort(key=lambda x: x[3], reverse=True)

        tree = ttk.Treeview(frame, columns=('touche', 'reussites', 'erreurs', 'taux'), show='headings', height=20)
        tree.heading('touche', text='Touche')
        tree.heading('reussites', text='✅ Réussites')
        tree.heading('erreurs', text='❌ Erreurs')
        tree.heading('taux', text="Taux d'erreur")
        tree.column('touche', width=100)
        tree.column('reussites', width=100)
        tree.column('erreurs', width=100)
        tree.column('taux', width=100)

        for t in touches_stats[:30]:
            tree.insert('', 'end', values=(t[0], t[1], t[2], f"{t[3]:.1f}%"))

        tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(stats_window, text="Fermer", command=stats_window.destroy,
                 bg='#3498db', fg='white', font=('Arial', 12),
                 padx=20, pady=5).pack(pady=10)

    def afficher_heatmap(self):
        if not self.stats_touches:
            messagebox.showinfo("Heatmap", "Aucune donnée disponible. Jouez d'abord !")
            return

        heat_window = tk.Toplevel(self.fenetre)
        heat_window.title("🔥 Heatmap du clavier")
        heat_window.geometry("900x400")
        heat_window.configure(bg='#2c3e50')

        tk.Label(heat_window, text="🔥 HEATMAP - Touches les plus difficiles", font=('Arial', 16, 'bold'),
                bg='#2c3e50', fg='#ffd700').pack(pady=10)

        canvas_frame = tk.Frame(heat_window, bg='#2c3e50')
        canvas_frame.pack(expand=True, fill='both', padx=20, pady=10)

        canvas = tk.Canvas(canvas_frame, bg='#34495e', highlightthickness=0)
        canvas.pack(expand=True, fill='both')

        # Disposition AZERTY simplifiée
        lignes = [
            ['A', 'Z', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['Q', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],
            ['W', 'X', 'C', 'V', 'B', 'N', ',', ';', ':', '!']
        ]

        taille_touche = 50
        marge_x = 50
        marge_y = 50

        max_erreur = 1
        for stats in self.stats_touches.values():
            if stats["erreurs"] > max_erreur:
                max_erreur = stats["erreurs"]

        for i, ligne in enumerate(lignes):
            y = marge_y + i * (taille_touche + 10)
            for j, char in enumerate(ligne):
                x = marge_x + j * (taille_touche + 10)
                stats = self.stats_touches.get(char, {"erreurs": 0})
                erreurs = stats["erreurs"]
                # Calcul de l'intensité (rouge)
                if max_erreur > 0:
                    intensite = int(255 * (erreurs / max_erreur))
                else:
                    intensite = 0
                couleur = f'#{intensite:02x}{255-intensite:02x}00'
                if erreurs == 0:
                    couleur = '#2ecc71'
                canvas.create_rectangle(x, y, x+taille_touche, y+taille_touche, fill=couleur, outline='white', width=2)
                canvas.create_text(x+taille_touche//2, y+taille_touche//2, text=char, fill='white', font=('Arial', 14, 'bold'))

        tk.Button(heat_window, text="Fermer", command=heat_window.destroy,
                 bg='#e74c3c', fg='white', font=('Arial', 12),
                 padx=20, pady=5).pack(pady=10)

    def terminer_partie(self):
        self.en_jeu = False
        self.attente_saisie = False
        self.arreter_timers()

        self.btn_demarrer.config(text="🚀 LANCER", bg='#27ae60', state='normal')
        self.instruction_label.config(text="👆 Cliquez sur LANCER pour rejouer")
        self.timer_label.config(text="⏱️ 0.0s")
        self.info_cible.config(text="")

        self.zone_jeu.delete("info_niveau")

        total = self.cibles_touchees + self.cibles_ratees + self.cibles_loupees
        precision = (self.cibles_touchees / total * 100) if total > 0 else 0

        score_final = self.score
        record_texte = "🏆 RECORD !" if score_final > self.meilleur_score else ""
        if score_final > self.meilleur_score:
            self.meilleur_score = score_final

        mode_nom = self.config_modes[self.mode_actuel]["nom"]
        self.last_score.config(text=f"Score: {score_final}")
        self.last_mode.config(text=f"Mode: {mode_nom}")

        self.zone_jeu.delete("all")
        width = self.zone_jeu.winfo_width() // 2
        height = self.zone_jeu.winfo_height() // 2

        if width < 10:
            width = 400
            height = 250

        y = height - 80
        self.zone_jeu.create_text(
            width, y,
            text="PARTIE TERMINÉE",
            fill='#ffd700',
            font=('Arial', 20, 'bold'),
            tags="resume"
        )

        if record_texte:
            self.zone_jeu.create_text(
                width, y + 35,
                text=record_texte,
                fill='#f1c40f',
                font=('Arial', 14, 'bold'),
                tags="resume"
            )

        stats = [
            f"Mode: {mode_nom}",
            f"Score: {score_final}",
            f"Niveau final: {self.niveau}",
            f"Précision: {precision:.0f}%",
            f"Combo max: x{self.max_combo}",
            f"Réussites: {self.cibles_touchees}",
            f"Erreurs: {self.cibles_ratees + self.cibles_loupees}"
        ]

        for i, stat in enumerate(stats):
            self.zone_jeu.create_text(
                width, y + 75 + i*22,
                text=stat,
                fill='#ecf0f1',
                font=('Arial', 11),
                tags="resume"
            )

        self.sauvegarder_score()
        self.mettre_a_jour_tableau_scores()
        self.sauvegarder_statistiques()

        if self.parent.profil_actuel in self.parent.profils:
            stats = self.parent.profils[self.parent.profil_actuel].get("stats_clavier", {"reussites": 0, "erreurs": 0, "touches": {}})
            stats["reussites"] = stats.get("reussites", 0) + self.cibles_touchees
            stats["erreurs"] = stats.get("erreurs", 0) + self.cibles_ratees + self.cibles_loupees
            for t, s in self.stats_touches.items():
                if t not in stats["touches"]:
                    stats["touches"][t] = {"reussites": 0, "erreurs": 0}
                stats["touches"][t]["reussites"] += s["reussites"]
                stats["touches"][t]["erreurs"] += s["erreurs"]
            self.parent.profils[self.parent.profil_actuel]["stats_clavier"] = stats
            self.parent.sauvegarder_tous_profils()

        xp_gagne = max(10, score_final // 10 + self.max_combo * 5)
        self.parent.ajouter_experience(xp_gagne)

        self.parent.verifier_succes({
            "partie_terminee": True,
            "max_combo": self.max_combo,
            "score": score_final,
            "module": "Keyboard Master",
            "perfect_clavier": self.cibles_touchees >= 20 and (self.cibles_ratees + self.cibles_loupees) == 0
        })
        self.parent.verifier_badges({
            "keyboard_niveau": self.niveau,
            "max_combo": self.max_combo
        })

    def mettre_a_jour_tableau_scores(self):
        self.scores_listbox.delete(0, tk.END)
        try:
            if os.path.exists("scores_clavier.json"):
                with open("scores_clavier.json", "r") as f:
                    scores = json.load(f)
                for i, score in enumerate(scores[:8], 1):
                    medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else "•"
                    self.scores_listbox.insert(tk.END, f"{medal} {score['score']} pts - {score['mode']}")
        except:
            self.scores_listbox.insert(tk.END, "Aucun score")

    def sauvegarder_score(self):
        try:
            scores = []
            if os.path.exists("scores_clavier.json"):
                with open("scores_clavier.json", "r") as f:
                    scores = json.load(f)
            mode_nom = self.config_modes[self.mode_actuel]["nom"]
            scores.append({
                "score": self.score,
                "mode": mode_nom,
                "niveau": self.niveau,
                "combo": self.max_combo,
                "date": datetime.now().strftime("%d/%m/%Y")
            })
            scores.sort(key=lambda x: x["score"], reverse=True)
            scores = scores[:15]
            with open("scores_clavier.json", "w") as f:
                json.dump(scores, f, indent=2)
        except:
            pass

    def sauvegarder_statistiques(self):
        try:
            stats = {
                "meilleur_score": self.meilleur_score,
                "parties_jouees": self.parties_jouees + 1,
                "max_combo": self.max_combo
            }
            with open("stats_clavier.json", "w") as f:
                json.dump(stats, f)
            self.parties_jouees += 1
        except:
            pass

    def charger_statistiques(self):
        try:
            if os.path.exists("stats_clavier.json"):
                with open("stats_clavier.json", "r") as f:
                    stats = json.load(f)
                    self.meilleur_score = stats.get("meilleur_score", 0)
                    self.parties_jouees = stats.get("parties_jouees", 0)
                    self.max_combo = stats.get("max_combo", 0)
        except:
            pass

    def quitter(self):
        self.fenetre.destroy()
        self.parent.fenetre.deiconify()
        self.parent.afficher_accueil()
        self.parent.fenetre.state('zoomed')

    def demarrer(self):
        self.afficher_regles_mode()
        self.fenetre.protocol("WM_DELETE_WINDOW", self.quitter)
        self.fenetre.focus_set()
        self.fenetre.mainloop()


# ============================================================
# MODULE ATELIER SOURIS
# ============================================================

class AtelierSourisModule:
    def __init__(self, parent):
        self.parent = parent
        self.fenetre = tk.Toplevel(parent.fenetre)
        self.fenetre.title("🐭 ATELIER SOURIS")
        self.fenetre.geometry("1200x800")
        self.fenetre.configure(bg='#1a2634')
        self.fenetre.state('zoomed')
        self.fenetre.bind('<F11>', lambda e: self.parent.toggle_fullscreen(e))

        self.exercice_actuel = None
        self.en_jeu = False
        self.score = 0
        self.cibles_restantes = 0
        self.reussites = 0
        self.erreurs = 0
        self.temps_debut = 0
        self.chrono_id = None

        self.creer_interface()

    def creer_interface(self):
        barre = tk.Frame(self.fenetre, bg='#2c3e50', height=60)
        barre.pack(fill='x')

        self.titre_label = tk.Label(barre, text="🐭 ATELIER SOURIS",
                                    font=('Arial', 18, 'bold'),
                                    bg='#2c3e50', fg='#ffd700')
        self.titre_label.pack(side='left', padx=20)

        self.score_label = tk.Label(barre, text="Score: 0", font=('Arial', 14),
                                    bg='#2c3e50', fg='#2ecc71')
        self.score_label.pack(side='left', padx=20)

        self.chrono_label = tk.Label(barre, text="⏱️ 0.0s", font=('Arial', 14),
                                     bg='#2c3e50', fg='#f1c40f')
        self.chrono_label.pack(side='right', padx=20)

        main_frame = tk.Frame(self.fenetre, bg='#1a2634')
        main_frame.pack(expand=True, fill='both', padx=10, pady=10)

        menu_frame = tk.Frame(main_frame, bg='#2c3e50', width=250)
        menu_frame.pack(side='left', fill='y', padx=(0, 10))
        menu_frame.pack_propagate(False)

        tk.Label(menu_frame, text="📋 EXERCICES", font=('Arial', 14, 'bold'),
                bg='#2c3e50', fg='#ecf0f1').pack(pady=15)

        exercices = [
            ("🖱️ Clic Gauche", self.exercice_clic_gauche),
            ("🖱️ Clic Droit", self.exercice_clic_droit),
            ("🖱️ Double Clic", self.exercice_double_clic),
            ("✋ Glisser-Déposer", self.exercice_glisser_deposer),
        ]

        for texte, commande in exercices:
            btn = tk.Button(menu_frame, text=texte, command=commande,
                          bg='#3498db', fg='white', font=('Arial', 12),
                          padx=20, pady=10, relief='flat', width=20)
            btn.pack(pady=5)

        zone_frame = tk.Frame(main_frame, bg='#ecf0f1', relief='sunken', bd=3)
        zone_frame.pack(side='right', expand=True, fill='both')

        self.zone_exercice = tk.Canvas(zone_frame, bg='white', highlightthickness=0)
        self.zone_exercice.pack(expand=True, fill='both', padx=10, pady=10)

        self.instruction_label = tk.Label(self.fenetre, text="Choisissez un exercice",
                                         font=('Arial', 12), bg='#34495e', fg='#ecf0f1',
                                         height=2)
        self.instruction_label.pack(fill='x', side='bottom')

        tk.Button(self.fenetre, text="🏠 QUITTER", command=self.quitter,
                 bg='#e74c3c', fg='white', font=('Arial', 12),
                 padx=30, pady=5).pack(side='bottom', pady=5)

        self.zone_exercice.bind('<Button-1>', self.on_clic_gauche)
        self.zone_exercice.bind('<Button-3>', self.on_clic_droit)
        self.zone_exercice.bind('<Double-Button-1>', self.on_double_clic)

    def reset_exercice(self):
        self.zone_exercice.delete("all")
        self.en_jeu = True
        self.score = 0
        self.reussites = 0
        self.erreurs = 0
        self.score_label.config(text="Score: 0")
        self.chrono_label.config(text="⏱️ 0.0s")
        self.temps_debut = time.time()
        self.mettre_a_jour_chrono()

    def mettre_a_jour_chrono(self):
        if self.en_jeu:
            temps_ecoule = time.time() - self.temps_debut
            self.chrono_label.config(text=f"⏱️ {temps_ecoule:.1f}s")
            self.chrono_id = self.fenetre.after(100, self.mettre_a_jour_chrono)

    def exercice_clic_gauche(self):
        self.reset_exercice()
        self.exercice_actuel = "clic_gauche"
        self.cibles_restantes = 10
        self.instruction_label.config(text="🖱️ Cliquez GAUCHE sur les carrés bleus !")

        for i in range(10):
            x = random.randint(50, 750)
            y = random.randint(50, 450)
            self.zone_exercice.create_rectangle(
                x-20, y-20, x+20, y+20,
                fill='#3498db', outline='#2980b9', width=2,
                tags=f"cible_{i}"
            )

    def exercice_clic_droit(self):
        self.reset_exercice()
        self.exercice_actuel = "clic_droit"
        self.cibles_restantes = 10
        self.instruction_label.config(text="🖱️ Cliquez DROIT sur les cercles rouges !")

        for i in range(10):
            x = random.randint(50, 750)
            y = random.randint(50, 450)
            self.zone_exercice.create_oval(
                x-20, y-20, x+20, y+20,
                fill='#e74c3c', outline='#c0392b', width=2,
                tags=f"cible_{i}"
            )

    def exercice_double_clic(self):
        self.reset_exercice()
        self.exercice_actuel = "double_clic"
        self.cibles_restantes = 8
        self.instruction_label.config(text="🖱️ DOUBLE-CLIQUEZ sur les étoiles jaunes !")

        for i in range(8):
            x = random.randint(50, 750)
            y = random.randint(50, 450)
            points = []
            for angle in range(0, 360, 72):
                rad = math.radians(angle)
                px = x + 25 * math.cos(rad)
                py = y + 25 * math.sin(rad)
                points.extend([px, py])
                rad2 = math.radians(angle + 36)
                px2 = x + 10 * math.cos(rad2)
                py2 = y + 10 * math.sin(rad2)
                points.extend([px2, py2])
            self.zone_exercice.create_polygon(points, fill='#f1c40f', outline='#f39c12', width=2, tags=f"cible_{i}")

    def exercice_glisser_deposer(self):
        self.reset_exercice()
        self.exercice_actuel = "glisser_deposer"
        self.objets_deposes = 0
        self.drag_active = False
        self.objet_drag = None
        self.instruction_label.config(text="✋ Glissez les cercles dans la zone verte !")

        self.zone_exercice.create_rectangle(
            500, 300, 700, 400,
            fill='#27ae60', outline='#229954', width=3,
            tags="zone_depot"
        )
        self.zone_exercice.create_text(600, 350, text="DÉPOSEZ ICI",
                                      fill='white', font=('Arial', 14, 'bold'))

        couleurs = ['#3498db', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c']
        for i in range(5):
            x = 100 + i * 80
            y = 150
            self.zone_exercice.create_oval(
                x-25, y-25, x+25, y+25,
                fill=couleurs[i], outline='#2c3e50', width=2,
                tags=f"drag_{i}"
            )

        self.zone_exercice.bind('<B1-Motion>', self.on_glisser)
        self.zone_exercice.bind('<ButtonRelease-1>', self.on_relacher)

    def on_clic_gauche(self, event):
        if self.exercice_actuel == "clic_gauche" and self.en_jeu:
            items = self.zone_exercice.find_overlapping(event.x-5, event.y-5,
                                                        event.x+5, event.y+5)
            for item in items:
                tags = self.zone_exercice.gettags(item)
                if tags and "cible" in tags[0]:
                    self.zone_exercice.delete(item)
                    self.cibles_restantes -= 1
                    self.score += 10
                    self.reussites += 1
                    self.score_label.config(text=f"Score: {self.score}")

                    if self.cibles_restantes == 0:
                        self.terminer_exercice(True)
                    break

        elif self.exercice_actuel == "glisser_deposer" and self.en_jeu:
            items = self.zone_exercice.find_overlapping(event.x-5, event.y-5,
                                                        event.x+5, event.y+5)
            for item in items:
                tags = self.zone_exercice.gettags(item)
                if tags and "drag" in tags[0]:
                    self.drag_active = True
                    self.objet_drag = item
                    self.drag_x = event.x
                    self.drag_y = event.y
                    break

    def on_clic_droit(self, event):
        if self.exercice_actuel == "clic_droit" and self.en_jeu:
            items = self.zone_exercice.find_overlapping(event.x-5, event.y-5,
                                                        event.x+5, event.y+5)
            for item in items:
                tags = self.zone_exercice.gettags(item)
                if tags and "cible" in tags[0]:
                    self.zone_exercice.delete(item)
                    self.cibles_restantes -= 1
                    self.score += 10
                    self.reussites += 1
                    self.score_label.config(text=f"Score: {self.score}")

                    if self.cibles_restantes == 0:
                        self.terminer_exercice(True)
                    break

    def on_double_clic(self, event):
        if self.exercice_actuel == "double_clic" and self.en_jeu:
            items = self.zone_exercice.find_overlapping(event.x-5, event.y-5,
                                                        event.x+5, event.y+5)
            for item in items:
                tags = self.zone_exercice.gettags(item)
                if tags and "cible" in tags[0]:
                    self.zone_exercice.delete(item)
                    self.cibles_restantes -= 1
                    self.score += 15
                    self.reussites += 1
                    self.score_label.config(text=f"Score: {self.score}")

                    if self.cibles_restantes == 0:
                        self.terminer_exercice(True)
                    break

    def on_glisser(self, event):
        if self.drag_active and self.objet_drag:
            dx = event.x - self.drag_x
            dy = event.y - self.drag_y
            self.zone_exercice.move(self.objet_drag, dx, dy)
            self.drag_x = event.x
            self.drag_y = event.y

    def on_relacher(self, event):
        if self.drag_active and self.exercice_actuel == "glisser_deposer":
            zone_coords = self.zone_exercice.coords("zone_depot")

            if (zone_coords and zone_coords[0] < event.x < zone_coords[2] and
                zone_coords[1] < event.y < zone_coords[3]):
                self.zone_exercice.delete(self.objet_drag)
                self.objets_deposes += 1
                self.score += 20
                self.reussites += 1
                self.score_label.config(text=f"Score: {self.score}")

                if self.objets_deposes == 5:
                    self.terminer_exercice(True)

        self.drag_active = False
        self.objet_drag = None

    def terminer_exercice(self, success=True):
        self.en_jeu = False
        if self.chrono_id:
            self.fenetre.after_cancel(self.chrono_id)

        temps_total = time.time() - self.temps_debut

        if success:
            xp_gagne = self.score
            self.parent.ajouter_experience(xp_gagne)

            if self.parent.profil_actuel in self.parent.profils:
                stats = self.parent.profils[self.parent.profil_actuel].get("stats_souris", {"reussites": 0, "erreurs": 0})
                stats["reussites"] += self.reussites
                stats["erreurs"] += self.erreurs
                self.parent.profils[self.parent.profil_actuel]["stats_souris"] = stats
                self.parent.sauvegarder_tous_profils()

            self.parent.verifier_succes({
                "partie_terminee": True,
                "module": "Atelier Souris"
            })

            # Vérifier les badges
            if self.exercice_actuel == "clic_gauche" and self.reussites == 10 and self.erreurs == 0:
                self.parent.verifier_badges({"clic_gauche_perfect": True})
            elif self.exercice_actuel == "clic_droit" and self.reussites == 10 and self.erreurs == 0:
                self.parent.verifier_badges({"clic_droit_perfect": True})
            elif self.exercice_actuel == "double_clic" and self.reussites == 8 and self.erreurs == 0:
                self.parent.verifier_badges({"double_clic_perfect": True})
            elif self.exercice_actuel == "glisser_deposer" and self.objets_deposes == 5 and self.erreurs == 0:
                self.parent.verifier_badges({"glisser_deposer_perfect": True})

            self.zone_exercice.create_text(
                400, 250,
                text=f"🎉 EXERCICE RÉUSSI ! 🎉\n\nScore: {self.score}\nTemps: {temps_total:.1f}s\nXP gagné: +{xp_gagne}",
                fill='#27ae60',
                font=('Arial', 16, 'bold'),
                justify='center'
            )

    def quitter(self):
        self.fenetre.destroy()
        self.parent.fenetre.deiconify()
        self.parent.afficher_accueil()
        self.parent.fenetre.state('zoomed')

    def demarrer(self):
        self.fenetre.protocol("WM_DELETE_WINDOW", self.quitter)
        self.fenetre.mainloop()


# ============================================================
# MODULE DACTYLO
# ============================================================

class DactyloModule:
    def __init__(self, parent):
        self.parent = parent
        self.fenetre = tk.Toplevel(parent.fenetre)
        self.fenetre.title("📝 DACTYLO - Maîtrise du clavier")
        self.fenetre.geometry("1200x800")
        self.fenetre.configure(bg='#1a2634')
        self.fenetre.state('zoomed')
        self.fenetre.bind('<F11>', lambda e: self.parent.toggle_fullscreen(e))

        self.texte_reference = "Maître Corbeau, sur un arbre perché, tenait en son bec un fromage. Maître Renard, par l'odeur alléché, lui tint à peu près ce langage : Et bonjour, Monsieur du Corbeau. Que vous êtes joli ! que vous me semblez beau !"
        self.texte_saisi = ""
        self.en_jeu = False
        self.debut_temps = None
        self.wpm = 0
        self.precision = 100
        self.erreurs = 0
        self.caracteres_tapes = 0
        self.erreurs_par_caractere = Counter()

        self.creer_interface()

    def creer_interface(self):
        titre = tk.Label(self.fenetre, text="📝 DACTYLO - La Fontaine", font=('Arial', 22, 'bold'),
                        bg='#1a2634', fg='#ffd700')
        titre.pack(pady=20)

        self.texte_ref_frame = tk.Frame(self.fenetre, bg='#2c3e50')
        self.texte_ref_frame.pack(fill='x', padx=50, pady=10)

        self.texte_ref = tk.Text(self.texte_ref_frame, height=4, font=('Courier', 14),
                                bg='#2c3e50', fg='#ecf0f1', wrap='word', state='disabled')
        self.texte_ref.pack(fill='x', padx=10, pady=10)
        self.texte_ref.insert('1.0', self.texte_reference)
        self.texte_ref.config(state='disabled')

        self.entry_frame = tk.Frame(self.fenetre, bg='#1a2634')
        self.entry_frame.pack(fill='x', padx=50, pady=20)

        tk.Label(self.entry_frame, text="Votre saisie :", font=('Arial', 14),
                bg='#1a2634', fg='#3498db').pack(anchor='w')

        self.entry_text = tk.Text(self.entry_frame, height=4, font=('Courier', 14),
                                 bg='#2c3e50', fg='white', insertbackground='white',
                                 wrap='word')
        self.entry_text.pack(fill='x', pady=5)
        self.entry_text.bind('<KeyRelease>', self.on_text_change)
        self.entry_text.bind('<Return>', self.on_enter)

        stats_frame = tk.Frame(self.fenetre, bg='#2c3e50')
        stats_frame.pack(fill='x', padx=50, pady=10)

        self.wpm_label = tk.Label(stats_frame, text="WPM: 0", font=('Arial', 16, 'bold'),
                                 bg='#2c3e50', fg='#f1c40f')
        self.wpm_label.pack(side='left', padx=30)

        self.precision_label = tk.Label(stats_frame, text="Précision: 100%", font=('Arial', 16, 'bold'),
                                       bg='#2c3e50', fg='#2ecc71')
        self.precision_label.pack(side='left', padx=30)

        self.temps_label = tk.Label(stats_frame, text="Temps: 0.0s", font=('Arial', 16, 'bold'),
                                   bg='#2c3e50', fg='#3498db')
        self.temps_label.pack(side='left', padx=30)

        btn_frame = tk.Frame(self.fenetre, bg='#1a2634')
        btn_frame.pack(pady=20)

        self.btn_demarrer = tk.Button(btn_frame, text="🚀 DÉMARRER", command=self.demarrer_exercice,
                                     bg='#27ae60', fg='white', font=('Arial', 14, 'bold'),
                                     padx=30, pady=10)
        self.btn_demarrer.pack(side='left', padx=10)

        tk.Button(btn_frame, text="🏠 QUITTER", command=self.quitter,
                 bg='#e74c3c', fg='white', font=('Arial', 14),
                 padx=30, pady=10).pack(side='left', padx=10)

    def demarrer_exercice(self):
        self.en_jeu = True
        self.texte_saisi = ""
        self.debut_temps = time.time()
        self.erreurs = 0
        self.caracteres_tapes = 0
        self.erreurs_par_caractere.clear()

        self.entry_text.delete('1.0', tk.END)
        self.entry_text.focus_set()

        self.btn_demarrer.config(text="⚡ EN COURS", bg='#e67e22', state='disabled')

        self.mettre_a_jour_chrono()
        self.update_reference_display()

    def on_text_change(self, event=None):
        if not self.en_jeu:
            return

        contenu = self.entry_text.get('1.0', 'end-1c')
        self.texte_saisi = contenu

        self.caracteres_tapes = len(contenu)
        self.erreurs = 0
        self.erreurs_par_caractere.clear()

        min_len = min(len(contenu), len(self.texte_reference))
        for i in range(min_len):
            if contenu[i] != self.texte_reference[i]:
                self.erreurs += 1
                self.erreurs_par_caractere[self.texte_reference[i]] += 1

        if len(contenu) > len(self.texte_reference):
            self.erreurs += len(contenu) - len(self.texte_reference)

        if self.caracteres_tapes > 0:
            self.precision = ((self.caracteres_tapes - self.erreurs) / self.caracteres_tapes) * 100
            self.precision_label.config(text=f"Précision: {self.precision:.1f}%")

        self.update_reference_display()

    def on_enter(self, event=None):
        if self.en_jeu:
            self.terminer_exercice()
        return 'break'

    def update_reference_display(self):
        self.texte_ref.config(state='normal')
        self.texte_ref.delete('1.0', tk.END)

        typed = self.texte_saisi
        for i, char in enumerate(self.texte_reference):
            if i < len(typed):
                if typed[i] == char:
                    self.texte_ref.insert(tk.END, char, 'correct')
                else:
                    self.texte_ref.insert(tk.END, char, 'incorrect')
            else:
                self.texte_ref.insert(tk.END, char, 'pending')

        self.texte_ref.tag_config('correct', foreground='#2ecc71')
        self.texte_ref.tag_config('incorrect', foreground='#e74c3c', background='#5a2a2a')
        self.texte_ref.tag_config('pending', foreground='#7f8c8d')
        self.texte_ref.config(state='disabled')

    def mettre_a_jour_chrono(self):
        if self.en_jeu:
            temps_ecoule = time.time() - self.debut_temps
            self.temps_label.config(text=f"Temps: {temps_ecoule:.1f}s")

            minutes = temps_ecoule / 60
            mots = len(self.texte_saisi.split())
            if minutes > 0:
                self.wpm = int(mots / minutes)
                self.wpm_label.config(text=f"WPM: {self.wpm}")

            self.fenetre.after(200, self.mettre_a_jour_chrono)

    def terminer_exercice(self):
        self.en_jeu = False
        self.btn_demarrer.config(text="🚀 DÉMARRER", bg='#27ae60', state='normal')

        temps_total = time.time() - self.debut_temps
        mots = len(self.texte_saisi.split())
        wpm_final = int(mots / (temps_total / 60)) if temps_total > 0 else 0

        xp_gagne = int(wpm_final * 2 + self.precision)
        self.parent.ajouter_experience(xp_gagne)
        self.parent.sauvegarder_score("Dactylo", wpm_final * 100, 1, 0, {"wpm": wpm_final, "precision": self.precision})

        self.parent.verifier_succes({
            "partie_terminee": True,
            "module": "Dactylo"
        })
        self.parent.verifier_badges({
            "wpm": wpm_final
        })

        resultat = f"🏁 EXERCICE TERMINÉ ! 🏁\n\n"
        resultat += f"WPM: {wpm_final}\n"
        resultat += f"Précision: {self.precision:.1f}%\n"
        resultat += f"Temps: {temps_total:.1f} secondes\n"
        resultat += f"Caractères tapés: {self.caracteres_tapes}\n"
        resultat += f"Erreurs: {self.erreurs}\n"
        resultat += f"XP gagné: +{xp_gagne}\n\n"

        if self.erreurs_par_caractere:
            resultat += "Caractères problématiques:\n"
            for char, count in self.erreurs_par_caractere.most_common(5):
                resultat += f"  '{char}': {count} erreur(s)\n"

        messagebox.showinfo("Résultats", resultat)

    def quitter(self):
        self.fenetre.destroy()
        self.parent.fenetre.deiconify()
        self.parent.afficher_accueil()
        self.parent.fenetre.state('zoomed')

    def demarrer(self):
        self.fenetre.protocol("WM_DELETE_WINDOW", self.quitter)
        self.fenetre.mainloop()


# ============================================================
# LANCEMENT
# ============================================================

if __name__ == "__main__":
    app = CentreEvaluation()
    app.demarrer()