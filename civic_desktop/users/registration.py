from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QLabel, QPushButton, 
	QHBoxLayout, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem, QDateEdit, 
	QComboBox, QCheckBox
)
from PyQt5.QtCore import QDate
from civic_desktop.users.backend import UserBackend
from civic_desktop.utils.validation import DataValidator
from civic_desktop.contracts.contract_ui import show_contract_acceptance_dialog

class RegistrationForm(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setWindowTitle("User Registration")
		self.fields = {}
		self.contracts_accepted = False
		self.id_document_path = None
		self._build_ui()

	def _build_ui(self):
		main_vbox = QVBoxLayout()
		main_vbox.setSpacing(18)
		main_vbox.setContentsMargins(40, 30, 40, 30)

		# Registration info group
		info_group = QGroupBox("Registration Information")
		info_group.setStyleSheet("QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #bbb; border-radius: 10px; background: #f8f8ff; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
		form_layout = QFormLayout()
		form_layout.setSpacing(12)

		# Name fields
		self.last_name_field = QLineEdit()
		form_layout.addRow("Legal Last Name", self.last_name_field)
		self.fields["last_name"] = self.last_name_field
		self.first_name_field = QLineEdit()
		form_layout.addRow("Legal First Name", self.first_name_field)
		self.fields["first_name"] = self.first_name_field

		# Date of Birth with proper date picker
		self.birth_date_edit = QDateEdit()
		self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
		self.birth_date_edit.setMaximumDate(QDate.currentDate())
		self.birth_date_edit.setMinimumDate(QDate(1900, 1, 1))
		self.birth_date_edit.dateChanged.connect(self.on_birth_date_changed)
		form_layout.addRow("Date of Birth", self.birth_date_edit)

		# Address fields
		self.address_field = QLineEdit()
		form_layout.addRow("Address of Residency (as on ID)", self.address_field)
		self.fields["address"] = self.address_field
		self.city_field = QLineEdit()
		form_layout.addRow("City", self.city_field)
		self.fields["city"] = self.city_field
		self.state_field = QLineEdit()
		form_layout.addRow("State", self.state_field)
		self.fields["state"] = self.state_field
		self.country_field = QLineEdit()
		form_layout.addRow("Country", self.country_field)
		self.fields["country"] = self.country_field

		# Government ID fields
		self.id_type_combo = QComboBox()
		self.id_type_combo.addItems(["Passport", "Driver's License", "State ID", "Military ID"])
		form_layout.addRow("Government ID Type", self.id_type_combo)
		
		self.id_number_field = QLineEdit()
		form_layout.addRow("Government ID Number", self.id_number_field)

		# Parental consent section (initially hidden)
		self.parental_consent_group = QGroupBox("Parental Consent (Required for under 18)")
		self.parental_consent_group.setVisible(False)
		parental_layout = QFormLayout()
		
		self.parent_name_field = QLineEdit()
		parental_layout.addRow("Parent/Guardian Name", self.parent_name_field)
		
		self.parent_email_field = QLineEdit()
		parental_layout.addRow("Parent/Guardian Email", self.parent_email_field)
		
		self.consent_checkbox = QCheckBox("I am the parent/guardian and consent to my child's participation")
		parental_layout.addRow("Consent", self.consent_checkbox)
		
		self.parental_consent_group.setLayout(parental_layout)
		form_layout.addRow(self.parental_consent_group)

		# Contact fields
		self.email_field = QLineEdit()
		form_layout.addRow("Email", self.email_field)
		self.fields["email"] = self.email_field

		# Password
		self.password_field = QLineEdit()
		self.password_field.setEchoMode(QLineEdit.Password)
		form_layout.addRow("Password", self.password_field)
		self.fields["password"] = self.password_field

		info_group.setLayout(form_layout)
		main_vbox.addWidget(info_group)

		# ID Document upload
		id_hbox = QHBoxLayout()
		self.id_label = QLabel("ID Document: Not selected")
		self.id_button = QPushButton("Upload ID Document")
		self.id_button.clicked.connect(self.upload_id)
		id_hbox.addWidget(self.id_label)
		id_hbox.addWidget(self.id_button)
		main_vbox.addLayout(id_hbox)

		# Contract acceptance section
		contract_group = QGroupBox("Governance Contract Acceptance")
		contract_group.setStyleSheet("QGroupBox { font-size: 15px; font-weight: bold; border: 1px solid #bbb; border-radius: 10px; background: #f8fff8; margin-top: 10px; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }")
		contract_vbox = QVBoxLayout()
		contract_info = QLabel("Before completing registration, you must review and accept the governance contracts that apply to your location. These establish the democratic rules for platform participation.")
		contract_info.setWordWrap(True)
		contract_vbox.addWidget(contract_info)
		contract_button_layout = QHBoxLayout()
		self.review_contracts_button = QPushButton("Review & Accept Contracts")
		self.review_contracts_button.clicked.connect(self.review_contracts)
		contract_button_layout.addWidget(self.review_contracts_button)
		self.contracts_status_label = QLabel("⚠ Contracts not yet accepted")
		self.contracts_status_label.setStyleSheet("color: red; font-weight: bold;")
		contract_button_layout.addWidget(self.contracts_status_label)
		contract_vbox.addLayout(contract_button_layout)
		contract_group.setLayout(contract_vbox)
		main_vbox.addWidget(contract_group)

		# Register button
		main_vbox.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
		self.register_button = QPushButton("Register")
		self.register_button.setStyleSheet("QPushButton { font-size: 15px; font-weight: bold; background: #4CAF50; color: white; border-radius: 6px; padding: 8px 24px; } QPushButton:hover { background: #388E3C; }")
		self.register_button.clicked.connect(self.register)
		main_vbox.addWidget(self.register_button)
		self.setLayout(main_vbox)

	def on_birth_date_changed(self):
		"""Show/hide parental consent based on age"""
		birth_date = self.birth_date_edit.date().toString("yyyy-MM-dd")
		valid, message, age = DataValidator.validate_birth_date(birth_date)
		
		if valid and age < 18:
			self.parental_consent_group.setVisible(True)
		else:
			self.parental_consent_group.setVisible(False)

	def upload_id(self):
		"""Upload ID document with security validation"""
		from civic_desktop.utils.validation import DataValidator
		
		file_path, _ = QFileDialog.getOpenFileName(
			self, 
			"Select ID Document",
			"",
			"Image files (*.jpg *.jpeg *.png *.pdf);;All Files (*)"
		)
		
		if file_path:
			# Validate file upload
			is_valid, message = DataValidator.validate_file_upload(file_path)
			if not is_valid:
				QMessageBox.warning(self, "Invalid File", f"File upload failed: {message}")
				return
			
			self.id_document_path = file_path
			import os
			filename = os.path.basename(file_path)
			self.id_label.setText(f"ID Document: {filename}")
			self.id_label.setStyleSheet("color: green; font-weight: bold;")

	def review_contracts(self):
		# Gather user location info for contract determination
		user_location = {
			"country": self.country_field.text().strip(),
			"state": self.state_field.text().strip(),
			"city": self.city_field.text().strip()
		}
		# Use the actual email for acceptance recording
		email = self.email_field.text().strip()
		if not email:
			QMessageBox.warning(self, "Email Required", "Please enter your email before reviewing contracts.")
			return
		# Open dialog and pass the email so acceptances are recorded correctly
		accepted = show_contract_acceptance_dialog(user_location, self, user_email=email)
		if accepted:
			# Record acceptance for this user
			from civic_desktop.contracts.contract_terms import contract_manager
			all_accepted, missing_contracts = contract_manager.check_all_required_accepted(email, user_location)
			if all_accepted:
				self.contracts_accepted = True
				self.contracts_status_label.setText("✓ All required contracts accepted")
				self.contracts_status_label.setStyleSheet("color: green; font-weight: bold;")
				self.review_contracts_button.setText("View Accepted Contracts")
			else:
				self.contracts_accepted = False
				self.contracts_status_label.setText("⚠ Contracts not yet accepted")
				self.contracts_status_label.setStyleSheet("color: red; font-weight: bold;")
				self.review_contracts_button.setText("Review & Accept Contracts")
		else:
			self.contracts_accepted = False
			self.contracts_status_label.setText("⚠ Contracts not yet accepted")
			self.contracts_status_label.setStyleSheet("color: red; font-weight: bold;")
			self.review_contracts_button.setText("Review & Accept Contracts")

	def register(self):
		# Collect data from all fields
		data = {k: f.text().strip() for k, f in self.fields.items()}
		
		# Add new fields for preliminary ranks system
		data["birth_date"] = self.birth_date_edit.date().toString("yyyy-MM-dd")
		data["id_type"] = self.id_type_combo.currentText()
		data["id_number"] = self.id_number_field.text().strip()
		data["id_document_path"] = self.id_document_path
		
		# Check if parental consent is required and provided
		birth_date = data["birth_date"]
		valid, message, age = DataValidator.validate_birth_date(birth_date)
		if valid and age < 18:
			if not self.consent_checkbox.isChecked():
				QMessageBox.warning(self, "Parental Consent Required", 
					"Parental consent is required for users under 18.")
				return
			
			# Validate parental consent fields
			parent_name = self.parent_name_field.text().strip()
			parent_email = self.parent_email_field.text().strip()
			
			valid_consent, consent_message = DataValidator.validate_parental_consent(
				parent_email, parent_name, data["email"]
			)
			if not valid_consent:
				QMessageBox.warning(self, "Invalid Parental Information", consent_message)
				return
			
			data["parental_consent"] = True
			data["parent_name"] = parent_name
			data["parent_email"] = parent_email
		else:
			data["parental_consent"] = False
			data["parent_name"] = ""
			data["parent_email"] = ""
		
		# Validate government ID
		valid_id, id_result = DataValidator.validate_government_id(
			data["id_number"], data["id_type"]
		)
		if not valid_id:
			QMessageBox.warning(self, "Invalid Government ID", id_result)
			return
		
		# Other existing validations...
		if not self.contracts_accepted:
			QMessageBox.warning(self, "Contracts Required", 
				"You must accept the governance contracts before registering.")
			return
		if not self.id_document_path:
			QMessageBox.warning(self, "ID Document Required", "Please upload your government ID document before registering.")
			return
		valid, msg, _ = DataValidator.validate_registration_data(data)
		if not valid:
			QMessageBox.warning(self, "Validation Error", msg)
			return
		success, result = UserBackend.register_user(data, self.id_document_path)
		if success:
			QMessageBox.information(self, "Registration Success", "Your account has been created.")
			self.clear_form()
		else:
			QMessageBox.critical(self, "Registration Failed", str(result))

	def clear_form(self):
		for f in self.fields.values():
			f.clear()
		
		# Clear new fields
		self.birth_date_edit.setDate(QDate.currentDate())
		self.id_type_combo.setCurrentIndex(0)
		self.id_number_field.clear()
		self.parent_name_field.clear()
		self.parent_email_field.clear()
		self.consent_checkbox.setChecked(False)
		self.parental_consent_group.setVisible(False)
		
		self.id_document_path = None
		self.id_label.setText("ID Document: Not selected")
		self.contracts_accepted = False
		self.contracts_status_label.setText("⚠ Contracts not yet accepted")
		self.contracts_status_label.setStyleSheet("color: red; font-weight: bold;")
		self.review_contracts_button.setText("Review & Accept Contracts")
