from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTableWidget, QWidget,
                               QTableWidgetItem, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QDialog, QFormLayout, QDateEdit, QComboBox, QMessageBox, QDoubleSpinBox,
                               QSizePolicy, QHeaderView, QInputDialog, QFileDialog)
from PySide6.QtCore import QDate, Qt, QSize, Signal, QTimer
from PySide6.QtGui import QIcon
from db import get_session, Animal, Species, Enclosure, Employee, HealthRecord, AnimalFeed, Feed, Offspring, AnimalCaretaker, Position
from fpdf import FPDF

# Кастомный класс для кнопки с иконкой "+"
class CustomButtonWidget(QWidget):
    clicked = Signal(str)
    plus_clicked = Signal(str)

    def __init__(self, text, plus_icon_path, plus_icon_size, parent=None):
        super().__init__(parent)
        self.setFixedSize(298, 48)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.main_button = QPushButton(text)
        self.main_button.setStyleSheet("""
            QPushButton {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: left;
                padding-right: 50px;
                position: relative;
            }
            QPushButton:hover {
                background-color: #C7E8FF;
                color: #636363;
            }
        """)
        self.main_button.clicked.connect(lambda: self.clicked.emit(text))

        self.plus_button = QPushButton(self.main_button)
        self.plus_button.setIcon(QIcon(plus_icon_path))
        self.plus_button.setIconSize(plus_icon_size)
        self.plus_button.setFixedSize(QSize(30, 30))
        self.plus_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                qproperty-iconSize: 24px;
                padding: 3px;
            }
            QPushButton:hover {
                background-color: #C7E8FF;
                border-radius: 10px;
            }
        """)
        self.plus_button.move(298 - 30 - 10, (48 - 30) // 2)
        self.plus_button.clicked.connect(lambda: self.plus_clicked.emit(text + "_add"))

        self.layout.addWidget(self.main_button)
        self.main_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

    def resizeEvent(self, event):
        self.setFixedSize(298, 48)
        self.plus_button.move(298 - 30 - 10, (48 - 30) // 2)
        super().resizeEvent(event)

    def set_active(self, active):
        if active:
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #C7E8FF;
                    color: #636363;
                    border-radius: 5px;
                    border: 1px solid #ECECEC;
                    padding: 5px 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-right: 50px;
                    position: relative;
                }
                QPushButton:hover {
                    background-color: #C7E8FF;
                    color: #636363;
                }
            """)
        else:
            self.main_button.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    color: #636363;
                    border-radius: 5px;
                    border: 1px solid #ECECEC;
                    padding: 5px 10px;
                    font-size: 14px;
                    text-align: left;
                    padding-right: 50px;
                    position: relative;
                }
                QPushButton:hover {
                    background-color: #C7E8FF;
                    color: #636363;
                }
            """)

# Базовый диалог
class BaseDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(400)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(10)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        save_button.setObjectName("save")
        cancel_button = QPushButton("Отмена")
        cancel_button.setObjectName("cancel")
        
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self.layout.addRow(buttons_layout)

# Диалог для добавления вида
class SpeciesDialog(BaseDialog):
    def __init__(self, parent=None, species=None):
        super().__init__(parent, "Добавить вид")
        self.name = QLineEdit()
        self.layout.addRow("Название вида:", self.name)
        if species:
            self.name.setText(species.name)

# Диалог для добавления должности
class PositionDialog(BaseDialog):
    def __init__(self, parent=None, position=None):
        super().__init__(parent, "Добавить должность")
        self.name = QLineEdit()
        self.layout.addRow("Название должности:", self.name)
        if position:
            self.name.setText(position.name)

# Диалог для животных
class AnimalDialog(BaseDialog):
    def __init__(self, parent=None, animal=None):
        super().__init__(parent, "Животное")
        self.name = QLineEdit()
        self.species = QComboBox()
        self.enclosure = QComboBox()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate())
        self.date_of_arrival = QDateEdit()
        self.date_of_arrival.setCalendarPopup(True)
        self.date_of_arrival.setDate(QDate.currentDate())
        self.sex = QComboBox()
        self.sex.addItems(["Male", "Female"])

        self.load_species()
        self.load_enclosures()

        species_layout = QHBoxLayout()
        species_layout.addWidget(self.species)
        add_species_button = QPushButton("Добавить вид")
        add_species_button.setObjectName("add_species_button")
        add_species_button.setIconSize(QSize(24, 24))
        add_species_button.clicked.connect(self.add_species)
        species_layout.addWidget(add_species_button)

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Вид:", species_layout)
        self.layout.addRow("Вольер:", self.enclosure)
        self.layout.addRow("Дата рождения:", self.date_of_birth)
        self.layout.addRow("Дата прибытия:", self.date_of_arrival)
        self.layout.addRow("Пол:", self.sex)

        if animal:
            self.name.setText(animal.name)
            self.species.setCurrentIndex(self.species.findData(animal.species_id))
            self.enclosure.setCurrentIndex(self.enclosure.findData(animal.enclosure_id))
            self.date_of_birth.setDate(QDate.fromString(str(animal.date_of_birth), "yyyy-MM-dd"))
            self.date_of_arrival.setDate(QDate.fromString(str(animal.date_of_arrival), "yyyy-MM-dd"))
            self.sex.setCurrentText(animal.sex)

    def load_species(self):
        self.species.clear()
        with get_session() as session:
            species_list = session.query(Species).all()
            for sp in species_list:
                self.species.addItem(sp.name, sp.id)

    def load_enclosures(self):
        self.enclosure.clear()
        with get_session() as session:
            enclosures = session.query(Enclosure).all()
            for enc in enclosures:
                self.enclosure.addItem(enc.name, enc.id)

    def add_species(self):
        species_dialog = SpeciesDialog(self)
        if species_dialog.exec():
            with get_session() as session:
                try:
                    new_species = Species(name=species_dialog.name.text())
                    session.add(new_species)
                    session.commit()
                    self.load_species()
                    self.species.setCurrentIndex(self.species.findData(new_species.id))
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении вида: {str(e)}")

# Диалог для сотрудников
class EmployeeDialog(BaseDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Сотрудник")
        self.name = QLineEdit()
        self.position = QComboBox()
        self.phone = QLineEdit()
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())

        self.load_positions()

        position_layout = QHBoxLayout()
        position_layout.addWidget(self.position)
        add_position_button = QPushButton("Добавить должность")
        add_position_button.setObjectName("add_position_button")
        add_position_button.clicked.connect(self.add_position)
        position_layout.addWidget(add_position_button)

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Должность:", position_layout)
        self.layout.addRow("Телефон:", self.phone)
        self.layout.addRow("Дата найма:", self.hire_date)

        if employee:
            self.name.setText(employee.name)
            self.position.setCurrentIndex(self.position.findData(employee.position_id))
            self.phone.setText(employee.phone)
            self.hire_date.setDate(QDate.fromString(str(employee.hire_date), "yyyy-MM-dd"))

    def load_positions(self):
        self.position.clear()
        with get_session() as session:
            positions = session.query(Position).all()
            for pos in positions:
                self.position.addItem(pos.name, pos.id)

    def add_position(self):
        position_dialog = PositionDialog(self)
        if position_dialog.exec():
            with get_session() as session:
                try:
                    new_position = Position(name=position_dialog.name.text())
                    session.add(new_position)
                    session.commit()
                    self.load_positions()
                    self.position.setCurrentIndex(self.position.findData(new_position.id))
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении должности: {str(e)}")

# Диалог для вольеров
class EnclosureDialog(BaseDialog):
    def __init__(self, parent=None, enclosure=None):
        super().__init__(parent, "Вольер")
        self.name = QLineEdit()
        self.size = QDoubleSpinBox()
        self.size.setRange(0, 10000)
        self.location = QLineEdit()
        self.description = QLineEdit()

        self.layout.addRow("Название:", self.name)
        self.layout.addRow("Размер (м²):", self.size)
        self.layout.addRow("Местоположение:", self.location)
        self.layout.addRow("Описание:", self.description)

        if enclosure:
            self.name.setText(enclosure.name)
            self.size.setValue(enclosure.size)
            self.location.setText(enclosure.location)
            self.description.setText(enclosure.description)

# Диалог для кормов
class FeedDialog(BaseDialog):
    def __init__(self, parent=None, feed=None):
        super().__init__(parent, "Корм")
        self.name = QLineEdit()
        self.description = QLineEdit()

        self.layout.addRow("Название:", self.name)
        self.layout.addRow("Описание:", self.description)

        if feed:
            self.name.setText(feed.name)
            self.description.setText(feed.description)

# Диалог для кормления
class AnimalFeedDialog(BaseDialog):
    def __init__(self, parent=None, animal_feed=None):
        super().__init__(parent, "Кормление")
        self.animal = QComboBox()
        self.feed = QComboBox()
        self.daily_amount = QDoubleSpinBox()
        self.daily_amount.setRange(0, 1000)

        self.load_animals()
        self.load_feeds()

        feed_layout = QHBoxLayout()
        feed_layout.addWidget(self.feed)
        add_feed_button = QPushButton("Добавить корм")
        add_feed_button.setObjectName("add_feed_button")
        add_feed_button.clicked.connect(self.add_feed)
        feed_layout.addWidget(add_feed_button)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Корм:", feed_layout)
        self.layout.addRow("Суточная норма (кг):", self.daily_amount)

        if animal_feed:
            self.animal.setCurrentIndex(self.animal.findData(animal_feed.animal_id))
            self.feed.setCurrentIndex(self.feed.findData(animal_feed.feed_id))
            self.daily_amount.setValue(animal_feed.daily_amount)

    def load_animals(self):
        self.animal.clear()
        with get_session() as session:
            animals = session.query(Animal).all()
            for a in animals:
                self.animal.addItem(a.name, a.id)

    def load_feeds(self):
        self.feed.clear()
        with get_session() as session:
            feeds = session.query(Feed).all()
            for f in feeds:
                self.feed.addItem(f.name, f.id)

    def add_feed(self):
        feed_dialog = FeedDialog(self)
        if feed_dialog.exec():
            with get_session() as session:
                try:
                    new_feed = Feed(
                        name=feed_dialog.name.text(),
                        description=feed_dialog.description.text()
                    )
                    session.add(new_feed)
                    session.commit()
                    self.load_feeds()
                    self.feed.setCurrentIndex(self.feed.findData(new_feed.id))
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении корма: {str(e)}")

# Диалог для медицинских записей
class HealthRecordDialog(BaseDialog):
    def __init__(self, parent=None, health_record=None):
        super().__init__(parent, "Медицинская запись")
        self.animal = QComboBox()
        self.checkup_date = QDateEdit()
        self.checkup_date.setCalendarPopup(True)
        self.checkup_date.setDate(QDate.currentDate())
        self.notes = QLineEdit()

        with get_session() as session:
            animals = session.query(Animal).all()
            for a in animals:
                self.animal.addItem(a.name, a.id)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Дата осмотра:", self.checkup_date)
        self.layout.addRow("Заметки:", self.notes)

        if health_record:
            self.animal.setCurrentIndex(self.animal.findData(health_record.animal_id))
            self.checkup_date.setDate(QDate.fromString(str(health_record.checkup_date), "yyyy-MM-dd"))
            self.notes.setText(health_record.notes)

# Диалог для потомства
class OffspringDialog(BaseDialog):
    def __init__(self, parent=None, offspring=None):
        super().__init__(parent, "Потомство")
        self.name = QLineEdit()
        self.mother = QComboBox()
        self.father = QComboBox()
        self.date_of_birth = QDateEdit()
        self.date_of_birth.setCalendarPopup(True)
        self.date_of_birth.setDate(QDate.currentDate())
        self.sex = QComboBox()
        self.sex.addItems(["Male", "Female"])

        with get_session() as session:
            animals = session.query(Animal).all()
            self.mother.addItem("Неизвестно", None)
            self.father.addItem("Неизвестно", None)
            for animal in animals:
                if animal.sex == "Female":
                    self.mother.addItem(animal.name, animal.id)
                if animal.sex == "Male":
                    self.father.addItem(animal.name, animal.id)

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Мать:", self.mother)
        self.layout.addRow("Отец:", self.father)
        self.layout.addRow("Дата рождения:", self.date_of_birth)
        self.layout.addRow("Пол:", self.sex)

        if offspring:
            self.name.setText(offspring.name)
            self.mother.setCurrentIndex(self.mother.findData(offspring.mother_id))
            self.father.setCurrentIndex(self.father.findData(offspring.father_id))
            self.date_of_birth.setDate(QDate.fromString(str(offspring.date_of_birth), "yyyy-MM-dd"))
            self.sex.setCurrentText(offspring.sex)

# Диалог для назначения ухаживающих
class AnimalCaretakerDialog(BaseDialog):
    def __init__(self, parent=None, caretaker=None):
        super().__init__(parent, "Назначение ухаживающего")
        self.employee = QComboBox()
        self.animal = QComboBox()

        with get_session() as session:
            employees = session.query(Employee).all()
            for emp in employees:
                self.employee.addItem(emp.name, emp.id)

            animals = session.query(Animal).all()
            for a in animals:
                self.animal.addItem(a.name, a.id)

        self.layout.addRow("Сотрудник:", self.employee)
        self.layout.addRow("Животное:", self.animal)

        if caretaker:
            self.employee.setCurrentIndex(self.employee.findData(caretaker.employee_id))
            self.animal.setCurrentIndex(self.animal.findData(caretaker.animal_id))

# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление зоопарком")
        self.setGeometry(200, 200, 1024, 768)
        self.setMinimumSize(1024, 768)
        self.setup_ui()
        self.apply_styles()
        self.show_animals()
        self.current_table = self.animals_table
        self.animals_table.show()
        self.set_active_button("Животные")
        self.start_auto_refresh()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #F5F6FF; font-family: 'Regular', 'Inter'; }
            QLabel#logo { padding: 10px; }
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 10px 15px;
                font-size: 14px;
            }
            #save, #cancel { text-align: center; }
            QPushButton {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton#report_button {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                padding: 5px 10px;
                font-size: 14px;
                text-align: center;
            }
            QPushButton#report_button:hover {
                background-color: #C7E8FF;
                color: #636363;
                border: 1px solid #ECECEC;
            }
            QPushButton#delete_button {
                background-color: #FFC1C1;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                text-align: center;
            }
            QPushButton#delete_button:hover {
                background-color: #FF9999;
                color: #FFFFFF;
                border: 1px solid #ECECEC;
            }
            QPushButton#add_button {
                background-color: #5FFFD2;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #ECECEC;
                text-align: center;
            }
            QPushButton#add_button:hover {
                background-color: #00E6A8;
                color: #FFFFFF;
                border: 1px solid #ECECEC;
            }
            QPushButton#add_species_button, QPushButton#add_position_button, QPushButton#add_feed_button {
                background-color: #FFFFFF;
                color: #636363;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
            }
            QPushButton#add_species_button:hover, QPushButton#add_position_button:hover, QPushButton#add_feed_button:hover { 
                background-color: #C7E8FF; 
                color: #636363; 
            }
            QPushButton:hover { 
                background-color: #C7E8FF; 
                color: #636363; 
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                font-size: 12px;
                alternate-background-color: #FFFFFF;
            }
            QTableWidget::item { 
                padding: 5px; 
            }
            QHeaderView::section {
                background-color: #C7E8FF;
                color: #636363;
                padding: 5px;
                font-size: 12px;
            }
            QHeaderView { 
                background-color: rgba(0,0,0,0); 
            }
            QDialog {
                background-color: #F5F6FF;
                border: 1px solid #ECECEC;
                border-radius: 10px;
            }
            QComboBox {
                background-color: #FFFFFF;
                border: 1px solid #ECECEC;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
                color: #636363;
            }
            QComboBox:hover {
                background-color: #C7E8FF;
            }
            QComboBox QAbstractItemView {
                color: #636363;
                background-color: #FFFFFF;
                selection-background-color: #C7E8FF;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        logo = QLabel()
        logo.setObjectName("logo")
        logo_icon = QIcon("logo.svg")
        logo_pixmap = logo_icon.pixmap(QSize(120, 120))
        logo.setPixmap(logo_pixmap)
        left_layout.addWidget(logo)

        self.buttons = []
        button_configs = [
            ("Животные", "plus.svg", QSize(24, 24)),
            ("Сотрудники", "plus.svg", QSize(24, 24)),
            ("Вольеры", "plus.svg", QSize(24, 24)),
            ("Корма", "plus.svg", QSize(24, 24)),
            ("Кормление", "plus.svg", QSize(24, 24)),
            ("Медицина", "plus.svg", QSize(24, 24)),
            ("Потомство", "plus.svg", QSize(24, 24)),
            ("Ухаживающие", "plus.svg", QSize(24, 24)),
        ]

        for text, plus_icon_path, plus_icon_size in button_configs:
            button_widget = CustomButtonWidget(text, plus_icon_path, plus_icon_size)
            button_widget.setFixedSize(298, 48)
            button_widget.clicked.connect(self.show_section)
            button_widget.plus_clicked.connect(self.add_item_from_plus)
            self.buttons.append(button_widget)
            left_layout.addWidget(button_widget)

        left_layout.addSpacing(50)

        report_panel = QWidget()
        report_layout = QVBoxLayout(report_panel)
        report_layout.setContentsMargins(0, 0, 0, 0)

        self.report_combo = QComboBox()
        self.report_combo.setFixedSize(298, 48)
        self.report_combo.addItems([
            "Отчёт по животным",
            "Отчёт по сотрудникам",
            "Отчёт по вольерам",
            "Отчёт по кормам",
            "Отчёт по кормлению",
            "Отчёт по медицинским записям",
            "Отчёт по родословной",
            "Отчёт по ухаживающим",
        ])
        self.report_combo.setCurrentText("Отчёт по животным")

        self.report_button = QPushButton("Сгенерировать")
        self.report_button.setObjectName("report_button")
        self.report_button.setFixedSize(298, 48)
        self.report_button.clicked.connect(self.generate_report)

        report_layout.addWidget(self.report_combo)
        report_layout.addWidget(self.report_button)
        left_layout.addWidget(report_panel)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        main_layout.setStretch(0, 1)

        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск")
        right_layout.addWidget(self.search_input)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setContentsMargins(0, 5, 0, 0)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.setObjectName("delete_button")
        self.delete_button.setFixedHeight(38)
        self.delete_button.clicked.connect(self.delete_item)

        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("add_button")
        self.add_button.setFixedHeight(38)
        self.add_button.clicked.connect(self.add_item)

        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.add_button)
        right_layout.addWidget(buttons_widget)

        self.animals_table = QTableWidget()
        self.employees_table = QTableWidget()
        self.enclosures_table = QTableWidget()
        self.feeds_table = QTableWidget()
        self.feeding_table = QTableWidget()
        self.health_table = QTableWidget()
        self.offspring_table = QTableWidget()
        self.caretaker_table = QTableWidget()

        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeds_table, self.feeding_table, self.health_table,
                      self.offspring_table, self.caretaker_table]:
            table.setAlternatingRowColors(True)
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.doubleClicked.connect(self.edit_item_on_double_click)
            right_layout.addWidget(table)

        self.search_input.textChanged.connect(self.search_items)

        main_layout.addWidget(right_panel)
        main_layout.setStretch(1, 2)

        self.hide_all_tables()
        self.current_table = None

    def start_auto_refresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_current_table)
        self.timer.start(5000)  # Обновление каждые 5 секунд

    def refresh_current_table(self):
        if self.current_table:
            if self.current_table == self.animals_table:
                self.show_animals()
            elif self.current_table == self.employees_table:
                self.show_employees()
            elif self.current_table == self.enclosures_table:
                self.show_enclosures()
            elif self.current_table == self.feeds_table:
                self.show_feeds()
            elif self.current_table == self.feeding_table:
                self.show_feeding()
            elif self.current_table == self.health_table:
                self.show_health()
            elif self.current_table == self.offspring_table:
                self.show_offspring()
            elif self.current_table == self.caretaker_table:
                self.show_caretakers()

    def generate_report(self):
        report_type = self.report_combo.currentText()
        if not report_type:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите тип отчёта.")
            return

        try:
            with get_session() as session:
                pdf = FPDF()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.add_page()

                pdf.add_font('FreeSans', '', 'FreeSans.ttf', uni=True)
                pdf.set_font('FreeSans', '', 16)

                pdf.cell(200, 10, f"{report_type}", ln=True, align='C')
                pdf.ln(10)

                pdf.set_font('FreeSans', '', 12)

                if report_type == "Отчёт по животным":
                    animals = session.query(Animal).all()
                    for animal in animals:
                        pdf.cell(200, 10, f"Имя: {animal.name}", ln=True)
                        pdf.cell(200, 10, f"Вид: {animal.fk_species.name if animal.fk_species else 'Не указан'}", ln=True)
                        pdf.cell(200, 10, f"Вольер: {animal.fk_enclosure.name if animal.fk_enclosure else 'Не указан'}", ln=True)
                        pdf.cell(200, 10, f"Дата рождения: {animal.date_of_birth}", ln=True)
                        pdf.cell(200, 10, f"Дата прибытия: {animal.date_of_arrival}", ln=True)
                        pdf.cell(200, 10, f"Пол: {animal.sex}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество животных: {len(animals)}", ln=True, align='R')

                elif report_type == "Отчёт по сотрудникам":
                    employees = session.query(Employee).all()
                    for emp in employees:
                        pdf.cell(200, 10, f"Имя: {emp.name}", ln=True)
                        pdf.cell(200, 10, f"Должность: {emp.fk_position.name if emp.fk_position else 'Не указана'}", ln=True)
                        pdf.cell(200, 10, f"Телефон: {emp.phone}", ln=True)
                        pdf.cell(200, 10, f"Дата найма: {emp.hire_date}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество сотрудников: {len(employees)}", ln=True, align='R')

                elif report_type == "Отчёт по вольерам":
                    enclosures = session.query(Enclosure).all()
                    for enc in enclosures:
                        pdf.cell(200, 10, f"Название: {enc.name}", ln=True)
                        pdf.cell(200, 10, f"Размер: {enc.size} м²", ln=True)
                        pdf.cell(200, 10, f"Местоположение: {enc.location}", ln=True)
                        pdf.cell(200, 10, f"Описание: {enc.description if enc.description else 'Нет описания'}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество вольеров: {len(enclosures)}", ln=True, align='R')

                elif report_type == "Отчёт по кормам":
                    feeds = session.query(Feed).all()
                    for feed in feeds:
                        pdf.cell(200, 10, f"Название: {feed.name}", ln=True)
                        pdf.cell(200, 10, f"Описание: {feed.description if feed.description else 'Нет описания'}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество кормов: {len(feeds)}", ln=True, align='R')

                elif report_type == "Отчёт по кормлению":
                    feedings = session.query(AnimalFeed).all()
                    total_daily_amount = 0
                    for feed in feedings:
                        pdf.cell(200, 10, f"Животное: {feed.fk_animal.name if feed.fk_animal else 'Не указано'}", ln=True)
                        pdf.cell(200, 10, f"Корм: {feed.fk_feed.name if feed.fk_feed else 'Не указано'}", ln=True)
                        pdf.cell(200, 10, f"Суточная норма: {feed.daily_amount} кг", ln=True)
                        total_daily_amount += feed.daily_amount
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество корма в сутки: {total_daily_amount:.2f} кг", ln=True, align='R')

                elif report_type == "Отчёт по медицинским записям":
                    health_records = session.query(HealthRecord).all()
                    for record in health_records:
                        pdf.cell(200, 10, f"Животное: {record.fk_animal.name if record.fk_animal else 'Не указано'}", ln=True)
                        pdf.cell(200, 10, f"Дата осмотра: {record.checkup_date}", ln=True)
                        pdf.cell(200, 10, f"Заметки: {record.notes if record.notes else 'Нет заметок'}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество медицинских записей: {len(health_records)}", ln=True, align='R')

                elif report_type == "Отчёт по родословной":
                    animal_name, ok = QInputDialog.getText(self, "Имя животного", "Введите имя животного для построения родословной:")
                    if not ok or not animal_name:
                        QMessageBox.warning(self, "Ошибка", "Имя животного не введено.")
                        return

                    animal = session.query(Animal).filter(Animal.name.ilike(f"%{animal_name}%")).first()
                    if not animal:
                        QMessageBox.warning(self, "Ошибка", f"Животное с именем '{animal_name}' не найдено.")
                        return

                    pedigree = self.build_pedigree(animal, session, depth=0)
                    pdf.multi_cell(200, 10, f"Родословная для {animal.name}:\n{pedigree}")

                elif report_type == "Отчёт по ухаживающим":
                    caretakers = session.query(AnimalCaretaker).all()
                    for caretaker in caretakers:
                        pdf.cell(200, 10, f"Сотрудник: {caretaker.fk_employee.name if caretaker.fk_employee else 'Не указано'}", ln=True)
                        pdf.cell(200, 10, f"Животное: {caretaker.fk_animal.name if caretaker.fk_animal else 'Не указано'}", ln=True)
                        pdf.ln(5)
                    pdf.ln(10)
                    pdf.set_font('FreeSans', '', 14)
                    pdf.cell(0, 10, f"Общее количество назначений: {len(caretakers)}", ln=True, align='R')

                report_filename = report_type.lower().replace(" ", "_").replace("отчёт_", "") + "_report.pdf"
                pdf_output_path, _ = QFileDialog.getSaveFileName(
                    self, "Сохранить отчёт", report_filename, "PDF Files (*.pdf)"
                )
                if not pdf_output_path:
                    return

                pdf.output(pdf_output_path)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при генерации отчёта: {str(e)}")

    def build_pedigree(self, animal, session, depth=0, max_depth=5):
        if depth > max_depth:
            return "  " * depth + "... (дальше не отображается)\n"

        indent = "  " * depth
        result = f"{indent}{animal.name} ({animal.sex}, {animal.date_of_birth})\n"

        mother_record = session.query(Offspring).filter(Offspring.name == animal.name).first()
        if mother_record and mother_record.fk_mother:
            result += f"{indent}Мать:\n"
            result += self.build_pedigree(mother_record.fk_mother, session, depth + 1, max_depth)

        if mother_record and mother_record.fk_father:
            result += f"{indent}Отец:\n"
            result += self.build_pedigree(mother_record.fk_father, session, depth + 1, max_depth)

        return result

    def show_section(self, section):
        self.hide_all_tables()
        if section == "Животные":
            self.current_table = self.animals_table
            self.show_animals()
        elif section == "Сотрудники":
            self.current_table = self.employees_table
            self.show_employees()
        elif section == "Вольеры":
            self.current_table = self.enclosures_table
            self.show_enclosures()
        elif section == "Корма":
            self.current_table = self.feeds_table
            self.show_feeds()
        elif section == "Кормление":
            self.current_table = self.feeding_table
            self.show_feeding()
        elif section == "Медицина":
            self.current_table = self.health_table
            self.show_health()
        elif section == "Потомство":
            self.current_table = self.offspring_table
            self.show_offspring()
        elif section == "Ухаживающие":
            self.current_table = self.caretaker_table
            self.show_caretakers()
        self.current_table.show()
        self.set_active_button(section)

    def set_active_button(self, active_section):
        for button_widget in self.buttons:
            button_widget.set_active(False)
        for button_widget in self.buttons:
            if button_widget.main_button.text() == active_section:
                button_widget.set_active(True)
                break

    def add_item_from_plus(self, action):
        if action.endswith("_add"):
            section = action[:-4]
            if section == "Животные":
                self.current_table = self.animals_table
                dialog = AnimalDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_animal = Animal(
                            name=dialog.name.text(),
                            species_id=dialog.species.currentData(),
                            enclosure_id=dialog.enclosure.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            date_of_arrival=dialog.date_of_arrival.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_animal)
                        session.commit()
                        self.show_animals()
            elif section == "Сотрудники":
                self.current_table = self.employees_table
                dialog = EmployeeDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_employee = Employee(
                            name=dialog.name.text(),
                            position_id=dialog.position.currentData(),
                            phone=dialog.phone.text(),
                            hire_date=dialog.hire_date.date().toPython()
                        )
                        session.add(new_employee)
                        session.commit()
                        self.show_employees()
            elif section == "Вольеры":
                self.current_table = self.enclosures_table
                dialog = EnclosureDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_enclosure = Enclosure(
                            name=dialog.name.text(),
                            size=dialog.size.value(),
                            location=dialog.location.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_enclosure)
                        session.commit()
                        self.show_enclosures()
            elif section == "Корма":
                self.current_table = self.feeds_table
                dialog = FeedDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_feed = Feed(
                            name=dialog.name.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_feed)
                        session.commit()
                        self.show_feeds()
            elif section == "Кормление":
                self.current_table = self.feeding_table
                dialog = AnimalFeedDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_feeding = AnimalFeed(
                            animal_id=dialog.animal.currentData(),
                            feed_id=dialog.feed.currentData(),
                            daily_amount=dialog.daily_amount.value()
                        )
                        session.add(new_feeding)
                        session.commit()
                        self.show_feeding()
            elif section == "Медицина":
                self.current_table = self.health_table
                dialog = HealthRecordDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_health = HealthRecord(
                            animal_id=dialog.animal.currentData(),
                            checkup_date=dialog.checkup_date.date().toPython(),
                            notes=dialog.notes.text()
                        )
                        session.add(new_health)
                        session.commit()
                        self.show_health()
            elif section == "Потомство":
                self.current_table = self.offspring_table
                dialog = OffspringDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_offspring = Offspring(
                            name=dialog.name.text(),
                            mother_id=dialog.mother.currentData(),
                            father_id=dialog.father.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_offspring)
                        session.commit()
                        self.show_offspring()
            elif section == "Ухаживающие":
                self.current_table = self.caretaker_table
                dialog = AnimalCaretakerDialog(self)
                if dialog.exec():
                    with get_session() as session:
                        new_caretaker = AnimalCaretaker(
                            employee_id=dialog.employee.currentData(),
                            animal_id=dialog.animal.currentData()
                        )
                        session.add(new_caretaker)
                        session.commit()
                        self.show_caretakers()

    def load_data(self, session, model, table_widget, headers, data_function):
        self.current_items = session.query(model).all()
        table_widget.setRowCount(len(self.current_items))
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)
        for row, item in enumerate(self.current_items):
            for col, value in enumerate(data_function(item)):
                table_widget.setItem(row, col, QTableWidgetItem(str(value)))
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def show_animals(self):
        with get_session() as session:
            headers = ["Имя", "Вид", "Вольер", "Дата рождения", "Дата прибытия", "Пол"]
            def get_animal_data(animal):
                return [
                    animal.name,
                    animal.fk_species.name if animal.fk_species else "",
                    animal.fk_enclosure.name if animal.fk_enclosure else "",
                    animal.date_of_birth,
                    animal.date_of_arrival,
                    animal.sex
                ]
            self.load_data(session, Animal, self.animals_table, headers, get_animal_data)
            self.set_active_button("Животные")

    def show_employees(self):
        with get_session() as session:
            headers = ["Имя", "Должность", "Телефон", "Дата найма"]
            def get_employee_data(employee):
                return [
                    employee.name,
                    employee.fk_position.name if employee.fk_position else "",
                    employee.phone,
                    employee.hire_date
                ]
            self.load_data(session, Employee, self.employees_table, headers, get_employee_data)
            self.set_active_button("Сотрудники")

    def show_enclosures(self):
        with get_session() as session:
            headers = ["Название", "Размер (m²)", "Местоположение", "Описание"]
            def get_enclosure_data(enclosure):
                return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
            self.load_data(session, Enclosure, self.enclosures_table, headers, get_enclosure_data)
            self.set_active_button("Вольеры")

    def show_feeds(self):
        with get_session() as session:
            headers = ["Название", "Описание"]
            def get_feed_data(feed):
                return [feed.name, feed.description]
            self.load_data(session, Feed, self.feeds_table, headers, get_feed_data)
            self.set_active_button("Корма")

    def show_feeding(self):
        with get_session() as session:
            headers = ["Животное", "Корм", "Суточная норма (кг)"]
            def get_feeding_data(animal_feed):
                return [
                    animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                    animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                    animal_feed.daily_amount
                ]
            self.load_data(session, AnimalFeed, self.feeding_table, headers, get_feeding_data)
            self.set_active_button("Кормление")

    def show_health(self):
        with get_session() as session:
            headers = ["Животное", "Дата осмотра", "Заметки"]
            def get_health_data(health_record):
                return [
                    health_record.fk_animal.name if health_record.fk_animal else "",
                    health_record.checkup_date,
                    health_record.notes
                ]
            self.load_data(session, HealthRecord, self.health_table, headers, get_health_data)
            self.set_active_button("Медицина")

    def show_offspring(self):
        with get_session() as session:
            headers = ["Имя", "Мать", "Отец", "Дата рождения", "Пол"]
            def get_offspring_data(offspring):
                return [
                    offspring.name,
                    offspring.fk_mother.name if offspring.fk_mother else "Неизвестно",
                    offspring.fk_father.name if offspring.fk_father else "Неизвестно",
                    offspring.date_of_birth,
                    offspring.sex
                ]
            self.load_data(session, Offspring, self.offspring_table, headers, get_offspring_data)
            self.set_active_button("Потомство")

    def show_caretakers(self):
        with get_session() as session:
            headers = ["Сотрудник", "Животное"]
            def get_caretaker_data(caretaker):
                return [
                    caretaker.fk_employee.name if caretaker.fk_employee else "",
                    caretaker.fk_animal.name if caretaker.fk_animal else ""
                ]
            self.load_data(session, AnimalCaretaker, self.caretaker_table, headers, get_caretaker_data)
            self.set_active_button("Ухаживающие")

    def hide_all_tables(self):
        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeds_table, self.feeding_table, self.health_table,
                      self.offspring_table, self.caretaker_table]:
            table.hide()

    def add_item(self):
        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    dialog = AnimalDialog(self)
                    if dialog.exec():
                        new_animal = Animal(
                            name=dialog.name.text(),
                            species_id=dialog.species.currentData(),
                            enclosure_id=dialog.enclosure.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            date_of_arrival=dialog.date_of_arrival.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_animal)
                        session.commit()
                        self.show_animals()
                elif self.current_table == self.employees_table:
                    dialog = EmployeeDialog(self)
                    if dialog.exec():
                        new_employee = Employee(
                            name=dialog.name.text(),
                            position_id=dialog.position.currentData(),
                            phone=dialog.phone.text(),
                            hire_date=dialog.hire_date.date().toPython()
                        )
                        session.add(new_employee)
                        session.commit()
                        self.show_employees()
                elif self.current_table == self.enclosures_table:
                    dialog = EnclosureDialog(self)
                    if dialog.exec():
                        new_enclosure = Enclosure(
                            name=dialog.name.text(),
                            size=dialog.size.value(),
                            location=dialog.location.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_enclosure)
                        session.commit()
                        self.show_enclosures()
                elif self.current_table == self.feeds_table:
                    dialog = FeedDialog(self)
                    if dialog.exec():
                        new_feed = Feed(
                            name=dialog.name.text(),
                            description=dialog.description.text()
                        )
                        session.add(new_feed)
                        session.commit()
                        self.show_feeds()
                elif self.current_table == self.feeding_table:
                    dialog = AnimalFeedDialog(self)
                    if dialog.exec():
                        new_feeding = AnimalFeed(
                            animal_id=dialog.animal.currentData(),
                            feed_id=dialog.feed.currentData(),
                            daily_amount=dialog.daily_amount.value()
                        )
                        session.add(new_feeding)
                        session.commit()
                        self.show_feeding()
                elif self.current_table == self.health_table:
                    dialog = HealthRecordDialog(self)
                    if dialog.exec():
                        new_health = HealthRecord(
                            animal_id=dialog.animal.currentData(),
                            checkup_date=dialog.checkup_date.date().toPython(),
                            notes=dialog.notes.text()
                        )
                        session.add(new_health)
                        session.commit()
                        self.show_health()
                elif self.current_table == self.offspring_table:
                    dialog = OffspringDialog(self)
                    if dialog.exec():
                        new_offspring = Offspring(
                            name=dialog.name.text(),
                            mother_id=dialog.mother.currentData(),
                            father_id=dialog.father.currentData(),
                            date_of_birth=dialog.date_of_birth.date().toPython(),
                            sex=dialog.sex.currentText()
                        )
                        session.add(new_offspring)
                        session.commit()
                        self.show_offspring()
                elif self.current_table == self.caretaker_table:
                    dialog = AnimalCaretakerDialog(self)
                    if dialog.exec():
                        new_caretaker = AnimalCaretaker(
                            employee_id=dialog.employee.currentData(),
                            animal_id=dialog.animal.currentData()
                        )
                        session.add(new_caretaker)
                        session.commit()
                        self.show_caretakers()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_item_on_double_click(self, index):
        if not self.current_table:
            return

        current_row = index.row()
        if current_row < 0:
            return

        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    self.current_items = session.query(Animal).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Animal).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = AnimalDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.species_id = dialog.species.currentData()
                        item.enclosure_id = dialog.enclosure.currentData()
                        item.date_of_birth = dialog.date_of_birth.date().toPython()
                        item.date_of_arrival = dialog.date_of_arrival.date().toPython()
                        item.sex = dialog.sex.currentText()
                        session.merge(item)
                        session.commit()
                        self.show_animals()
                elif self.current_table == self.employees_table:
                    self.current_items = session.query(Employee).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Employee).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = EmployeeDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.position_id = dialog.position.currentData()
                        item.phone = dialog.phone.text()
                        item.hire_date = dialog.hire_date.date().toPython()
                        session.merge(item)
                        session.commit()
                        self.show_employees()
                elif self.current_table == self.enclosures_table:
                    self.current_items = session.query(Enclosure).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Enclosure).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = EnclosureDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.size = dialog.size.value()
                        item.location = dialog.location.text()
                        item.description = dialog.description.text()
                        session.merge(item)
                        session.commit()
                        self.show_enclosures()
                elif self.current_table == self.feeds_table:
                    self.current_items = session.query(Feed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Feed).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = FeedDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.description = dialog.description.text()
                        session.merge(item)
                        session.commit()
                        self.show_feeds()
                elif self.current_table == self.feeding_table:
                    self.current_items = session.query(AnimalFeed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalFeed).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = AnimalFeedDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.feed_id = dialog.feed.currentData()
                        item.daily_amount = dialog.daily_amount.value()
                        session.merge(item)
                        session.commit()
                        self.show_feeding()
                elif self.current_table == self.health_table:
                    self.current_items = session.query(HealthRecord).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(HealthRecord).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = HealthRecordDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.checkup_date = dialog.checkup_date.date().toPython()
                        item.notes = dialog.notes.text()
                        session.merge(item)
                        session.commit()
                        self.show_health()
                elif self.current_table == self.offspring_table:
                    self.current_items = session.query(Offspring).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Offspring).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = OffspringDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.mother_id = dialog.mother.currentData()
                        item.father_id = dialog.father.currentData()
                        item.date_of_birth = dialog.date_of_birth.date().toPython()
                        item.sex = dialog.sex.currentText()
                        session.merge(item)
                        session.commit()
                        self.show_offspring()
                elif self.current_table == self.caretaker_table:
                    self.current_items = session.query(AnimalCaretaker).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalCaretaker).filter_by(id=item_id).first()
                    if not item:
                        return
                    dialog = AnimalCaretakerDialog(self, item)
                    if dialog.exec():
                        item.employee_id = dialog.employee.currentData()
                        item.animal_id = dialog.animal.currentData()
                        session.merge(item)
                        session.commit()
                        self.show_caretakers()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {str(e)}")

    def delete_item(self):
        if not self.current_table:
            QMessageBox.warning(self, "Ошибка", "Выберите таблицу для удаления")
            return

        current_row = self.current_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите строку для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить эту запись?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        with get_session() as session:
            try:
                if self.current_table == self.animals_table:
                    self.current_items = session.query(Animal).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Animal).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_animals()
                elif self.current_table == self.employees_table:
                    self.current_items = session.query(Employee).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Employee).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_employees()
                elif self.current_table == self.enclosures_table:
                    self.current_items = session.query(Enclosure).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Enclosure).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_enclosures()
                elif self.current_table == self.feeds_table:
                    self.current_items = session.query(Feed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Feed).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_feeds()
                elif self.current_table == self.feeding_table:
                    self.current_items = session.query(AnimalFeed).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalFeed).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_feeding()
                elif self.current_table == self.health_table:
                    self.current_items = session.query(HealthRecord).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(HealthRecord).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_health()
                elif self.current_table == self.offspring_table:
                    self.current_items = session.query(Offspring).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(Offspring).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_offspring()
                elif self.current_table == self.caretaker_table:
                    self.current_items = session.query(AnimalCaretaker).all()
                    if current_row >= len(self.current_items):
                        return
                    item_id = self.current_items[current_row].id
                    item = session.query(AnimalCaretaker).filter_by(id=item_id).first()
                    if not item:
                        return
                    session.delete(item)
                    session.commit()
                    self.show_caretakers()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении: {str(e)}")

    def search_items(self, text):
        if not text:
            if self.current_table == self.animals_table:
                self.show_animals()
            elif self.current_table == self.employees_table:
                self.show_employees()
            elif self.current_table == self.enclosures_table:
                self.show_enclosures()
            elif self.current_table == self.feeds_table:
                self.show_feeds()
            elif self.current_table == self.feeding_table:
                self.show_feeding()
            elif self.current_table == self.health_table:
                self.show_health()
            elif self.current_table == self.offspring_table:
                self.show_offspring()
            elif self.current_table == self.caretaker_table:
                self.show_caretakers()
            return
        with get_session() as session:
            text = text.lower()
            if self.current_table == self.animals_table:
                filtered_items = session.query(Animal).filter(
                    (Animal.name.ilike(f"%{text}%")) |
                    (Animal.fk_species.has(Species.name.ilike(f"%{text}%"))) |
                    (Animal.fk_enclosure.has(Enclosure.name.ilike(f"%{text}%")))
                ).all()
                headers = ["Имя", "Вид", "Вольер", "Дата рождения", "Дата прибытия", "Пол"]
                def get_animal_data(animal):
                    return [
                        animal.name,
                        animal.fk_species.name if animal.fk_species else "",
                        animal.fk_enclosure.name if animal.fk_enclosure else "",
                        animal.date_of_birth,
                        animal.date_of_arrival,
                        animal.sex
                    ]
                self.current_items = filtered_items
                self.animals_table.setRowCount(len(filtered_items))
                self.animals_table.setColumnCount(len(headers))
                self.animals_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_animal_data(item)):
                        self.animals_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.animals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.employees_table:
                filtered_items = session.query(Employee).filter(
                    (Employee.name.ilike(f"%{text}%")) |
                    (Employee.fk_position.has(Position.name.ilike(f"%{text}%"))) |
                    (Employee.phone.ilike(f"%{text}%"))
                ).all()
                headers = ["Имя", "Должность", "Телефон", "Дата найма"]
                def get_employee_data(employee):
                    return [
                        employee.name,
                        employee.fk_position.name if employee.fk_position else "",
                        employee.phone,
                        employee.hire_date
                    ]
                self.current_items = filtered_items
                self.employees_table.setRowCount(len(filtered_items))
                self.employees_table.setColumnCount(len(headers))
                self.employees_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_employee_data(item)):
                        self.employees_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.employees_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.enclosures_table:
                filtered_items = session.query(Enclosure).filter(
                    (Enclosure.name.ilike(f"%{text}%")) |
                    (Enclosure.location.ilike(f"%{text}%")) |
                    (Enclosure.description.ilike(f"%{text}%"))
                ).all()
                headers = ["Название", "Размер (m²)", "Местоположение", "Описание"]
                def get_enclosure_data(enclosure):
                    return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
                self.current_items = filtered_items
                self.enclosures_table.setRowCount(len(filtered_items))
                self.enclosures_table.setColumnCount(len(headers))
                self.enclosures_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_enclosure_data(item)):
                        self.enclosures_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.enclosures_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.feeds_table:
                filtered_items = session.query(Feed).filter(
                    (Feed.name.ilike(f"%{text}%")) |
                    (Feed.description.ilike(f"%{text}%"))
                ).all()
                headers = ["Название", "Описание"]
                def get_feed_data(feed):
                    return [feed.name, feed.description]
                self.current_items = filtered_items
                self.feeds_table.setRowCount(len(filtered_items))
                self.feeds_table.setColumnCount(len(headers))
                self.feeds_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_feed_data(item)):
                        self.feeds_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.feeds_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.feeding_table:
                filtered_items = session.query(AnimalFeed).filter(
                    (AnimalFeed.fk_animal.has(Animal.name.ilike(f"%{text}%"))) |
                    (AnimalFeed.fk_feed.has(Feed.name.ilike(f"%{text}%")))
                ).all()
                headers = ["Животное", "Корм", "Суточная норма (кг)"]
                def get_feeding_data(animal_feed):
                    return [
                        animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                        animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                        animal_feed.daily_amount
                    ]
                self.current_items = filtered_items
                self.feeding_table.setRowCount(len(filtered_items))
                self.feeding_table.setColumnCount(len(headers))
                self.feeding_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_feeding_data(item)):
                        self.feeding_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.feeding_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.health_table:
                filtered_items = session.query(HealthRecord).filter(
                    (HealthRecord.fk_animal.has(Animal.name.ilike(f"%{text}%"))) |
                    (HealthRecord.notes.ilike(f"%{text}%"))
                ).all()
                headers = ["Животное", "Дата осмотра", "Заметки"]
                def get_health_data(health_record):
                    return [
                        health_record.fk_animal.name if health_record.fk_animal else "",
                        health_record.checkup_date,
                        health_record.notes
                    ]
                self.current_items = filtered_items
                self.health_table.setRowCount(len(filtered_items))
                self.health_table.setColumnCount(len(headers))
                self.health_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_health_data(item)):
                        self.health_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.health_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

            elif self.current_table == self.offspring_table:
                filtered_items = session.query(Offspring).filter(
                    (Offspring.name.ilike(f"%{text}%")) |
                    (Offspring.fk_mother.has(Animal.name.ilike(f"%{text}%"))) |
                    (Offspring.fk_father.has(Animal.name.ilike(f"%{text}%")))
                ).all()
                headers = ["Имя", "Мать", "Отец", "Дата рождения", "Пол"]
                def get_offspring_data(offspring):
                    return [
                        offspring.name,
                        offspring.fk_mother.name if offspring.fk_mother else "Неизвестно",
                        offspring.fk_father.name if offspring.fk_father else "Неизвестно",
                        offspring.date_of_birth,
                        offspring.sex
                    ]
                self.current_items = filtered_items
                self.offspring_table.setRowCount(len(filtered_items))
                self.offspring_table.setColumnCount(len(headers))
                self.offspring_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_offspring_data(item)):
                        self.offspring_table.setItem(row, col, QTableWidgetItem(str(value)))
                self.off