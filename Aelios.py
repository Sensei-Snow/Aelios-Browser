from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QToolBar, QPushButton, QTabWidget, QWidget, QVBoxLayout, QMenu, QAction, QFileDialog, QShortcut
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtNetwork import QNetworkProxy
import subprocess
import os
import tempfile
import platform
import sys

class CustomWebEngineView(QWebEngineView):
    def __init__(self):
        super().__init__()

        self.setContextMenuPolicy(Qt.DefaultContextMenu)

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)

        back_action = QAction(QIcon("assets/back_white.png"), "Retour", self)
        back_action.triggered.connect(self.back)
        context_menu.addAction(back_action)

        forward_action = QAction(QIcon("assets/forward_white.png"), "Avancer", self)
        forward_action.triggered.connect(self.forward)
        context_menu.addAction(forward_action)

        reload_action = QAction(QIcon("assets/reload_white.png"), "Actualiser", self)
        reload_action.triggered.connect(self.reload)
        context_menu.addAction(reload_action)

        copy_url_action = QAction(QIcon("assets/copy_link.png"), "Copier l'URL", self)
        copy_url_action.triggered.connect(lambda: QApplication.clipboard().setText(self.url().toString()))
        context_menu.addAction(copy_url_action)

        print_action = QAction(QIcon("assets/pdf.png"), "Enregistrer en PDF", self)
        print_action.triggered.connect(self.print_page)
        context_menu.addAction(print_action)

        view_source_action = QAction(QIcon("assets/source.png"), "Voir le code source", self)
        view_source_action.triggered.connect(self.view_page_source)
        context_menu.addAction(view_source_action)

        context_menu.setStyleSheet("""
                    QMenu {
                        background-color: #56585d;
                        border: 2px solid #d58e02;
                        color: white;
                    }
                    
                    QMenu::item {
                        background-color: transparent;
                        padding: 8px 25px;
                    }
                    
                    QMenu::item:selected {
                        background-color: #797c83;
                    }
                    
                    QMenu::icon {
                        padding-left: 10px;
                    }
                """)

        context_menu.exec_(event.globalPos())

    def view_page_source(self):
        self.page().toHtml(self.save_and_open_in_notepad)

    def save_and_open_in_notepad(self, html):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html", mode="w", encoding="utf-8")
        temp_file.write(html)
        temp_file.close()

        system = platform.system()

        try:
            if system == "Windows":
                subprocess.Popen(["notepad.exe", temp_file.name])
            elif system == "Linux":
                subprocess.Popen(["xdg-open", temp_file.name])
            elif system == "Darwin":  # macOS (juste au cas où)
                subprocess.Popen(["open", temp_file.name])
            else:
                print("[ERROR] -- System not supported")
        except Exception as e:
            print(f"[ERROR] -- Error during opening the file : {e}")

    def print_page(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer sous", "", "Fichiers PDF (*.pdf);;Tous les fichiers (*)", options=options
        )

        if file_path:
            self.page().printToPdf(file_path)


class Navigateur(QMainWindow):
    def __init__(self):
        super().__init__()

        global tor_status
        tor_status = False

        self.browser = CustomWebEngineView()

        profile = QWebEngineProfile.defaultProfile()
        profile.setHttpUserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36")

        # --------------------------------------------------------------Onglets (QTabWidget)
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setMovable(False)
        self.tabs.currentChanged.connect(self.update_nav_buttons)

        # --------------------------------------------------------------Tool Bar
        self.toolbar = QToolBar()
        self.toolbar.setFixedHeight(45)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.addToolBar(self.toolbar)
        self.toolbar.setContextMenuPolicy(Qt.PreventContextMenu)

        # -------------------------------------------------------------Boutons avec icônes
        self.home_button = QPushButton()
        self.home_button.setIcon(QIcon("assets/home.png"))
        self.home_button.clicked.connect(self.go_home)
        shortcut_home = QShortcut(QKeySequence("Ctrl+A"), self)
        shortcut_home.activated.connect(self.home_button.click)

        self.back_button = QPushButton()
        self.back_button.setIcon(QIcon("assets/back.png"))
        self.back_button.clicked.connect(lambda: self.get_current_browser().back())
        shortcut_back = QShortcut(QKeySequence("Ctrl+Z"), self)
        shortcut_back.activated.connect(self.back_button.click)

        self.forward_button = QPushButton()
        self.forward_button.setIcon(QIcon("assets/forward.png"))
        self.forward_button.clicked.connect(lambda: self.get_current_browser().forward())
        shortcut_forward = QShortcut(QKeySequence("Ctrl+E"), self)
        shortcut_forward.activated.connect(self.forward_button.click)

        self.reload_button = QPushButton()
        self.reload_button.setIcon(QIcon("assets/reload.png"))
        self.reload_button.clicked.connect(lambda: self.get_current_browser().reload())
        shortcut_reload = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_reload.activated.connect(self.reload_button.click)

        self.new_tab_button = QPushButton()
        self.new_tab_button.setIcon(QIcon("assets/tab.png"))
        self.new_tab_button.clicked.connect(lambda: self.add_new_tab(QUrl("file:///assets/home.html"), "Nouvel Onglet"))
        shortcut_add_tab = QShortcut(QKeySequence("Ctrl+T"), self)
        shortcut_add_tab.activated.connect(self.new_tab_button.click)
        shortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        shortcut.activated.connect(self.close_current_tab)
        next_tab_shortcut = QShortcut(QKeySequence("Ctrl+Tab"), self)
        next_tab_shortcut.activated.connect(self.next_tab)
        prev_tab_shortcut = QShortcut(QKeySequence("Ctrl+Shift+Tab"), self)
        prev_tab_shortcut.activated.connect(self.prev_tab)

        self.wikipedia_button = QPushButton()
        self.wikipedia_button.setIcon(QIcon("assets/wikipedia.png"))
        self.wikipedia_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://wikipedia.org"), "Wikipédia"))
        shortcut_wikipedia = QShortcut(QKeySequence("Ctrl+&"), self)
        shortcut_wikipedia.activated.connect(self.wikipedia_button.click)

        self.youtube_button = QPushButton()
        self.youtube_button.setIcon(QIcon("assets/youtube.png"))
        self.youtube_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://youtube.com"), "Youtube"))
        shortcut_youtube = QShortcut(QKeySequence("Ctrl+é"), self)
        shortcut_youtube.activated.connect(self.youtube_button.click)

        self.gmaps_button = QPushButton()
        self.gmaps_button.setIcon(QIcon("assets/gmaps.png"))
        self.gmaps_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://www.google.com/maps"), "Google Maps"))
        shortcut_gmaps = QShortcut(QKeySequence("Ctrl+\""), self)
        shortcut_gmaps.activated.connect(self.gmaps_button.click)

        self.amazon_button = QPushButton()
        self.amazon_button.setIcon(QIcon("assets/amazon.png"))
        self.amazon_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://amazon.com"), "Amazon"))
        shortcut_amazon = QShortcut(QKeySequence("Ctrl+'"), self)
        shortcut_amazon.activated.connect(self.amazon_button.click)

        self.canva_button = QPushButton()
        self.canva_button.setIcon(QIcon("assets/canva.png"))
        self.canva_button.clicked.connect(lambda: self.add_new_tab(QUrl("https://canva.com"), "Canva"))
        shortcut_canva = QShortcut(QKeySequence("Ctrl+("), self)
        shortcut_canva.activated.connect(self.canva_button.click)

        self.tor_button = QPushButton()
        self.tor_button.setIcon(QIcon("assets/tor_disable.png"))
        self.tor_button.clicked.connect(self.enable_disable_tor)
        shortcut_tor = QShortcut(QKeySequence("Ctrl+U"), self)
        shortcut_tor.activated.connect(self.tor_button.click)

        # -------------------------------------------------------------Espaces
        self.left_space = QWidget()
        self.left_space.setFixedWidth(35)

        self.right_space = QWidget()
        self.right_space.setFixedWidth(35)

        self.bookmarks_space = QWidget()
        self.bookmarks_space.setFixedWidth(35)

        self.tor_space = QWidget()
        self.tor_space.setFixedWidth(32)

        # -------------------------------------------------------------Style du reste de la fenêtre
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #38393c;
                    }
                """)

        # -------------------------------------------------------------URL Bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Entrez une URL ou recherchez sur le Web...")
        self.url_bar.returnPressed.connect(self.load_url)
        self.url_bar.setFixedWidth(600)
        self.url_bar.setFixedHeight(30)

        self.url_bar.setStyleSheet("""
                    QLineEdit {
                        border: 2px solid #d58e02;
                        border-radius: 10px;
                        padding: 5px 10px;
                        font-size: 12px;
                        background-color: #ecf0f1;
                        color: #2c3e50;
                    }
                    QLineEdit:focus {
                        border: 2px solid #c78501;
                        background-color: white;
                    }
                """)

        # --------------------------------------------------------------Ajouter les widgets à la toolbar
        self.toolbar.addWidget(self.home_button)
        self.toolbar.addWidget(self.back_button)
        self.toolbar.addWidget(self.forward_button)
        self.toolbar.addWidget(self.reload_button)

        self.toolbar.addWidget(self.left_space)
        self.toolbar.addWidget(self.url_bar)
        self.toolbar.addWidget(self.right_space)

        self.toolbar.addWidget(self.new_tab_button)

        self.toolbar.addWidget(self.bookmarks_space)
        self.toolbar.addWidget(self.wikipedia_button)
        self.toolbar.addWidget(self.youtube_button)
        self.toolbar.addWidget(self.gmaps_button)
        self.toolbar.addWidget(self.amazon_button)
        self.toolbar.addWidget(self.canva_button)

        self.toolbar.addWidget(self.tor_space)
        self.toolbar.addWidget(self.tor_button)

        self.setCentralWidget(self.tabs)

        self.toolbar.setStyleSheet("""
                    QToolBar {
                        background-color: #415b76;
                        background-image: url('assets/logo_final.png');
                        background-repeat: no-repeat;
                        background-position: right bottom;
                        border: none;
                        padding: 5px;
                    }

                    QToolBar QPushButton {
                        background-color: #56789c;
                        border-radius: 5px;
                        padding: 6px;
                        margin: 0 4px;
                    }

                    QToolBar QPushButton:hover {
                        background-color: #d58e02;
                    }

                    QToolBar QPushButton:pressed {
                        background-color: #a26b01;
                    }
                """)

        # -------------------------------------------------------------Ouvrir un premier onglet
        self.add_new_tab(QUrl("file:///assets/home.html"), "Nouvel Onglet")

        # --------------------------------------------------------------Window Propriétés
        self.setWindowTitle("Aelios")
        self.resize(1315, 768)
        self.setMinimumSize(1315, 600)
        self.setWindowIcon(QIcon("assets/logo.png"))

        self.tabs.setStyleSheet("""
                     QTabWidget::pane {
                        background-color: #56585d;
                        border: solid 1px #56585d;
                    }
                    
                    QTabBar {
                        background-color: #38393c;
                    }
                    
                    QTabBar::tab {
                        background: #38393c;
                        padding: 10px;
                        margin: 2px;
                        border-top-left-radius: 7px;
                        border-top-right-radius: 7px;
                        border-bottom-left-radius: 0px;
                        border-bottom-right-radius: 0px;
                        font-weight: bold;
                        width: 150px;
                        color: #a1a2a4;
                    }

                    QTabBar::tab:selected {
                        background: #56585d;
                        color: white;
                        margin-bottom: -2px;
                        margin-top: 3px;
                    }

                    QTabBar::tab:hover {
                        background: #404145;
                        color: white;
                    }
                    
                    QTabBar::close-button {
                        image: url("assets/close_tab.png");
                        subcontrol-position: right;
                        margin-right: 5px;
                    }
                    
                    QTabBar::close-button:hover {
                        image: url("assets/close_tab_hover.png");
                    }
                """)

    # --------------------------------------------------------------Ajouter un onglet
    def add_new_tab(self, url=None, label="Nouvel Onglet"):
        if url is None:
            url = QUrl("file:///assets/home.html")

        browser = CustomWebEngineView()
        browser.setUrl(url)

        browser.loadFinished.connect(self.update_nav_buttons)

        browser.page().iconChanged.connect(lambda icon, browser=browser: self.update_tab_icon(icon, browser))

        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_urlbar(qurl, browser))

        tab = QWidget()
        layout = QVBoxLayout()

        search_bar = QLineEdit()
        search_bar.setPlaceholderText("Rechercher...")
        search_bar.setFixedHeight(30)
        search_bar.setVisible(False)

        search_bar.returnPressed.connect(lambda: self.search_from_home(browser, search_bar.text()))

        layout.addWidget(search_bar)

        layout.addWidget(browser)
        tab.setLayout(layout)

        index = self.tabs.addTab(tab, label)
        self.tabs.setCurrentIndex(index)
        self.tabs.setTabToolTip(index, url.toString())

        if self.tabs.count() > 1:
            self.tabs.setMovable(True)
            self.tabs.setStyleSheet("""
                                 QTabWidget::pane {
                                    background-color: #56585d;
                                    border: solid 1px #56585d;
                                }

                                QTabBar {
                                    background-color: #38393c;
                                }

                                QTabBar::tab {
                                    background: #38393c;
                                    padding: 10px;
                                    margin: 2px;
                                    border-top-left-radius: 7px;
                                    border-top-right-radius: 7px;
                                    border-bottom-left-radius: 0px;
                                    border-bottom-right-radius: 0px;
                                    font-weight: bold;
                                    width: 150px;
                                    color: #a1a2a4;
                                }

                                QTabBar::tab:hover {
                                    background: #404145;
                                    color: white;
                                }
                                
                                QTabBar::tab:selected {
                                    background: #56585d;
                                    color: white;
                                    margin-bottom: -2px;
                                    margin-top: 3px;
                                }

                                QTabBar::close-button {
                                    image: url("assets/close_tab.png");
                                    subcontrol-position: right;
                                    margin-right: 5px;
                                }

                                QTabBar::close-button:hover {
                                    image: url("assets/close_tab_hover.png");
                                }
                            """)

    # --------------------------------------------------------------Fermer un onglet
    def close_current_tab(self):
        # Récupère l'index de l'onglet actif
        current_index = self.tabs.currentIndex()
        self.close_tab(current_index)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            if self.tabs.count() == 1:
                self.tabs.setMovable(False)
        else:
            exit()

    # --------------------------------------------------------------Charger une URL
    def load_url(self):
        global tor_status
        url = self.url_bar.text()
        if not "." in url:
            if tor_status == False:
                url = "https://duckduckgo.com/?t=h_&q=" + url
            else:
                url = "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/?t=h_&q=" + url
        if not url.startswith("http"):
            url = "http://" + url
        self.get_current_browser().setUrl(QUrl(url))

    # --------------------------------------------------------------Affiche URL
    def update_urlbar(self, qurl, browser):
        if browser == self.get_current_browser():
            if qurl.toString() == "file:///assets/home.html":
                self.url_bar.clear()
            else:
                self.url_bar.setText(qurl.toString())

                index = self.tabs.currentIndex()
                self.tabs.setTabText(index, qurl.host())

    # --------------------------------------------------------------Affiche Icône Onglet
    def update_tab_icon(self, icon, browser):
        index = self.tabs.indexOf(self.tabs.currentWidget())
        if index != -1:
            self.tabs.setTabIcon(index, icon)

    # --------------------------------------------------------------Autoriser Back Forward
    def update_nav_buttons(self):
        browser = self.get_current_browser()
        if browser:
            self.back_button.setEnabled(browser.page().history().canGoBack())
            self.forward_button.setEnabled(browser.page().history().canGoForward())

    # --------------------------------------------------------------Retourner l'onglet
    def next_tab(self):
        # Change pour l'onglet suivant
        current_index = self.tabs.currentIndex()
        next_index = current_index + 1 if current_index < self.tabs.count() - 1 else 0
        self.tabs.setCurrentIndex(next_index)

    def prev_tab(self):
        # Change pour l'onglet précédent
        current_index = self.tabs.currentIndex()
        prev_index = current_index - 1 if current_index > 0 else self.tabs.count() - 1
        self.tabs.setCurrentIndex(prev_index)

    def get_current_browser(self):
        current_widget = self.tabs.currentWidget()
        if current_widget:
            browser = current_widget.layout().itemAt(1).widget()
            return browser
        return None

    # --------------------------------------------------------------Accueil
    def go_home(self):
        self.get_current_browser().setUrl(QUrl("file:///assets/home.html"))

    # --------------------------------------------------------------Activer/Désactiver Tor
    def enable_disable_tor(self):
        global tor_status

        if tor_status == False:
            script_name = "LaunchTor.py"

            script_path = os.path.join(os.path.dirname(__file__), script_name)

            system = platform.system()

            interpreter = sys.executable

            try:
                if system == "Windows":
                    subprocess.Popen(f'start \"\" \"{interpreter}\" \"{script_path}\"', shell=True)

                elif system == "Linux":
                    terminal_commands = [
                        f'gnome-terminal -- {interpreter} "{script_path}"',
                        f'x-terminal-emulator -e {interpreter} "{script_path}"',
                        f'xterm -e {interpreter} "{script_path}"',
                        f'konsole -e {interpreter} "{script_path}"',
                    ]
                    launched = False
                    for cmd in terminal_commands:
                        try:
                            subprocess.Popen(cmd, shell=True)
                            launched = True
                            break
                        except FileNotFoundError:
                            continue

                    if not launched:
                        print("[ERROR] -- Linux terminal not found")
                        print("Maybe you have a too specific distribution, edsktop environnment or terminal...")
                        print("If you want, the code to modify is in \"Aelios.py\" beyond the line 520")

                elif system == "Darwin":
                    subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{interpreter} \\"{script_path}\\""'])

                else:
                    print("[ERROR] -- System not supported")

            except FileNotFoundError:
                print(f"[ERROR] -- {script_name} not found")
            except Exception as e:
                print(f"[ERROR] -- There was an error during starting tor executable : {e}")

            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.Socks5Proxy)
            proxy.setHostName("127.0.0.1")
            proxy.setPort(9050)
            QNetworkProxy.setApplicationProxy(proxy)
            self.add_new_tab(QUrl("http://check.torproject.org"), "Check Tor Network")
            self.tor_button.setIcon(QIcon("assets/tor_enable.png"))

            tor_status = True
        else:
            system = platform.system()

            try:
                if system == "Windows":
                    subprocess.run("taskkill /F /IM tor.exe", shell=True, check=True)
                    print("[Notice] -- tor executable successfully closed")

                elif system == "Linux" or system == "Darwin":
                    subprocess.run("pkill -f tor", shell=True, check=True)
                    print(f"[Notice] -- tor executable successfully closed")

                else:
                    print("[ERROR] -- System not supported")
            except subprocess.CalledProcessError:
                print("[ERROR] -- There was an error during closing tor executable")

            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.NoProxy)
            QNetworkProxy.setApplicationProxy(proxy)
            self.tor_button.setIcon(QIcon("assets/tor_disable.png"))

            tor_status = False


# --------------------------------------------------------------Lancement

app = QApplication([])
fenetre = Navigateur()
fenetre.show()
app.exec_()