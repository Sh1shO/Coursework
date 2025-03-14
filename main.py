from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTableWidget, QWidget,
                               QTableWidgetItem, QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QDialog, QFormLayout, QDateEdit, QComboBox, QMessageBox, QDoubleSpinBox)
from PySide6.QtCore import QDate, Qt, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor
from PySide6.QtWidgets import QGraphicsDropShadowEffect
from db import get_session, Animal, Species, Enclosure, Employee, HealthRecord, AnimalFeed, Feed, Offspring
from datetime import datetime

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

        # Загружаем виды и вольеры
        self.load_species()
        self.load_enclosures()

        # Создаем кнопку для добавления вида
        species_layout = QHBoxLayout()
        species_layout.addWidget(self.species)
        add_species_button = QPushButton("Добавить вид")
        add_species_button.setObjectName("add_species_button")
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
            if not species_list:
                QMessageBox.warning(self, "Предупреждение", "Нет видов животных. Добавьте виды.")
            for sp in species_list:
                self.species.addItem(sp.name, sp.id)

    def load_enclosures(self):
        self.enclosure.clear()
        with get_session() as session:
            enclosures = session.query(Enclosure).all()
            if not enclosures:
                QMessageBox.warning(self, "Предупреждение", "Нет вольеров. Добавьте вольеры.")
            for enc in enclosures:
                self.enclosure.addItem(enc.name, enc.id)

    def add_species(self):
        species_dialog = SpeciesDialog(self)
        if species_dialog.exec():
            with get_session() as session:
                try:
                    new_species = Species(
                        name=species_dialog.name.text()
                    )
                    session.add(new_species)
                    session.commit()
                    QMessageBox.information(self, "Успех", "Новый вид успешно добавлен!")
                    self.load_species()  # Обновляем список видов
                    self.species.setCurrentIndex(self.species.findData(new_species.id))
                except Exception as e:
                    session.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении вида: {str(e)}")

# Диалог для сотрудников
class EmployeeDialog(BaseDialog):
    def __init__(self, parent=None, employee=None):
        super().__init__(parent, "Сотрудник")
        self.name = QLineEdit()
        self.position = QLineEdit()
        self.phone = QLineEdit()
        self.hire_date = QDateEdit()
        self.hire_date.setCalendarPopup(True)
        self.hire_date.setDate(QDate.currentDate())

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Должность:", self.position)
        self.layout.addRow("Телефон:", self.phone)
        self.layout.addRow("Дата найма:", self.hire_date)

        if employee:
            self.name.setText(employee.name)
            self.position.setText(employee.position)
            self.phone.setText(employee.phone)
            self.hire_date.setDate(QDate.fromString(str(employee.hire_date), "yyyy-MM-dd"))

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

# Диалог для кормления
class AnimalFeedDialog(BaseDialog):
    def __init__(self, parent=None, animal_feed=None):
        super().__init__(parent, "Кормление")
        self.animal = QComboBox()
        self.feed = QComboBox()
        self.daily_amount = QDoubleSpinBox()
        self.daily_amount.setRange(0, 1000)

        with get_session() as session:
            animals = session.query(Animal).all()
            if not animals:
                QMessageBox.warning(self, "Предупреждение", "Нет животных. Добавьте животных.")
            for a in animals:
                self.animal.addItem(a.name, a.id)
            feeds = session.query(Feed).all()
            if not feeds:
                QMessageBox.warning(self, "Предупреждение", "Нет кормов. Добавьте корма.")
            for f in feeds:
                self.feed.addItem(f.name, f.id)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Корм:", self.feed)
        self.layout.addRow("Суточная норма (кг):", self.daily_amount)

        if animal_feed:
            self.animal.setCurrentIndex(self.animal.findData(animal_feed.animal_id))
            self.feed.setCurrentIndex(self.feed.findData(animal_feed.feed_id))
            self.daily_amount.setValue(animal_feed.daily_amount)

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
            if not animals:
                QMessageBox.warning(self, "Предупреждение", "Нет животных. Добавьте животных.")
            for a in animals:
                self.animal.addItem(a.name, a.id)

        self.layout.addRow("Животное:", self.animal)
        self.layout.addRow("Дата осмотра:", self.checkup_date)
        self.layout.addRow("Заметки:", self.notes)

        if health_record:
            self.animal.setCurrentIndex(self.animal.findData(health_record.animal_id))
            self.checkup_date.setDate(QDate.fromString(str(health_record.checkup_date), "yyyy-MM-dd"))
            self.notes.setText(health_record.notes)

# Главное окно
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление зоопарком")
        self.setGeometry(200, 200, 1024, 768)
        self.setMinimumSize(1024, 768)  # Минимальный размер окна
        self.setup_ui()
        self.apply_styles()
        self.show_animals()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F6FF;
                font-family: 'Regular', 'Inter';
            }
            
            QLabel#logo {
                padding: 10px;
            }
            
            QLineEdit {
                background-color: #FFFFFF;
                border: 1px solid #B9B9B9;
                border-radius: 5px;
                transition: 0.3s ease;
                padding: 10px 15px;
                font-size: 14px;
            }

            #save, #cancel {
                text-align:center;
            }
            
            QPushButton {
                background-color: #FFFFFF;
                color: #636363;
                border-radius: 5px;
                border: 1px solid #B9B9C9;
                padding: 5px 10px;
                font-size: 14px;
                transition: background-color 0.3s ease;
                text-align: left;
            }
            
            QPushButton#edit_button, QPushButton#add_button {
                padding-left: 10px;
                position: relative;
                padding-right: 40px; /* Делаем место для иконки справа */
                border:1px solid #B9B9B9;
                text-align: center; /* Текст слева */
                background-position: right center; /* Иконка справа */
                background-repeat: no-repeat; /* Не повторяем иконку */
            }

            QPushButton#add_species_button {
                background-color: #FFFFFF;
                color: #636363;
                border: 1px solid #B9B9B9;
                border-radius: 5px;
                padding: 5px 10px;
                font-size: 14px;
                transition: background-color 0.3s ease;
            }
          
            QPushButton:hover {
                background-color: #BA68C8;
                color:white;
            }
            QTableWidget {
                background-color: #FFFFFF;
                border: 1px solid #B0BEC5;
                border-radius: 5px;
                font-size: 12px;
                alternate-background-color: #FFFFFF;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #CE93D8;
                color: #FFFFFF;
                padding: 5px;
                font-size: 12px;
            }
            QDialog {
                background-color: #F5F6FF;
                border: 1px solid #B9B9B9;
                border-radius: 10px;
            }
        """)

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Левая панель с кнопками (1/3 ширины)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Логотип как SVG
        logo = QLabel()
        logo.setObjectName("logo")
        logo_icon = QIcon("logo.svg")  # Укажите путь к вашему SVG-файлу
        logo_pixmap = logo_icon.pixmap(QSize(100, 100))  # Установите желаемый размер (например, 100x100)
        logo.setPixmap(logo_pixmap)
        left_layout.addWidget(logo)

        self.buttons = []
        button_configs = [
            ("Животные", "animals.svg", QSize(24, 24)),
            ("Сотрудники", "employees.svg", QSize(24, 24)),
            ("Вольеры", "enclosures.svg", QSize(24, 24)),
            ("Кормление", "feeding.svg", QSize(24, 24)),
            ("Медицина", "health.svg", QSize(24, 24)),
        ]

        # Создаем эффект тени
        shadow_effect = QGraphicsDropShadowEffect()
        shadow_effect.setBlurRadius(15)  # Размытие тени (аналог 15px в CSS)
        shadow_effect.setXOffset(10)     # Смещение по X (аналог 10px в CSS)
        shadow_effect.setYOffset(10)     # Смещение по Y (аналог 10px в CSS)
        shadow_effect.setColor(QColor(255, 255, 255, 0.4))  # Цвет тени (rgba(99, 99, 99, 1))

        for text, icon_path, icon_size in button_configs:
            button = QPushButton(text)
            button.setFixedSize(298, 48)
            button.setIcon(QIcon(icon_path))  # Устанавливаем SVG-иконку
            button.setIconSize(icon_size)     # Устанавливаем размер иконки
            button.setLayoutDirection(Qt.LeftToRight)  # Текст слева, иконка справа
            button.clicked.connect(lambda checked, t=text: self.show_section(t))
            button.setGraphicsEffect(shadow_effect)  # Применяем тень
            self.buttons.append(button)
            left_layout.addWidget(button)

        left_layout.addStretch()
        main_layout.addWidget(left_panel)
        main_layout.setStretch(0, 1)  # Левая панель — 1/3

        # Правая панель с поиском и таблицей (2/3 ширины)
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)  # Убираем лишние отступы

        # Поиск и кнопки над таблицей
        top_layout = QHBoxLayout()
        search_widget = QWidget()
        search_layout = QVBoxLayout(search_widget)
        self.search_input = QLineEdit()
        self.search_input.setFixedSize(624, 48)
        self.search_input.setPlaceholderText("Поиск")
        search_layout.addWidget(self.search_input)

        table_buttons_layout = QHBoxLayout()
        # Кнопка "Редактировать" с иконкой карандаша
        self.edit_button = QPushButton("Редактировать")
        self.edit_button.setObjectName("edit_button")  # Устанавливаем objectName для стилей
        self.edit_button.setFixedSize(298, 38)
        self.edit_button.clicked.connect(self.edit_item)
        self.edit_button.setGraphicsEffect(shadow_effect)  # Применяем тень

        # Кнопка "Добавить" с иконкой плюса
        self.add_button = QPushButton("Добавить")
        self.add_button.setObjectName("add_button")  # Устанавливаем objectName для стилей
        self.add_button.setFixedSize(298, 38)
        self.add_button.clicked.connect(self.add_item)
        self.add_button.setGraphicsEffect(shadow_effect)  # Применяем тень

        table_buttons_layout.addWidget(self.edit_button)
        table_buttons_layout.addStretch()
        table_buttons_layout.addWidget(self.add_button)
        search_layout.addLayout(table_buttons_layout)
        search_widget.setFixedHeight(100 + 38 + 10)  # Высота: 48px (поиск) + 38px (кнопки) + 10px (отступ)

        top_layout.addWidget(search_widget)
        top_layout.setStretch(0, 2)  # Поиск занимает 2/3
        top_layout.addStretch(1)     # Пустое пространство 1/3
        right_layout.addLayout(top_layout)

        # Таблица
        self.animals_table = QTableWidget()
        self.employees_table = QTableWidget()
        self.enclosures_table = QTableWidget()
        self.feeding_table = QTableWidget()
        self.health_table = QTableWidget()
        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeding_table, self.health_table]:
            table.setAlternatingRowColors(True)
            right_layout.addWidget(table)

        self.search_input.textChanged.connect(self.search_items)

        main_layout.addWidget(right_panel)
        main_layout.setStretch(1, 2)  # Правая панель — 2/3

        # Скрываем все таблицы
        self.hide_all_tables()
        self.current_table = None

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
        elif section == "Кормление":
            self.current_table = self.feeding_table
            self.show_feeding()
        elif section == "Медицина":
            self.current_table = self.health_table
            self.show_health()
        self.current_table.show()

    def load_data(self, model, table_widget, headers, data_function):
        with get_session() as session:
            self.current_items = session.query(model).all()  # Обновляем current_items
            table_widget.setRowCount(len(self.current_items))
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            for row, item in enumerate(self.current_items):
                for col, value in enumerate(data_function(item)):
                    table_widget.setItem(row, col, QTableWidgetItem(str(value)))
            table_widget.resizeColumnsToContents()

    def show_animals(self):
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
        self.load_data(Animal, self.animals_table, headers, get_animal_data)

    def show_employees(self):
        headers = ["Имя", "Должность", "Телефон", "Дата найма"]
        def get_employee_data(employee):
            return [employee.name, employee.position, employee.phone, employee.hire_date]
        self.load_data(Employee, self.employees_table, headers, get_employee_data)

    def show_enclosures(self):
        headers = ["Название", "Размер (m²)", "Местоположение", "Описание"]
        def get_enclosure_data(enclosure):
            return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
        self.load_data(Enclosure, self.enclosures_table, headers, get_enclosure_data)

    def show_feeding(self):
        headers = ["Животное", "Корм", "Суточная норма (кг)"]
        def get_feeding_data(animal_feed):
            return [
                animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                animal_feed.daily_amount
            ]
        self.load_data(AnimalFeed, self.feeding_table, headers, get_feeding_data)

    def show_health(self):
        headers = ["Животное", "Дата осмотра", "Заметки"]
        def get_health_data(health_record):
            return [
                health_record.fk_animal.name if health_record.fk_animal else "",
                health_record.checkup_date,
                health_record.notes
            ]
        self.load_data(HealthRecord, self.health_table, headers, get_health_data)

    def hide_all_tables(self):
        for table in [self.animals_table, self.employees_table, self.enclosures_table,
                      self.feeding_table, self.health_table]:
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
                            position=dialog.position.text(),
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
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении: {str(e)}")

    def edit_item(self):
        with get_session() as session:
            try:
                current_row = self.current_table.currentRow()
                if current_row < 0:
                    QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования")
                    return

                # Обновляем current_items в зависимости от текущей таблицы
                if self.current_table == self.animals_table:
                    self.current_items = session.query(Animal).all()
                elif self.current_table == self.employees_table:
                    self.current_items = session.query(Employee).all()
                elif self.current_table == self.enclosures_table:
                    self.current_items = session.query(Enclosure).all()
                elif self.current_table == self.feeding_table:
                    self.current_items = session.query(AnimalFeed).all()
                elif self.current_table == self.health_table:
                    self.current_items = session.query(HealthRecord).all()

                if current_row >= len(self.current_items):
                    QMessageBox.warning(self, "Ошибка", "Выбранная строка недоступна")
                    return

                item = self.current_items[current_row]
                print(f"Editing item: {item}")  # Отладочный вывод

                if self.current_table == self.animals_table:
                    dialog = AnimalDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.species_id = dialog.species.currentData()
                        item.enclosure_id = dialog.enclosure.currentData()
                        item.date_of_birth = dialog.date_of_birth.date().toPython()
                        item.date_of_arrival = dialog.date_of_arrival.date().toPython()
                        item.sex = dialog.sex.currentText()
                        session.commit()
                        self.show_animals()
                elif self.current_table == self.employees_table:
                    dialog = EmployeeDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.position = dialog.position.text()
                        item.phone = dialog.phone.text()
                        item.hire_date = dialog.hire_date.date().toPython()
                        session.commit()
                        self.show_employees()
                elif self.current_table == self.enclosures_table:
                    dialog = EnclosureDialog(self, item)
                    if dialog.exec():
                        item.name = dialog.name.text()
                        item.size = dialog.size.value()
                        item.location = dialog.location.text()
                        item.description = dialog.description.text()
                        session.commit()
                        self.show_enclosures()
                elif self.current_table == self.feeding_table:
                    dialog = AnimalFeedDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.feed_id = dialog.feed.currentData()
                        item.daily_amount = dialog.daily_amount.value()
                        session.commit()
                        self.show_feeding()
                elif self.current_table == self.health_table:
                    dialog = HealthRecordDialog(self, item)
                    if dialog.exec():
                        item.animal_id = dialog.animal.currentData()
                        item.checkup_date = dialog.checkup_date.date().toPython()
                        item.notes = dialog.notes.text()
                        session.commit()
                        self.show_health()
            except Exception as e:
                session.rollback()
                QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании: {str(e)}")
                print(f"Exception: {e}")  # Отладочный вывод ошибки

    def search_items(self, text):
        if not text:
            if self.current_table == self.animals_table:
                self.show_animals()
            elif self.current_table == self.employees_table:
                self.show_employees()
            elif self.current_table == self.enclosures_table:
                self.show_enclosures()
            elif self.current_table == self.feeding_table:
                self.show_feeding()
            elif self.current_table == self.health_table:
                self.show_health()
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
                self.current_items = filtered_items  # Обновляем current_items для поиска
                self.animals_table.setRowCount(len(filtered_items))
                self.animals_table.setColumnCount(len(headers))
                self.animals_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_animal_data(item)):
                        self.animals_table.setItem(row, col, QTableWidgetItem(str(value)))
            elif self.current_table == self.employees_table:
                filtered_items = session.query(Employee).filter(
                    (Employee.name.ilike(f"%{text}%")) |
                    (Employee.position.ilike(f"%{text}%")) |
                    (Employee.phone.ilike(f"%{text}%"))
                ).all()
                headers = ["Имя", "Должность", "Телефон", "Дата найма"]
                def get_employee_data(employee):
                    return [employee.name, employee.position, employee.phone, employee.hire_date]
                self.current_items = filtered_items
                self.employees_table.setRowCount(len(filtered_items))
                self.employees_table.setColumnCount(len(headers))
                self.employees_table.setHorizontalHeaderLabels(headers)
                for row, item in enumerate(filtered_items):
                    for col, value in enumerate(get_employee_data(item)):
                        self.employees_table.setItem(row, col, QTableWidgetItem(str(value)))
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
            self.current_table.resizeColumnsToContents()

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()