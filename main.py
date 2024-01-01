import sys
import json
import re
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QMainWindow
from PyQt5.uic import loadUi

#############################################################################################################

def load_users():
    try:
        with open('users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error loading users.json: {e}")
        return []

def save_users(users):
    try:
        with open('users.json', 'w') as file:
            json.dump(users, file, indent=4)
    except Exception as e:
        print(f"Error saving to users.json: {e}")

###############################################################################################################

def load_lessons():
        try:
            with open('lessons.json', 'r') as lessons_file:
                return json.load(lessons_file)
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error loading lessons.json: {e}")
            return []
        
def save_lessons(lessons):
        try:
            with open('lessons.json', 'w') as lessons_file:
                json.dump(lessons,lessons_file, indent=4)
        except Exception as e:
            print(f"Error saving to lessons.json: {e}")

###############################################################################################################


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+={}[\]:;<>,.?/~\\-]).{8,}$"
    return re.match(pattern, password)

def is_valid_phone(phone):
    return re.match(r"^\+\d{1,3}\d{9}$", phone)

def is_admin(user):
    return user.get('type') == 'admin'

def is_student(user):
    return user.get('type') == 'student'

def is_teacher(user):
    return user.get('type') == 'teacher'

#############################################################################################################

# Application Classes
class AdminApp(QMainWindow):
    def __init__(self):
        super(AdminApp, self).__init__()
        loadUi("admin.ui", self)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().setVisible(False)
        self.menu11.triggered.connect(self.add_teacher_tab)
        self.menu12.triggered.connect(self.edit_teacher_tab)
        self.menu71.triggered.connect(self.close)  # Logout from admin menu
        self.b5.clicked.connect(self.handle_teacher_registration)
        self.cb21.currentIndexChanged.connect(self.on_teacher_selected)

    def add_teacher_tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.fill_teacherID()

    def fill_teacherID(self):
        try:
            with open("users.json", "r") as userFile:
                data = json.load(userFile)
                teacherID = 0
                for item in data:
                    if item.get('type') == 'teacher':
                        teacherID += 1
                self.tb11.setText(str(teacherID+1))
        except FileNotFoundError:
            print("File not found: users.json")
            return []
        except Exception as e:
            print(f"Error loading users.json: {e}")
            return []

    def handle_teacher_registration(self):
        if self.save_teacher_details():
            self.clear_form_fields()
            self.ask_to_register_another()

    def save_teacher_details(self):
        teacherId = self.tb11.text()
        email = self.tb12.text()
        password = self.tb17.text()
        name = self.tb13.text()
        surname = self.tb14.text()
        gender = self.cb11.currentText()
        date_of_birth = self.tb15.text()
        phone = self.tb16.text()

        if not is_valid_email(email) or not is_valid_password(password) or not is_valid_phone(phone):
            QMessageBox.warning(self, "Registration Error", "Invalid input format")
            return False

        users = load_users()
        if any(user['email'] == email for user in users):
            QMessageBox.warning(self, "Registration form", "User Already Exists!!")
            return False
        else:
            users.append({
                'teacherId': teacherId,
                'email': email,
                'password': password,
                'name': name,
                'surname': surname,
                'gender': gender,
                'date_of_birth': date_of_birth,
                'phone': phone,
                'type': 'teacher'
            })
            save_users(users)
            QMessageBox.information(self, "Registration form", "New Teacher Registered Successfully, HE/SHE CAN NOW LOGIN!!")
            return True

    def clear_form_fields(self):
        self.tb11.clear()
        self.tb12.clear()
        self.tb17.clear()
        self.tb13.clear()
        self.tb14.clear()
        self.cb11.setCurrentIndex(0)
        self.tb15.clear()
        self.tb16.clear()

    def ask_to_register_another(self):
        reply = QMessageBox.question(self, 'Register Another Teacher',
                                     'Do you want to register another teacher?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_teacher_tab()
        else:
            self.close()

    def edit_teacher_tab(self):
        self.tabWidget.setCurrentIndex(2)
        self.load_teachers_into_combobox()
        self.b6.clicked.connect(self.update_teacher_details)  # b6 is your Save button
        self.b7.clicked.connect(self.delete_teacher)  # b7 is your Delete button

    def load_teachers_into_combobox(self):
        self.cb21.clear()  # Clear existing items, replace cb21 with your actual QComboBox name
        users = load_users()  # Load users from file
        teachers = [user for user in users if user.get('type') == 'teacher']
        for teacher in teachers:
            self.cb21.addItem(teacher['email'], teacher)  # Adding teacher ID and associate the full teacher data

    def on_teacher_selected(self, index):
        if index == -1:  # No selection or the combo box is being cleared
            return

        teacher_data = self.cb21.itemData(index)
        if teacher_data:
            self.tb21.setText(teacher_data['teacherId'])
            self.tb22.setText(teacher_data['email'])
            self.tb23.setText(teacher_data['name'])
            self.tb24.setText(teacher_data['surname'])
            self.cb22.setCurrentText(teacher_data['gender'])
            self.tb25.setText(teacher_data['date_of_birth'])
            self.tb26.setText(teacher_data['phone'])

    def update_teacher_details(self):
        teacherId = self.tb21.text()
        email = self.tb22.text()
        name = self.tb23.text()
        surname = self.tb24.text()
        gender = self.cb22.currentText()
        date_of_birth = self.tb25.text()
        phone = self.tb26.text()
        password = self.tb27.text()

        users = load_users()
        for i, user in enumerate(users):
            if user.get('type') == 'teacher' and user['email'] == email:
                users[i].update({
                    'teacherId': teacherId,
                    'email': email,
                    'name': name,
                    'surname': surname,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'phone': phone,
                    'password': password
                })
                break
        save_users(users)
        QMessageBox.information(self, "Update Success", "Teacher details updated successfully.")
        self.load_teachers_into_combobox()  # Refresh the teacher list

    def delete_teacher(self):
        teacher_id_to_delete = self.cb21.currentText()
        users = load_users()
        users = [user for user in users if not (user.get('type') == 'teacher' and user['email'] == teacher_id_to_delete)]
        save_users(users)
        QMessageBox.information(self, "Deletion Success", "Teacher details deleted successfully.")
        self.load_teachers_into_combobox()  # Refresh the teacher list

#############################################################################################################
class TeacherApp(QMainWindow):
    def __init__(self, email):
        super(TeacherApp, self).__init__()
        loadUi("teacher.ui", self)
        self.email = email
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().setVisible(False)
        self.menu11_t.triggered.connect(self.edit_profile_tab)
        self.menu21_t.triggered.connect(self.course_schedule_tab)
        self.menu71_t.triggered.connect(self.close)  # Logout from teacher menu

        self.b6.clicked.connect(self.update_teacher_details)  
        self.b6_t.clicked.connect(self.save_course_schedule)
        self.b7_t_3.clicked.connect(self.clear_schedule_form)  # Button to clear form  

 #############################################################################################################
        
    def edit_profile_tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.load_teacher_details()

    def load_teacher_details(self):
        users = load_users()
        for user in users:
            if user.get('type') == 'teacher' and user['email'] == self.email:
                # Load the teacher's details into the form
                self.tb21.setText(user.get('teacherId', ''))  
                self.tb22.setText(user.get('email', ''))  
                self.tb23.setText(user.get('name', ''))  
                self.tb24.setText(user.get('surname', ''))  
                self.cb11_tch.setCurrentText(user.get('gender', ''))  
                self.tb25.setText(user.get('date_of_birth', ''))  
                self.tb26.setText(user.get('phone', ''))  
                self.tb27.setText(user.get('password', ''))  
                break

    def update_teacher_details(self):
        teacher_id = self.tb21.text()
        email = self.tb22.text()
        name = self.tb23.text()
        surname = self.tb24.text()
        gender = self.cb11_tch.currentText()
        date_of_birth = self.tb25.text()
        phone = self.tb26.text()
        password = self.tb27.text()

        if not is_valid_email(email) or not is_valid_password(password) or not is_valid_phone(phone):
            QMessageBox.warning(self, "Update Error", "Invalid input format")
            return

        users = load_users()
        for i, user in enumerate(users):
            if user.get('type') == 'teacher' and user['email'] == self.email:
                users[i].update({
                    'teacherId': teacher_id,
                    'email': email,
                    'name': name,
                    'surname': surname,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'phone': phone,
                    'password': password
                })
                break
        save_users(users)
        QMessageBox.information(self, "Update Success", "Your teacher details updated successfully.")
#############################################################################################################

    def course_schedule_tab(self):
        self.tabWidget.setCurrentIndex(2)
        self.load_current_schedule()
    
    def load_current_schedule(self):
        lessons = load_lessons()
        if not lessons:
            QMessageBox.information(self, "Load Schedule", "No existing schedule found.")
            return

        current_schedule = lessons[0]

        self.tb21_course.setText(current_schedule.get('date_lesson_1', ''))
        self.cb21_course.setCurrentText(current_schedule.get('time_slot_lesson_1', ''))
        self.tb22_course.setText(current_schedule.get('lesson_subject_lesson_1', ''))
        self.tb23_course.setText(current_schedule.get('date_lesson_2', ''))
        self.cb22_course.setCurrentText(current_schedule.get('time_slot_lesson_2', ''))
        self.tb24_course.setText(current_schedule.get('lesson_subject_lesson_2', ''))
        self.tb25_course.setText(current_schedule.get('date_lesson_3', ''))
        self.cb23_course.setCurrentText(current_schedule.get('time_slot_lesson_3', ''))
        self.tb26_course.setText(current_schedule.get('lesson_subject_lesson_3', ''))
        self.tb27_course.setText(current_schedule.get('date_lesson_4', ''))
        self.cb24_course.setCurrentText(current_schedule.get('time_slot_lesson_4', ''))
        self.tb28_course.setText(current_schedule.get('lesson_subject_lesson_4', ''))
        self.tb29_course.setText(current_schedule.get('date_lesson_5', ''))
        self.cb25_course.setCurrentText(current_schedule.get('time_slot_lesson_5', ''))
        self.tb210_course.setText(current_schedule.get('lesson_subject_lesson_5', ''))
        self.tb211_course.setText(current_schedule.get('date_lesson_6', ''))
        self.cb26_course.setCurrentText(current_schedule.get('time_slot_lesson_6', ''))
        self.tb212_course.setText(current_schedule.get('lesson_subject_lesson_6', ''))
        self.tb213_course.setText(current_schedule.get('date_lesson_7', ''))
        self.cb27_course.setCurrentText(current_schedule.get('time_slot_lesson_7', ''))
        self.tb214_course.setText(current_schedule.get('lesson_subject_lesson_7', ''))
        self.tb215_course.setText(current_schedule.get('date_lesson_8', ''))
        self.cb28_course.setCurrentText(current_schedule.get('time_slot_lesson_8', ''))
        self.tb216_course.setText(current_schedule.get('lesson_subject_lesson_8', ''))
        self.tb217_course.setText(current_schedule.get('date_lesson_9', ''))
        self.cb29_course.setCurrentText(current_schedule.get('time_slot_lesson_9', ''))
        self.tb218_course.setText(current_schedule.get('lesson_subject_lesson_9', ''))
        self.tb219_course.setText(current_schedule.get('date_lesson_10', ''))
        self.cb210_course.setCurrentText(current_schedule.get('time_slot_lesson_10', ''))
        self.tb220_course.setText(current_schedule.get('lesson_subject_lesson_10', ''))
        self.tb221_course.setText(current_schedule.get('date_lesson_11', ''))
        self.cb211_course.setCurrentText(current_schedule.get('time_slot_lesson_11', ''))
        self.tb222_course.setText(current_schedule.get('lesson_subject_lesson_11', ''))
        self.tb223_course.setText(current_schedule.get('date_lesson_12', ''))
        self.cb212_course.setCurrentText(current_schedule.get('time_slot_lesson_12', ''))
        self.tb224_course.setText(current_schedule.get('lesson_subject_lesson_12', ''))
        self.tb225_course.setText(current_schedule.get('date_lesson_13', ''))
        self.cb213_course.setCurrentText(current_schedule.get('time_slot_lesson_13', ''))
        self.tb226_course.setText(current_schedule.get('lesson_subject_lesson_13', ''))
        self.tb227_course.setText(current_schedule.get('date_lesson_14', ''))
        self.cb214_course.setCurrentText(current_schedule.get('time_slot_lesson_14', ''))
        self.tb228_course.setText(current_schedule.get('lesson_subject_lesson_14', ''))
        self.tb229_course.setText(current_schedule.get('date_lesson_15', ''))
        self.cb215_course.setCurrentText(current_schedule.get('time_slot_lesson_15', ''))
        self.tb230_course.setText(current_schedule.get('lesson_subject_lesson_15', ''))    

        
    def save_course_schedule(self):
        try:
            new_schedule = {
            'date_lesson_1': self.tb21_course.text(),
            'time_slot_lesson_1': self.cb21_course.currentText(),
            'lesson_subject_lesson_1': self.tb22_course.text(),
            'date_lesson_2': self.tb23_course.text(),
            'time_slot_lesson_2': self.cb22_course.currentText(),
            'lesson_subject_lesson_2': self.tb24_course.text(),
            'date_lesson_3': self.tb25_course.text(),
            'time_slot_lesson_3': self.cb23_course.currentText(),
            'lesson_subject_lesson_3': self.tb26_course.text(),
            'date_lesson_4': self.tb27_course.text(),
            'time_slot_lesson_4': self.cb24_course.currentText(),
            'lesson_subject_lesson_4': self.tb28_course.text(),
            'date_lesson_5': self.tb29_course.text(),
            'time_slot_lesson_5': self.cb25_course.currentText(),
            'lesson_subject_lesson_5': self.tb210_course.text(),
            'date_lesson_6': self.tb211_course.text(),
            'time_slot_lesson_6': self.cb26_course.currentText(),
            'lesson_subject_lesson_6': self.tb212_course.text(),
            'date_lesson_7': self.tb213_course.text(),
            'time_slot_lesson_7': self.cb27_course.currentText(),
            'lesson_subject_lesson_7': self.tb214_course.text(),
            'date_lesson_8': self.tb215_course.text(),
            'time_slot_lesson_8': self.cb28_course.currentText(),
            'lesson_subject_lesson_8': self.tb216_course.text(),
            'date_lesson_9': self.tb217_course.text(),
            'time_slot_lesson_9': self.cb29_course.currentText(),
            'lesson_subject_lesson_9': self.tb218_course.text(),
            'date_lesson_10': self.tb219_course.text(),
            'time_slot_lesson_10': self.cb210_course.currentText(),
            'lesson_subject_lesson_10': self.tb220_course.text(),
            'date_lesson_11': self.tb221_course.text(),
            'time_slot_lesson_11': self.cb211_course.currentText(),
            'lesson_subject_lesson_11': self.tb222_course.text(),
            'date_lesson_12': self.tb223_course.text(),
            'time_slot_lesson_12': self.cb212_course.currentText(),
            'lesson_subject_lesson_12': self.tb224_course.text(),
            'date_lesson_13': self.tb225_course.text(),
            'time_slot_lesson_13': self.cb213_course.currentText(),
            'lesson_subject_lesson_13': self.tb226_course.text(),
            'date_lesson_14': self.tb227_course.text(),
            'time_slot_lesson_14': self.cb214_course.currentText(),
            'lesson_subject_lesson_14': self.tb228_course.text(),
            'date_lesson_15': self.tb229_course.text(),
            'time_slot_lesson_15': self.cb215_course.currentText(),
            'lesson_subject_lesson_15': self.tb230_course.text(),
            }

        # This will overwrite the existing schedule with the new one
            save_lessons([new_schedule])
            QMessageBox.information(self, "Success", "Course schedule saved/updated successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"An error occurred: {e}")

    def clear_schedule_form(self):
        # Clear the schedule form for all QLineEdit and QComboBox widgets
        self.tb21_course.clear()
        self.cb21_course.setCurrentIndex(0)
        self.tb22_course.clear()
        self.tb23_course.clear()
        self.cb22_course.setCurrentIndex(0)
        self.tb24_course.clear()
        self.tb25_course.clear()
        self.cb23_course.setCurrentIndex(0)
        self.tb26_course.clear()
        self.tb27_course.clear()
        self.cb24_course.setCurrentIndex(0)
        self.tb28_course.clear()
        self.tb29_course.clear()
        self.cb25_course.setCurrentIndex(0)
        self.tb210_course.clear()
        self.tb211_course.clear()
        self.cb26_course.setCurrentIndex(0)
        self.tb212_course.clear()
        self.tb213_course.clear()
        self.cb27_course.setCurrentIndex(0)
        self.tb214_course.clear()
        self.tb215_course.clear()
        self.cb28_course.setCurrentIndex(0)
        self.tb216_course.clear()
        self.tb217_course.clear()
        self.cb29_course.setCurrentIndex(0)
        self.tb218_course.clear()
        self.tb219_course.clear()
        self.cb210_course.setCurrentIndex(0)
        self.tb220_course.clear()
        self.tb221_course.clear()
        self.cb211_course.setCurrentIndex(0)
        self.tb222_course.clear()
        self.tb223_course.clear()
        self.cb212_course.setCurrentIndex(0)
        self.tb224_course.clear()
        self.tb225_course.clear()
        self.cb213_course.setCurrentIndex(0)
        self.tb226_course.clear()
        self.tb227_course.clear()
        self.cb214_course.setCurrentIndex(0)
        self.tb228_course.clear()
        self.tb229_course.clear()
        self.cb215_course.setCurrentIndex(0)
        self.tb230_course.clear()

#############################################################################################################

class LoginApp(QDialog):
    def __init__(self):
        super(LoginApp, self).__init__()
        loadUi("login_form.ui", self)
        self.b1.clicked.connect(self.login)
        self.b2.clicked.connect(self.show_reg)
        self.tb2.returnPressed.connect(self.login)
        
    def login(self):
        email = self.tb1.text()
        password = self.tb2.text()
        users = load_users()
        user = next((user for user in users if user['email'] == email and user['password'] == password), None)
        if user:
            if is_admin(user):
                self.admin_app = AdminApp()
                self.admin_app.show()
                
            elif is_student(user):
                self.student_app = StudentApp(email)
                self.student_app.show()
                
            elif is_teacher(user):
                self.teacher_app = TeacherApp(email)
                self.teacher_app.show()
        
            else:
                QMessageBox.information(self, "Login Output", "Login Successful")
        else:
            QMessageBox.warning(self, "Login Output", "Invalid email or password")

    def show_reg(self):
        global widget
        widget.setCurrentIndex(1)

#############################################################################################################

class RegApp(QDialog):
    def __init__(self):
        super(RegApp, self).__init__()
        loadUi("register_form.ui", self)
        self.b3.clicked.connect(self.reg)
        self.b4.clicked.connect(self.show_login)
        self.fill_studentId()

    def fill_studentId(self):
        users = load_users()
        studentId = sum(1 for user in users if user.get('type') == 'student') + 1
        self.tb_sId.setText(str(studentId))
    
    def reg(self):
        studentId = self.tb_sId.text()
        email = self.tb3.text()
        password = self.tb4.text()
        name = self.tb5.text()
        surname = self.tb6.text()
        gender = self.cb1_reg.currentText()
        date_of_birth = self.tb7.text()
        phone = self.tb8.text()
        
        if not is_valid_email(email) or not is_valid_password(password) or not is_valid_phone(phone):
            QMessageBox.warning(self, "Registration Error", "Invalid input format")
            return

        users = load_users()
        if any(user['email'] == email for user in users):
            QMessageBox.warning(self, "Registration Error", "User Already Exists!!")
            return
        else:
            users.append({
                'studentId': studentId,
                'email': email,
                'password': password,
                'name': name,
                'surname': surname,
                'gender': gender,
                'date_of_birth': date_of_birth,
                'phone': phone,
                'type': 'student'
            })
            save_users(users)
            QMessageBox.information(self, "Registration Successful", "User Registered Successfully, YOU CAN NOW LOGIN!!")
            self.clear_registration_form()

    def clear_registration_form(self):
        self.tb_sId.clear()
        self.tb3.clear()
        self.tb4.clear()
        self.tb5.clear()
        self.tb6.clear()
        self.cb1_reg.setCurrentIndex(0)
        self.tb7.clear()
        self.tb8.clear()

    def show_login(self):
        global widget
        widget.setCurrentIndex(0)

#############################################################################################################
          
class StudentApp(QMainWindow):
    def __init__(self, email):
        super(StudentApp, self).__init__()
        loadUi("student.ui", self)
        self.email = email
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.tabBar().setVisible(False)
        self.menu11.triggered.connect(self.edit_profile_tab)
        self.menu71.triggered.connect(self.close)  # Logout from student menu

        self.b6.clicked.connect(self.update_student_details)  
        
    def edit_profile_tab(self):
        self.tabWidget.setCurrentIndex(1)
        self.load_student_details()

    def load_student_details(self):
        users = load_users()
        for user in users:
            if user.get('type') == 'student' and user['email'] == self.email:
                # Load the student's details into the form
                self.tb21.setText(user.get('studentId', ''))  
                self.tb22.setText(user.get('email', ''))  
                self.tb23.setText(user.get('name', ''))  
                self.tb24.setText(user.get('surname', ''))  
                self.cb11_st.setCurrentText(user.get('gender', ''))  
                self.tb25.setText(user.get('date_of_birth', ''))  
                self.tb26.setText(user.get('phone', ''))  
                self.tb27.setText(user.get('password', ''))  
                break

    def update_student_details(self):
        student_id = self.tb21.text()
        email = self.tb22.text()
        name = self.tb23.text()
        surname = self.tb24.text()
        gender = self.cb11_st.currentText()
        date_of_birth = self.tb25.text()
        phone = self.tb26.text()
        password = self.tb27.text()

        if not is_valid_email(email) or not is_valid_password(password) or not is_valid_phone(phone):
            QMessageBox.warning(self, "Update Error", "Invalid input format")
            return

        users = load_users()
        for i, user in enumerate(users):
            if user.get('type') == 'student' and user['email'] == self.email:
                users[i].update({
                    'studentId': student_id,
                    'email': email,
                    'name': name,
                    'surname': surname,
                    'gender': gender,
                    'date_of_birth': date_of_birth,
                    'phone': phone,
                    'password': password
                })
                break
        save_users(users)
        QMessageBox.information(self, "Update Success", "Student details updated successfully.")
#############################################################################################################

# Main Application Setup
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()
    login_form = LoginApp()
    registration_form = RegApp()
    email = ""
    student_form = StudentApp(email)
    teacher_form = TeacherApp(email)

    widget.addWidget(login_form)
    widget.addWidget(registration_form)
    widget.addWidget(student_form)
    widget.addWidget(teacher_form)
    widget.setFixedWidth(400)
    widget.setFixedHeight(650)
    widget.show()
    sys.exit(app.exec_())
    
#############################################################################################################
