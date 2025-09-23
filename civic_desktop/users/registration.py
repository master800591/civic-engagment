from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, QLabel, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QSizePolicy, QSpacerItem
)
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

		# Date of Birth
		self.gov_dob_field = QLineEdit()
		form_layout.addRow("Date of Birth (YYYY-MM-DD)", self.gov_dob_field)

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
		self.gov_id_type_field = QLineEdit()
		form_layout.addRow("Government ID Type", self.gov_id_type_field)
		self.gov_id_number_field = QLineEdit()
		form_layout.addRow("Government ID Number", self.gov_id_number_field)

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
		# Example validation and backend call
		data = {k: f.text().strip() for k, f in self.fields.items()}
		data["dob"] = self.gov_dob_field.text().strip()
		data["gov_id_type"] = self.gov_id_type_field.text().strip()
		data["gov_id_number"] = self.gov_id_number_field.text().strip()
		data["id_document_path"] = self.id_document_path
		if not self.contracts_accepted:
			QMessageBox.warning(self, "Contracts Required", "You must accept the governance contracts before registering.")
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
		self.gov_dob_field.clear()
		self.gov_id_type_field.clear()
		self.gov_id_number_field.clear()
		self.id_label.setText("ID Document: Not selected")
		self.contracts_accepted = False
		self.contracts_status_label.setText("⚠ Contracts not yet accepted")
		self.contracts_status_label.setStyleSheet("color: red; font-weight: bold;")
		self.review_contracts_button.setText("Review & Accept Contracts")
