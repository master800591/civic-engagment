# Training Module - UI Components for civic education and role-based training
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QTabWidget, QTextEdit, QFrame, QGroupBox,
                            QProgressBar, QListWidget, QListWidgetItem, QDialog,
                            QRadioButton, QButtonGroup, QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QColor
from .backend import TrainingBackend
from ..users.session import SessionManager
from ..users.backend import UserBackend


class TrainingTab(QWidget):
    """Main training interface for civic education"""
    
    def __init__(self):
        super().__init__()
        self.current_course = None
        self.current_module = None
        self.init_ui()
        # Don't call refresh_content in __init__ since user might not be logged in yet
    
    def init_ui(self):
        """Initialize the training interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        # Blockchain status and user role display
        from civic_desktop.users.session import SessionManager
        user = SessionManager.get_current_user()
        role = user.get('role', 'Unknown') if user else 'Unknown'
        blockchain_status = QLabel("All training completions are <b>recorded on blockchain</b> for audit and transparency.")
        blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
        role_label = QLabel(f"Your Role: <b>{role}</b>")
        role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
        export_btn = QPushButton("Export Training Report")
        export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 5px; padding: 8px 18px;")
        export_btn.clicked.connect(self.open_reports_tab)
        top_layout = QVBoxLayout()
        top_layout.addWidget(blockchain_status)
        top_layout.addWidget(role_label)
        top_layout.addWidget(export_btn)
        layout.addLayout(top_layout)
        # Header
        header = QLabel("🎓 Civic Training & Education Center")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
                color: white;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        # Create main content container
        self.main_content = QWidget()
        layout.addWidget(self.main_content)
        self.setLayout(layout)
        self.refresh_ui()

    def open_reports_tab(self):
        mw = self.parent()
        while mw and not hasattr(mw, 'tabs'):
            mw = mw.parent()
        if mw and hasattr(mw, 'tabs'):
            for i in range(mw.tabs.count()):
                if mw.tabs.tabText(i).lower().startswith("📊 reports") or mw.tabs.tabText(i).lower().startswith("reports"):
                    mw.tabs.setCurrentIndex(i)
                    break
    
    def refresh_ui(self):
        """Refresh the entire UI based on authentication status"""
        # Clear existing content
        if hasattr(self, 'main_content'):
            # Remove all widgets from main_content
            layout = self.main_content.layout()
            if layout:
                while layout.count():
                    child = layout.takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                layout = QVBoxLayout()
                self.main_content.setLayout(layout)
        
        # Check if user is logged in
        if not SessionManager.is_authenticated():
            self.show_login_required()
            return
        
        # Create main content area for logged-in users
        self.create_main_content()
        self.refresh_content()
    
    def create_main_content(self):
        """Create the main content area for logged-in users"""
        layout = self.main_content.layout()
        
        # Main content area
        splitter = QSplitter()
        
        # Left panel - Course list and progress
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # Right panel - Course content
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        splitter.setSizes([300, 700])
        layout.addWidget(splitter)
    
    def show_login_required(self):
        """Show login required message"""
        layout = self.main_content.layout()
        
        login_required = QLabel("🔐 Please log in to access the training center")
        login_required.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: #e74c3c;
                text-align: center;
                padding: 40px;
                background: #fdf2f2;
                border: 2px dashed #e74c3c;
                border-radius: 10px;
                margin: 20px;
            }
        """)
        login_required.setAlignment(Qt.AlignCenter)
        layout.addWidget(login_required)
    
    def create_left_panel(self) -> QWidget:
        """Create the left panel with course list and progress"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # User progress summary
        progress_group = QGroupBox("📊 Your Training Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_summary = QLabel("Loading progress...")
        progress_layout.addWidget(self.progress_summary)
        
        self.overall_progress = QProgressBar()
        progress_layout.addWidget(self.overall_progress)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # Available courses
        courses_group = QGroupBox("📚 Available Courses")
        courses_layout = QVBoxLayout()
        
        self.course_list = QListWidget()
        self.course_list.itemClicked.connect(self.load_course)
        courses_layout.addWidget(self.course_list)
        
        courses_group.setLayout(courses_layout)
        layout.addWidget(courses_group)
        
        # Current certifications
        certs_group = QGroupBox("🏆 Your Certifications")
        certs_layout = QVBoxLayout()
        
        self.certifications_list = QListWidget()
        certs_layout.addWidget(self.certifications_list)
        
        certs_group.setLayout(certs_layout)
        layout.addWidget(certs_group)
        
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Create the right panel for course content"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Course header
        self.course_header = QLabel("Select a course to begin")
        self.course_header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: #ecf0f1;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(self.course_header)
        
        # Course tabs
        self.course_tabs = QTabWidget()
        self.course_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
                font-weight: bold;
            }
        """)
        
        # Overview tab
        self.overview_tab = QScrollArea()
        self.overview_content = QTextEdit()
        self.overview_content.setReadOnly(True)
        self.overview_tab.setWidget(self.overview_content)
        self.course_tabs.addTab(self.overview_tab, "📋 Overview")
        
        # Modules tab
        self.modules_tab = self.create_modules_tab()
        self.course_tabs.addTab(self.modules_tab, "📖 Modules")
        
        # Progress tab
        self.progress_tab = self.create_progress_tab()
        self.course_tabs.addTab(self.progress_tab, "📈 Progress")
        
        layout.addWidget(self.course_tabs)
        
        panel.setLayout(layout)
        return panel
    
    def create_modules_tab(self) -> QWidget:
        """Create the modules tab for course content"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Module selector
        self.module_list = QListWidget()
        self.module_list.itemClicked.connect(self.load_module)
        layout.addWidget(self.module_list)
        
        # Module content area
        self.module_content = QTextEdit()
        self.module_content.setReadOnly(True)
        layout.addWidget(self.module_content)
        
        # Module actions
        actions_layout = QHBoxLayout()
        
        self.take_quiz_btn = QPushButton("📝 Take Quiz")
        self.take_quiz_btn.clicked.connect(self.take_quiz)
        self.take_quiz_btn.setEnabled(False)
        actions_layout.addWidget(self.take_quiz_btn)
        
        self.complete_module_btn = QPushButton("✅ Complete Module")
        self.complete_module_btn.clicked.connect(self.complete_module)
        self.complete_module_btn.setEnabled(False)
        actions_layout.addWidget(self.complete_module_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_progress_tab(self) -> QWidget:
        """Create the progress tracking tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.detailed_progress = QTextEdit()
        self.detailed_progress.setReadOnly(True)
        layout.addWidget(self.detailed_progress)
        
        widget.setLayout(layout)
        return widget
    
    def refresh_content(self):
        """Refresh all training content and progress"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        self.refresh_course_list()
        self.refresh_progress()
        self.refresh_certifications()
    
    def refresh_course_list(self):
        """Refresh the list of available courses"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        self.course_list.clear()
        courses = TrainingBackend.get_available_courses(user['email'])
        
        for course in courses:
            # Check if course is completed
            user_progress = TrainingBackend.get_user_progress(user['email'])
            completed = course['id'] in user_progress.get('completed_courses', [])
            
            item_text = f"{course['title']}"
            if completed:
                item_text += " ✅"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, course)
            
            # Style based on completion status
            if completed:
                item.setBackground(Qt.lightGray)
            
            self.course_list.addItem(item)
    
    def refresh_progress(self):
        """Refresh user progress display"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        progress = TrainingBackend.get_user_progress(user['email'])
        completed_courses = len(progress.get('completed_courses', []))
        available_courses = len(TrainingBackend.get_available_courses(user['email']))
        
        if available_courses > 0:
            progress_percent = int((completed_courses / available_courses) * 100)
            self.overall_progress.setValue(progress_percent)
            
            self.progress_summary.setText(
                f"Completed: {completed_courses}/{available_courses} courses ({progress_percent}%)"
            )
        else:
            self.overall_progress.setValue(0)
            self.progress_summary.setText("No courses available for your role")
    
    def refresh_certifications(self):
        """Refresh certifications display with blockchain verification"""
        user = SessionManager.get_current_user()
        if not user:
            return
        
        progress = TrainingBackend.get_user_progress(user['email'])
        certifications = progress.get('certifications', [])
        
        self.certifications_list.clear()
        for cert in certifications:
            # Verify certification on blockchain
            is_verified = TrainingBackend.verify_certification_on_blockchain(
                cert['certification_id'], user['email']
            )
            
            verification_icon = "✅" if is_verified else "❌"
            item_text = f"🏆 {cert['course_title']} {verification_icon}"
            item = QListWidgetItem(item_text)
            
            tooltip_text = f"""Certification ID: {cert['certification_id']}
Completed: {cert['completed_at']}
Blockchain Verified: {'Yes' if is_verified else 'No'}
Course: {cert['course_title']}"""
            
            item.setToolTip(tooltip_text)
            self.certifications_list.addItem(item)
    
    def load_course(self, item):
        """Load selected course content"""
        course = item.data(Qt.UserRole)
        if not course:
            return
        
        self.current_course = course
        
        # Update course header
        self.course_header.setText(f"📚 {course['title']}")
        
        # Load overview
        overview_html = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50;">{course['title']}</h2>
            <p><strong>Description:</strong> {course['description']}</p>
            <p><strong>Estimated Time:</strong> {course['estimated_time']}</p>
            <p><strong>Difficulty:</strong> {course['difficulty']}</p>
            
            {f"<p><strong>Prerequisites:</strong> {', '.join(course.get('prerequisite_courses', []))}</p>" if course.get('prerequisite_courses') else ""}
            
            <h3 style="color: #27ae60;">Course Modules:</h3>
            <ul>
        """
        
        for i, module in enumerate(course['modules'], 1):
            overview_html += f"<li><strong>Module {i}:</strong> {module['title']}</li>"
        
        overview_html += "</ul></div>"
        
        self.overview_content.setHtml(overview_html)
        
        # Load modules
        self.load_modules()
        
        # Load progress
        self.load_course_progress()
        
        # Check if user can start course
        user = SessionManager.get_current_user()
        if user:
            user_progress = TrainingBackend.get_user_progress(user['email'])
            if course['id'] not in user_progress.get('completed_courses', []):
                if course['id'] != user_progress.get('current_course'):
                    # Offer to start course
                    reply = QMessageBox.question(
                        self, "Start Course",
                        f"Would you like to start the course '{course['title']}'?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.Yes:
                        success, message = TrainingBackend.start_course(user['email'], course['id'])
                        if success:
                            QMessageBox.information(self, "Course Started", message)
                            self.refresh_content()
                        else:
                            QMessageBox.warning(self, "Error", message)
    
    def load_modules(self):
        """Load course modules"""
        if not self.current_course:
            return
        
        self.module_list.clear()
        user = SessionManager.get_current_user()
        if not user:
            return
        
        user_progress = TrainingBackend.get_user_progress(user['email'])
        completed_modules = user_progress.get('module_progress', {}).get(self.current_course['id'], {}).get('completed_modules', [])
        
        for i, module in enumerate(self.current_course['modules']):
            item_text = f"Module {i+1}: {module['title']}"
            if module['id'] in completed_modules:
                item_text += " ✅"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, module)
            
            if module['id'] in completed_modules:
                item.setBackground(Qt.lightGray)
            
            self.module_list.addItem(item)
    
    def load_module(self, item):
        """Load selected module content"""
        module = item.data(Qt.UserRole)
        if not module:
            return
        
        self.current_module = module
        
        # Display module content
        self.module_content.setHtml(module['content'])
        
        # Enable quiz button if module has quiz
        has_quiz = 'quiz' in module and len(module['quiz']) > 0
        self.take_quiz_btn.setEnabled(has_quiz)
        
        # Enable complete button
        self.complete_module_btn.setEnabled(True)
    
    def load_course_progress(self):
        """Load detailed course progress"""
        if not self.current_course:
            return
        
        user = SessionManager.get_current_user()
        if not user:
            return
        
        user_progress = TrainingBackend.get_user_progress(user['email'])
        course_progress = user_progress.get('module_progress', {}).get(self.current_course['id'], {})
        
        progress_html = f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h3>Course Progress: {self.current_course['title']}</h3>
        """
        
        if course_progress:
            completed_modules = course_progress.get('completed_modules', [])
            total_modules = len(self.current_course['modules'])
            progress_percent = int((len(completed_modules) / total_modules) * 100) if total_modules > 0 else 0
            
            progress_html += f"""
            <p><strong>Overall Progress:</strong> {len(completed_modules)}/{total_modules} modules ({progress_percent}%)</p>
            <p><strong>Started:</strong> {course_progress.get('started_at', 'Not started')}</p>
            
            <h4>Module Status:</h4>
            <ul>
            """
            
            for i, module in enumerate(self.current_course['modules']):
                status = "✅ Completed" if module['id'] in completed_modules else "⏳ Not started"
                progress_html += f"<li><strong>Module {i+1}:</strong> {module['title']} - {status}</li>"
            
            progress_html += "</ul>"
            
            # Show quiz scores if available
            quiz_scores = user_progress.get('quiz_scores', {}).get(self.current_course['id'], {})
            if quiz_scores:
                progress_html += "<h4>Quiz Scores:</h4><ul>"
                for module_id, score in quiz_scores.items():
                    module_title = next((m['title'] for m in self.current_course['modules'] if m['id'] == module_id), module_id)
                    progress_html += f"<li>{module_title}: {score:.1f}%</li>"
                progress_html += "</ul>"
            
            # Add blockchain verification section
            progress_html += """
            <h4>⛓️ Blockchain Verification:</h4>
            <p style="color: #27ae60;">All training progress is permanently recorded on the blockchain for verification and audit purposes.</p>
            """
            
            # Get blockchain records for this user
            blockchain_records = TrainingBackend.get_blockchain_training_records(user['email'])
            course_records = [r for r in blockchain_records if r['data'].get('course_id') == self.current_course['id']]
            
            if course_records:
                progress_html += "<h5>Blockchain Records for this Course:</h5><ul>"
                for record in course_records:
                    action = record['action_type'].replace('training_', '').replace('_', ' ').title()
                    timestamp = record['timestamp']
                    progress_html += f"<li><strong>{action}:</strong> {timestamp} (Block #{record['index']})</li>"
                progress_html += "</ul>"
            else:
                progress_html += "<p style='color: #666;'>No blockchain records found for this course yet.</p>"
                
        else:
            progress_html += "<p>Course not started yet.</p>"
        
        progress_html += "</div>"
        self.detailed_progress.setHtml(progress_html)
    
    def take_quiz(self):
        """Open quiz dialog for current module"""
        if not self.current_module or 'quiz' not in self.current_module:
            return
        
        quiz_dialog = QuizDialog(self.current_module['quiz'], self)
        if quiz_dialog.exec_() == QDialog.Accepted:
            score = quiz_dialog.get_score()
            QMessageBox.information(
                self, "Quiz Completed", 
                f"Quiz completed! Score: {score:.1f}%"
            )
            
            # Record quiz completion
            user = SessionManager.get_current_user()
            if user:
                TrainingBackend.complete_module(
                    user['email'], 
                    self.current_course['id'], 
                    self.current_module['id'], 
                    score
                )
                self.refresh_content()
                self.load_course_progress()
    
    def complete_module(self):
        """Mark current module as completed"""
        if not self.current_module or not self.current_course:
            return
        
        user = SessionManager.get_current_user()
        if not user:
            return
        
        success, message = TrainingBackend.complete_module(
            user['email'], 
            self.current_course['id'], 
            self.current_module['id']
        )
        
        if success:
            QMessageBox.information(self, "Module Completed", message)
            self.refresh_content()
            self.load_modules()
            self.load_course_progress()
        else:
            QMessageBox.warning(self, "Error", message)


class QuizDialog(QDialog):
    """Dialog for taking module quizzes"""
    
    def __init__(self, quiz_questions, parent=None):
        super().__init__(parent)
        self.quiz_questions = quiz_questions
        self.answers = {}
        self.init_ui()
    
    def init_ui(self):
        """Initialize quiz dialog"""
        self.setWindowTitle("📝 Module Quiz")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("📝 Module Quiz")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(header)
        
        # Instructions
        instructions = QLabel("Answer all questions and click Submit to complete the quiz.")
        instructions.setStyleSheet("color: #6c757d; margin-bottom: 20px;")
        layout.addWidget(instructions)
        
        # Scroll area for questions
        scroll = QScrollArea()
        questions_widget = QWidget()
        questions_layout = QVBoxLayout()
        
        self.button_groups = []
        
        for i, question in enumerate(self.quiz_questions):
            # Question frame
            q_frame = QFrame()
            q_frame.setFrameStyle(QFrame.StyledPanel)
            q_layout = QVBoxLayout()
            
            # Question text
            q_label = QLabel(f"<b>Question {i+1}:</b> {question['question']}")
            q_label.setWordWrap(True)
            q_layout.addWidget(q_label)
            
            # Answer options
            button_group = QButtonGroup()
            self.button_groups.append(button_group)
            
            for j, option in enumerate(question['options']):
                radio = QRadioButton(option)
                button_group.addButton(radio, j)
                q_layout.addWidget(radio)
            
            q_frame.setLayout(q_layout)
            questions_layout.addWidget(q_frame)
        
        questions_widget.setLayout(questions_layout)
        scroll.setWidget(questions_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        submit_btn = QPushButton("Submit Quiz")
        submit_btn.clicked.connect(self.submit_quiz)
        submit_btn.setDefault(True)
        buttons_layout.addWidget(submit_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def submit_quiz(self):
        """Submit quiz and calculate score"""
        # Check if all questions are answered
        for i, group in enumerate(self.button_groups):
            if group.checkedId() == -1:
                QMessageBox.warning(
                    self, "Incomplete Quiz", 
                    f"Please answer question {i+1} before submitting."
                )
                return
        
        # Calculate score
        correct_answers = 0
        total_questions = len(self.quiz_questions)
        
        for i, group in enumerate(self.button_groups):
            selected = group.checkedId()
            correct = self.quiz_questions[i]['correct']
            if selected == correct:
                correct_answers += 1
        
        self.score = (correct_answers / total_questions) * 100
        
        # Show results
        result_text = f"Score: {correct_answers}/{total_questions} ({self.score:.1f}%)"
        
        if self.score >= 70:
            result_text += "\\n\\n✅ Passed! You may proceed to the next module."
            self.accept()
        else:
            result_text += "\\n\\n❌ Score below 70%. Please review the material and retake the quiz."
            QMessageBox.information(self, "Quiz Results", result_text)
    
    def get_score(self):
        """Get quiz score"""
        return getattr(self, 'score', 0.0)