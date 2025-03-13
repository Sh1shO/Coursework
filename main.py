from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QTableWidget, QWidget, 
                               QTableWidgetItem, QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                               QDialog, QFormLayout, QDateEdit, QComboBox, QMessageBox, QDoubleSpinBox)
from PySide6.QtCore import QDate
from db import get_session, Animal, Species, Enclosure, Employee, HealthRecord, AnimalFeed, Feed, Offspring
from datetime import datetime

# Базовый диалог
class BaseDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.layout = QFormLayout(self)

        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Сохранить")
        cancel_button = QPushButton("Отмена")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        self.layout.addRow(buttons_layout)

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

        with get_session() as session:
            species_list = session.query(Species).all()
            if not species_list:
                QMessageBox.warning(self, "Предупреждение", "Нет видов животных. Добавьте виды.")
            for sp in species_list:
                self.species.addItem(sp.name, sp.id)
            enclosures = session.query(Enclosure).all()
            if not enclosures:
                QMessageBox.warning(self, "Предупреждение", "Нет вольеров. Добавьте вольеры.")
            for enc in enclosures:
                self.enclosure.addItem(enc.name, enc.id)

        self.layout.addRow("Имя:", self.name)
        self.layout.addRow("Вид:", self.species)
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
        self.setup_ui()
        self.show_animals()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        search_layout = QHBoxLayout()
        search_label = QLabel("Поиск")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        buttons_layout = QHBoxLayout()
        self.animals_button = QPushButton("Животные")
        self.employees_button = QPushButton("Сотрудники")
        self.enclosures_button = QPushButton("Вольеры")
        self.feeding_button = QPushButton("Кормление")
        self.health_button = QPushButton("Медицина")
        self.add_button = QPushButton("Добавить")
        self.edit_button = QPushButton("Редактировать")

        for btn in [self.animals_button, self.employees_button, self.enclosures_button,
                    self.feeding_button, self.health_button, self.add_button, self.edit_button]:
            buttons_layout.addWidget(btn)
        layout.addLayout(buttons_layout)

        self.animals_table = QTableWidget()
        self.employees_table = QTableWidget()
        self.enclosures_table = QTableWidget()
        self.feeding_table = QTableWidget()
        self.health_table = QTableWidget()
        layout.addWidget(self.animals_table)
        layout.addWidget(self.employees_table)
        layout.addWidget(self.enclosures_table)
        layout.addWidget(self.feeding_table)
        layout.addWidget(self.health_table)

        self.animals_button.clicked.connect(self.show_animals)
        self.employees_button.clicked.connect(self.show_employees)
        self.enclosures_button.clicked.connect(self.show_enclosures)
        self.feeding_button.clicked.connect(self.show_feeding)
        self.health_button.clicked.connect(self.show_health)
        self.add_button.clicked.connect(self.add_item)
        self.edit_button.clicked.connect(self.edit_item)

    def load_data(self, model, table_widget, headers, data_function):
        with get_session() as session:
            self.current_items = session.query(model).all()
            table_widget.setRowCount(len(self.current_items))
            table_widget.setColumnCount(len(headers))
            table_widget.setHorizontalHeaderLabels(headers)
            for row, item in enumerate(self.current_items):
                for col, value in enumerate(data_function(item)):
                    table_widget.setItem(row, col, QTableWidgetItem(str(value)))
            table_widget.resizeColumnsToContents()

    def show_animals(self):
        self.current_table = self.animals_table
        self.hide_all_tables()
        self.animals_table.show()
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
        self.current_table = self.employees_table
        self.hide_all_tables()
        self.employees_table.show()
        headers = ["Имя", "Должность", "Телефон", "Дата найма"]
        def get_employee_data(employee):
            return [employee.name, employee.position, employee.phone, employee.hire_date]
        self.load_data(Employee, self.employees_table, headers, get_employee_data)

    def show_enclosures(self):
        self.current_table = self.enclosures_table
        self.hide_all_tables()
        self.enclosures_table.show()
        headers = ["Название", "Размер (м²)", "Местоположение", "Описание"]
        def get_enclosure_data(enclosure):
            return [enclosure.name, enclosure.size, enclosure.location, enclosure.description]
        self.load_data(Enclosure, self.enclosures_table, headers, get_enclosure_data)

    def show_feeding(self):
        self.current_table = self.feeding_table
        self.hide_all_tables()
        self.feeding_table.show()
        headers = ["Животное", "Корм", "Суточная норма (кг)"]
        def get_feeding_data(animal_feed):
            return [
                animal_feed.fk_animal.name if animal_feed.fk_animal else "",
                animal_feed.fk_feed.name if animal_feed.fk_feed else "",
                animal_feed.daily_amount
            ]
        self.load_data(AnimalFeed, self.feeding_table, headers, get_feeding_data)

    def show_health(self):
        self.current_table = self.health_table
        self.hide_all_tables()
        self.health_table.show()
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
                if current_row < 0 or current_row >= len(self.current_items):
                    QMessageBox.warning(self, "Ошибка", "Выберите строку для редактирования")
                    return
                item = self.current_items[current_row]
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
                self.current_items = filtered_items
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
                headers = ["Название", "Размер (м²)", "Местоположение", "Описание"]
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

app = QApplication([])
window = MainWindow()
window.show()
app.exec()