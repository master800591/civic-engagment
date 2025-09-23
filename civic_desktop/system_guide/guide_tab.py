# System Guide Module - Comprehensive User Guide and Documentation
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QScrollArea, QTabWidget, QTextEdit, QFrame, QGroupBox,
                            QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from ..users.session import SessionManager
from ..users.backend import UserBackend


class SystemGuideTab(QWidget):
    """Comprehensive system guide and documentation for users"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the system guide interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("🏛️ Civic Engagement Platform - Complete System Guide")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Create tabbed guide sections
        self.guide_tabs = QTabWidget()
        self.guide_tabs.setStyleSheet("""
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
        
        # Add guide sections
        self.guide_tabs.addTab(self.overview_section(), "📋 Overview")
        self.guide_tabs.addTab(self.roles_section(), "👥 Roles & Titles")
        self.guide_tabs.addTab(self.governance_section(), "🏛️ Governance")
        self.guide_tabs.addTab(self.participation_section(), "🗳️ Participation")
        self.guide_tabs.addTab(self.blockchain_section(), "⛓️ Blockchain")
        self.guide_tabs.addTab(self.getting_started_section(), "🚀 Getting Started")
        
        layout.addWidget(self.guide_tabs)
        self.setLayout(layout)
    
    def overview_section(self) -> QWidget:
        """Platform overview and mission"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">🌟 Platform Mission</h2>
            <p><strong>The Civic Engagement Platform</strong> is a revolutionary democratic governance system that combines cutting-edge technology with time-tested democratic principles to create a transparent, accountable, and participatory civic experience.</p>
            
            <h3 style="color: #27ae60;">🎯 Core Objectives</h3>
            <ul>
                <li><strong>Democratic Transparency:</strong> All governance actions recorded on an immutable blockchain</li>
                <li><strong>Citizen Empowerment:</strong> Direct participation in policy debates and elections</li>
                <li><strong>Constitutional Protection:</strong> Multi-layered safeguards against tyranny and abuse</li>
                <li><strong>Professional Governance:</strong> Role-based system with proper checks and balances</li>
            </ul>
            
            <h3 style="color: #e74c3c;">🛡️ Anti-Tyranny Design</h3>
            <p>The platform is specifically designed to prevent both <em>majority tyranny</em> and <em>minority rule</em> through:</p>
            <ul>
                <li><strong>Separation of Powers:</strong> Legislative, Executive, and Judicial branches</li>
                <li><strong>Constitutional Limits:</strong> Fundamental rights that cannot be voted away</li>
                <li><strong>Geographic Representation:</strong> Ensuring all regions have a voice</li>
                <li><strong>Supermajority Requirements:</strong> Major changes require broad consensus</li>
                <li><strong>Term Limits:</strong> Preventing entrenched power structures</li>
            </ul>
            
            <h3 style="color: #9b59b6;">⚖️ Key Features</h3>
            <ul>
                <li><strong>Smart Contract Governance:</strong> Rules enforced by technology, not just trust</li>
                <li><strong>Real-time Voting:</strong> Instant democratic participation</li>
                <li><strong>Debate Platform:</strong> Structured policy discussions with argument threading</li>
                <li><strong>Moderation System:</strong> Community-driven content oversight with due process</li>
                <li><strong>Election Management:</strong> Secure, transparent elections for all positions</li>
                <li><strong>Audit Trail:</strong> Complete record of all platform activity</li>
            </ul>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        def init_ui(self):
            """Initialize the system guide interface"""
            layout = QVBoxLayout()
            layout.setContentsMargins(10, 10, 10, 10)
            # Blockchain status and user role display
            from civic_desktop.users.session import SessionManager
            user = SessionManager.get_current_user()
            role = user.get('role', 'Unknown') if user else 'Unknown'
            blockchain_status = QLabel("All system guide updates are <b>recorded on blockchain</b> for audit and transparency.")
            blockchain_status.setStyleSheet("color: #007bff; font-size: 13px; margin-bottom: 8px;")
            role_label = QLabel(f"Your Role: <b>{role}</b>")
            role_label.setStyleSheet("color: #343a40; font-size: 13px; margin-bottom: 8px;")
            export_btn = QPushButton("Export Guide Report")
            export_btn.setStyleSheet("background-color: #28a745; color: white; font-weight: bold; border-radius: 5px; padding: 8px 18px;")
            export_btn.clicked.connect(self.open_reports_tab)
            top_layout = QVBoxLayout()
            top_layout.addWidget(blockchain_status)
            top_layout.addWidget(role_label)
            top_layout.addWidget(export_btn)
            layout.addLayout(top_layout)
            # Header
            header = QLabel("🏛️ Civic Engagement Platform - Complete System Guide")
            header.setStyleSheet("""
                QLabel {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 15px;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    border-radius: 10px;
                    margin-bottom: 10px;
                }
            """)
            header.setAlignment(Qt.AlignCenter)
            layout.addWidget(header)
            # Create tabbed guide sections
            self.guide_tabs = QTabWidget()
            self.guide_tabs.setStyleSheet("""
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
            # ...existing code...

        def open_reports_tab(self):
            mw = self.parent()
            while mw and not hasattr(mw, 'tabs'):
                mw = mw.parent()
            if mw and hasattr(mw, 'tabs'):
                for i in range(mw.tabs.count()):
                    if mw.tabs.tabText(i).lower().startswith("📊 reports") or mw.tabs.tabText(i).lower().startswith("reports"):
                        mw.tabs.setCurrentIndex(i)
                        break
                </ul>
                <p><strong>Limitations:</strong></p>
                <ul>
                    <li>Cannot initiate legislation or policy</li>
                    <li>Cannot directly govern without other branch approval</li>
                    <li>Subject to citizen recall (55% turnout + 60% approval required)</li>
                </ul>
                <p><strong>Term:</strong> 4 years, renewable, maximum 3 consecutive terms</p>
                <p><strong>Selection:</strong> Elected by Representatives and Senators combined (55% approval)</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">
                <h3 style="color: #007bff; margin-top: 0;">🏛️ Contract Senators (Deliberative Upper House)</h3>
                <p><strong>Symbol:</strong> 🏛️ Senator [Name]</p>
                <p><strong>Authority Level:</strong> Legislative Review</p>
                <p><strong>Powers:</strong></p>
                <ul>
                    <li><strong>Legislative Review:</strong> Must approve all Representative proposals</li>
                    <li><strong>Deliberative Delay:</strong> Require 30-day cooling-off period for major decisions</li>
                    <li><strong>Confirmation Authority:</strong> Approve major appointments and platform changes</li>
                    <li><strong>Override Power:</strong> Override Elder vetoes with 67% supermajority</li>
                </ul>
                <p><strong>Limitations:</strong></p>
                <ul>
                    <li>Cannot initiate spending or taxation proposals</li>
                    <li>Cannot override Contract Founder emergency powers</li>
                    <li>Subject to citizen recall with same threshold as Elders</li>
                </ul>
                <p><strong>Term:</strong> 6 years, maximum 2 consecutive terms</p>
                <p><strong>Selection:</strong> Mixed system - 1/3 by Representatives, 1/3 by citizens, 1/3 by Elders</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #28a745; margin: 10px 0;">
                <h3 style="color: #28a745; margin-top: 0;">🗳️ Contract Representatives (House of the People)</h3>
                <p><strong>Symbol:</strong> 🗳️ Representative [Name]</p>
                <p><strong>Authority Level:</strong> Legislative Initiative</p>
                <p><strong>Powers:</strong></p>
                <ul>
                    <li><strong>Legislative Initiative:</strong> Create and propose new platform policies</li>
                    <li><strong>Budget Authority:</strong> Control platform resource allocation</li>
                    <li><strong>Impeachment Power:</strong> Impeach Senators, Elders, or Founders (60% vote)</li>
                    <li><strong>Platform Oversight:</strong> Monitor and investigate platform operations</li>
                </ul>
                <p><strong>Limitations:</strong></p>
                <ul>
                    <li>All proposals subject to Elder veto review</li>
                    <li>Cannot override Elder constitutional interpretations</li>
                    <li>Decisions require bicameral approval from Senators</li>
                </ul>
                <p><strong>Term:</strong> 2 years, unlimited terms</p>
                <p><strong>Selection:</strong> Direct election by citizens within geographic jurisdiction</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0;">
                <h3 style="color: #fd7e14; margin-top: 0;">👤 Contract Citizens (Sovereign Authority)</h3>
                <p><strong>Symbol:</strong> 👤 Citizen [Name]</p>
                <p><strong>Authority Level:</strong> Democratic Foundation</p>
                <p><strong>Powers:</strong></p>
                <ul>
                    <li><strong>Electoral Authority:</strong> Vote in all elections and referendums</li>
                    <li><strong>Initiative Power:</strong> Propose constitutional amendments (40% petition + 55% approval)</li>
                    <li><strong>Recall Authority:</strong> Remove any elected official through special elections</li>
                    <li><strong>Platform Participation:</strong> Full debate, moderation, and governance participation</li>
                </ul>
                <p><strong>Protections:</strong></p>
                <ul>
                    <li><strong>Constitutional Rights:</strong> Cannot be overridden by any single branch</li>
                    <li><strong>Minority Protection:</strong> Geographic and demographic representation guarantees</li>
                    <li><strong>Due Process:</strong> Appeals process for any moderation or governance decisions</li>
                </ul>
                <p><strong>Term:</strong> Permanent (as long as account is active)</p>
                <p><strong>Selection:</strong> Automatic upon successful registration and verification</p>
            </div>
            
            <h3 style="color: #e74c3c;">💼 Leadership Titles</h3>
            <p>In addition to contract roles, users may hold executive positions:</p>
            <ul>
                <li><strong>💼 CEO:</strong> Chief Executive Officer - Platform leadership</li>
                <li><strong>📋 Director:</strong> Department Directors - Specialized management</li>
                <li><strong>📊 Manager:</strong> Team Managers - Operational oversight</li>
            </ul>
            
            <h3 style="color: #17a2b8;">🤖 System Accounts</h3>
            <p>Automated platform functions appear as:</p>
            <ul>
                <li><strong>🤖 Agent [Name]:</strong> System-generated content and automated processes</li>
                <li>Examples: 🤖 Agent Security Monitor, 🤖 Agent Blockchain Validator</li>
            </ul>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        return widget
    
    def governance_section(self) -> QWidget:
        """Governance structure and decision-making processes"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">⚖️ Governance Structure & Decision-Making</h2>
            
            <h3 style="color: #27ae60;">🔄 Regular Governance Process</h3>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <ol>
                    <li><strong>Proposal:</strong> Contract Representatives propose legislation</li>
                    <li><strong>Review:</strong> Contract Senators review and deliberate (30-day period for major changes)</li>
                    <li><strong>Constitutional Check:</strong> Contract Elders review for constitutional compliance</li>
                    <li><strong>Implementation:</strong> If no Elder veto → Automatic implementation</li>
                    <li><strong>Override Option:</strong> If Elder veto → Senators can override with 67% supermajority</li>
                </ol>
            </div>
            
            <h3 style="color: #e74c3c;">🚨 Constitutional Changes</h3>
            <div style="background: #fdf2f2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Platform Fundamentals require special process:</strong></p>
                <ol>
                    <li><strong>Initiation:</strong> Contract Founders (75%+ consensus) OR Citizen Initiative (40% petition)</li>
                    <li><strong>Legislative Approval:</strong> Representatives (60%+ vote) AND Senators (60%+ vote)</li>
                    <li><strong>Constitutional Review:</strong> Contract Elders review for compatibility</li>
                    <li><strong>Citizen Ratification:</strong> 55%+ turnout with 60%+ approval required</li>
                    <li><strong>Implementation:</strong> 6-month period with ongoing review process</li>
                </ol>
            </div>
            
            <h3 style="color: #f39c12;">⚡ Emergency Protocols</h3>
            <div style="background: #fef9e7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>For platform-threatening situations:</strong></p>
                <ol>
                    <li><strong>Declaration:</strong> Contract Founders emergency declaration (75%+ consensus)</li>
                    <li><strong>Immediate Action:</strong> 48-hour implementation period</li>
                    <li><strong>Elder Review:</strong> Contract Elders immediate constitutional review</li>
                    <li><strong>Legislative Session:</strong> Contract Senators emergency session within 7 days</li>
                    <li><strong>Citizen Oversight:</strong> Citizen referendum within 30 days to confirm/overturn</li>
                </ol>
            </div>
            
            <h3 style="color: #9b59b6;">🤝 Conflict Resolution</h3>
            <div style="background: #f4f1fb; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>When branches disagree:</strong></p>
                <ol>
                    <li><strong>Mediation:</strong> Contract Elders attempt mediation</li>
                    <li><strong>Joint Session:</strong> Special combined session of Representatives + Senators</li>
                    <li><strong>Citizen Decision:</strong> If unresolved → Citizen referendum with 30-day debate</li>
                    <li><strong>Binding Resolution:</strong> Result binding with 55%+ turnout threshold</li>
                </ol>
            </div>
            
            <h3 style="color: #17a2b8;">🛡️ Anti-Tyranny Safeguards</h3>
            
            <h4>Preventing Majority Tyranny:</h4>
            <ul>
                <li><strong>Geographic Representation:</strong> Electoral college ensures small regions have voice</li>
                <li><strong>Supermajority Requirements:</strong> Major changes need 60-75% approval</li>
                <li><strong>Constitutional Rights:</strong> Fundamental rights cannot be voted away</li>
                <li><strong>Elder Veto:</strong> Wisdom council blocks harmful majority decisions</li>
                <li><strong>Bicameral Legislature:</strong> Both houses must approve major changes</li>
                <li><strong>Staggered Terms:</strong> Prevents sudden complete power shifts</li>
            </ul>
            
            <h4>Preventing Minority Rule:</h4>
            <ul>
                <li><strong>Popular Mandate:</strong> Representatives directly elected by citizen majority</li>
                <li><strong>Override Powers:</strong> Senators can override Elder vetoes with supermajority</li>
                <li><strong>Recall Mechanisms:</strong> Citizens can remove any official</li>
                <li><strong>Initiative Process:</strong> Citizens bypass government gridlock</li>
                <li><strong>Regular Elections:</strong> No permanent appointments (except Founders with removal)</li>
                <li><strong>Transparency:</strong> All decisions recorded on blockchain</li>
            </ul>
            
            <h3 style="color: #dc3545;">🔒 Constitutional Rights (Unchangeable)</h3>
            <ul>
                <li><strong>Free Expression:</strong> Right to speak, debate, and criticize governance</li>
                <li><strong>Due Process:</strong> Fair treatment in all procedures with appeal rights</li>
                <li><strong>Equal Participation:</strong> Equal access to platform features and democracy</li>
                <li><strong>Privacy Protection:</strong> Personal data security and limited surveillance</li>
                <li><strong>Equal Treatment:</strong> Protection from discrimination</li>
                <li><strong>Democratic Rights:</strong> Vote, run for office, petition government</li>
            </ul>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        return widget
    
    def participation_section(self) -> QWidget:
        """How to participate in different platform activities"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">🗳️ How to Participate</h2>
            
            <h3 style="color: #27ae60;">📝 Creating Debate Topics</h3>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Who Can Create:</strong> Contract Representatives and Contract Senators</p>
                <p><strong>Process:</strong></p>
                <ol>
                    <li>Go to the "Debates" tab</li>
                    <li>Click "Create New Topic"</li>
                    <li>Select appropriate jurisdiction level (City/State/Country/World)</li>
                    <li>Choose location from dropdown (based on your registered location)</li>
                    <li>Provide clear title and detailed description</li>
                    <li>Submit for Elder constitutional review</li>
                </ol>
                <p><strong>Jurisdiction Rules:</strong> You can only create topics for locations where you actually live</p>
            </div>
            
            <h3 style="color: #007bff;">💬 Participating in Debates</h3>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Who Can Participate:</strong> All Contract Citizens and above</p>
                <p><strong>How to Engage:</strong></p>
                <ul>
                    <li><strong>Browse Topics:</strong> View active debates in your jurisdiction</li>
                    <li><strong>Read Arguments:</strong> Review existing FOR, AGAINST, and NEUTRAL positions</li>
                    <li><strong>Add Arguments:</strong> Submit your own position with supporting evidence</li>
                    <li><strong>Vote:</strong> Cast your vote on the topic after reviewing arguments</li>
                    <li><strong>Follow Updates:</strong> Track debate progress and vote tallies</li>
                </ul>
                <p><strong>Debate Rules:</strong> All content subject to constitutional review and community moderation</p>
            </div>
            
            <h3 style="color: #6f42c1;">🗳️ Elections and Voting</h3>
            <div style="background: #f4f1fb; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Types of Elections:</strong></p>
                <ul>
                    <li><strong>Representative Elections:</strong> Every 2 years for local representatives</li>
                    <li><strong>Senator Elections:</strong> Every 6 years with mixed selection process</li>
                    <li><strong>Elder Elections:</strong> Every 4 years by combined legislative vote</li>
                    <li><strong>Special Elections:</strong> Recall votes and emergency appointments</li>
                    <li><strong>Referendums:</strong> Direct citizen votes on constitutional amendments</li>
                </ul>
                <p><strong>Voting Process:</strong></p>
                <ol>
                    <li>Check "Users" tab during election periods</li>
                    <li>Review candidate platforms and qualifications</li>
                    <li>Cast secure, blockchain-recorded vote</li>
                    <li>Monitor real-time results and turnout</li>
                </ol>
            </div>
            
            <h3 style="color: #dc3545;">🛡️ Content Moderation</h3>
            <div style="background: #fdf2f2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Reporting Content:</strong></p>
                <ul>
                    <li><strong>Who Can Report:</strong> Any Contract Citizen</li>
                    <li><strong>What to Report:</strong> Constitutional violations, harassment, spam, misinformation</li>
                    <li><strong>How to Report:</strong> Use "Moderation" tab to flag content with detailed reasoning</li>
                </ul>
                <p><strong>Moderation Process:</strong></p>
                <ol>
                    <li><strong>Flag Submission:</strong> Citizen reports problematic content</li>
                    <li><strong>Jurisdictional Review:</strong> Assigned to appropriate moderators</li>
                    <li><strong>Investigation:</strong> Multi-branch review of content and context</li>
                    <li><strong>Elder Review:</strong> Constitutional compliance check</li>
                    <li><strong>Action/Resolution:</strong> Warning, removal, or dismissal with explanation</li>
                    <li><strong>Appeal Process:</strong> Due process rights with constitutional review</li>
                </ol>
            </div>
            
            <h3 style="color: #f39c12;">📊 Running for Office</h3>
            <div style="background: #fef9e7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Eligibility Requirements:</strong></p>
                <ul>
                    <li>Active Contract Citizen status</li>
                    <li>Meet age and residency requirements for position</li>
                    <li>No recent constitutional violations</li>
                    <li>Complete required training modules</li>
                </ul>
                <p><strong>Campaign Process:</strong></p>
                <ol>
                    <li><strong>Declaration:</strong> Announce candidacy during filing period</li>
                    <li><strong>Platform Development:</strong> Create policy positions and goals</li>
                    <li><strong>Debate Participation:</strong> Engage in public candidate debates</li>
                    <li><strong>Voter Outreach:</strong> Campaign within constitutional guidelines</li>
                    <li><strong>Election Day:</strong> Final vote tallying and results</li>
                </ol>
            </div>
            
            <h3 style="color: #17a2b8;">📋 Citizen Initiatives</h3>
            <div style="background: #e0f7fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Constitutional Amendments:</strong></p>
                <ul>
                    <li><strong>Petition Phase:</strong> Gather 40% of citizen signatures</li>
                    <li><strong>Review Phase:</strong> Elder constitutional compatibility review</li>
                    <li><strong>Debate Phase:</strong> 30-day public discussion period</li>
                    <li><strong>Vote Phase:</strong> Citizen referendum with 55% turnout requirement</li>
                    <li><strong>Implementation:</strong> 6-month rollout with oversight</li>
                </ul>
                <p><strong>Recall Elections:</strong></p>
                <ul>
                    <li><strong>Any Citizen Can Initiate:</strong> Start recall petition for any elected official</li>
                    <li><strong>Signature Requirements:</strong> Collect required percentage based on position</li>
                    <li><strong>Special Election:</strong> If threshold met, special recall vote held</li>
                    <li><strong>Due Process:</strong> Official has right to respond and defend</li>
                </ul>
            </div>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        return widget
    
    def blockchain_section(self) -> QWidget:
        """Blockchain technology and transparency explanation"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">⛓️ Blockchain Technology & Transparency</h2>
            
            <h3 style="color: #27ae60;">🔗 Why Blockchain for Governance?</h3>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p>Blockchain technology provides the foundation for trustworthy democratic governance:</p>
                <ul>
                    <li><strong>Immutability:</strong> Once recorded, governance actions cannot be altered or deleted</li>
                    <li><strong>Transparency:</strong> All citizens can verify every vote, decision, and action</li>
                    <li><strong>Decentralization:</strong> No single point of control or failure</li>
                    <li><strong>Cryptographic Security:</strong> Mathematical proof of authenticity</li>
                    <li><strong>Audit Trail:</strong> Complete historical record of all platform activity</li>
                </ul>
            </div>
            
            <h3 style="color: #007bff;">🏗️ Hierarchical Blockchain Structure</h3>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p>Our blockchain uses a unique hierarchical structure designed for government-scale operations:</p>
                
                <h4>📄 Pages (Immediate Actions)</h4>
                <ul>
                    <li><strong>Purpose:</strong> Record individual actions as they happen</li>
                    <li><strong>Content:</strong> User registrations, votes, debate posts, moderation actions</li>
                    <li><strong>Timeline:</strong> Created instantly for each action</li>
                    <li><strong>Validation:</strong> Cryptographically signed by user and validators</li>
                </ul>
                
                <h4>📚 Chapters (Daily Summaries)</h4>
                <ul>
                    <li><strong>Purpose:</strong> Consolidate 24 hours of pages into organized chapters</li>
                    <li><strong>Content:</strong> Daily activity summaries, vote tallies, decision outcomes</li>
                    <li><strong>Timeline:</strong> Created automatically every 24 hours</li>
                    <li><strong>Validation:</strong> Validated by elected representatives serving as blockchain validators</li>
                </ul>
                
                <h4>📖 Books (Monthly Compilations)</h4>
                <ul>
                    <li><strong>Purpose:</strong> Monthly governance records and policy outcomes</li>
                    <li><strong>Content:</strong> Election results, major decisions, constitutional changes</li>
                    <li><strong>Timeline:</strong> Created monthly with comprehensive summaries</li>
                    <li><strong>Validation:</strong> Multi-signature validation by senior elected officials</li>
                </ul>
                
                <h4>📚 Parts (Yearly Archives)</h4>
                <ul>
                    <li><strong>Purpose:</strong> Annual governance archives and historical records</li>
                    <li><strong>Content:</strong> Year-end summaries, long-term trend analysis</li>
                    <li><strong>Timeline:</strong> Created annually</li>
                    <li><strong>Validation:</strong> Full consensus validation by all branches of government</li>
                </ul>
                
                <h4>📚 Series (Decade Collections)</h4>
                <ul>
                    <li><strong>Purpose:</strong> Historical archives for long-term preservation</li>
                    <li><strong>Content:</strong> Constitutional evolution, major governance milestones</li>
                    <li><strong>Timeline:</strong> Created every 10 years</li>
                    <li><strong>Validation:</strong> Constitutional validation by Contract Founders and Elders</li>
                </ul>
            </div>
            
            <h3 style="color: #6f42c1;">🔐 Proof of Authority (PoA) Consensus</h3>
            <div style="background: #f4f1fb; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Democratic Validator Selection:</strong></p>
                <ul>
                    <li><strong>Validators:</strong> Elected Contract Representatives automatically become blockchain validators</li>
                    <li><strong>Authority:</strong> Validators earn their position through democratic election, not computational power</li>
                    <li><strong>Responsibility:</strong> Must validate blocks honestly or face democratic accountability</li>
                    <li><strong>Term Limits:</strong> Validator status tied to elected position term limits</li>
                </ul>
                
                <p><strong>Validation Process:</strong></p>
                <ol>
                    <li><strong>Block Creation:</strong> New governance actions grouped into blocks</li>
                    <li><strong>Validator Signatures:</strong> Multiple elected validators must sign each block</li>
                    <li><strong>Network Distribution:</strong> Validated blocks distributed to all nodes</li>
                    <li><strong>Consensus Check:</strong> Network verifies validator signatures and block integrity</li>
                    <li><strong>Chain Integration:</strong> Valid blocks permanently added to blockchain</li>
                </ol>
            </div>
            
            <h3 style="color: #dc3545;">🔍 Transparency Features</h3>
            <div style="background: #fdf2f2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>What Citizens Can Verify:</strong></p>
                <ul>
                    <li><strong>Every Vote:</strong> Individual votes in elections and referendums</li>
                    <li><strong>All Decisions:</strong> Representative votes on legislation and policy</li>
                    <li><strong>Moderation Actions:</strong> Content flags, reviews, and resolutions</li>
                    <li><strong>Election Results:</strong> Real-time vote counting with cryptographic proof</li>
                    <li><strong>Government Spending:</strong> Budget allocations and expenditures</li>
                    <li><strong>Constitutional Changes:</strong> All amendments and modifications</li>
                </ul>
                
                <p><strong>Blockchain Explorer:</strong></p>
                <ul>
                    <li>Visit the "Blockchain" tab to explore the complete governance record</li>
                    <li>Search for specific actions, votes, or decisions</li>
                    <li>Verify cryptographic signatures and validation chains</li>
                    <li>Download complete governance data for independent analysis</li>
                </ul>
            </div>
            
            <h3 style="color: #f39c12;">🛡️ Security Features</h3>
            <div style="background: #fef9e7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Cryptographic Protection:</strong></p>
                <ul>
                    <li><strong>RSA-2048 Signatures:</strong> Every user action cryptographically signed</li>
                    <li><strong>Hash Chains:</strong> Blocks linked with cryptographic hashes preventing tampering</li>
                    <li><strong>Multi-Signature Validation:</strong> Multiple validators must agree on each block</li>
                    <li><strong>Private Key Security:</strong> Individual user keys stored locally, never transmitted</li>
                </ul>
                
                <p><strong>Integrity Verification:</strong></p>
                <ul>
                    <li><strong>Automatic Validation:</strong> System continuously verifies blockchain integrity</li>
                    <li><strong>Tamper Detection:</strong> Any unauthorized changes immediately detected</li>
                    <li><strong>Redundancy:</strong> Multiple copies of blockchain maintained across network</li>
                    <li><strong>Recovery Procedures:</strong> Automatic restoration from verified backup chains</li>
                </ul>
            </div>
            
            <h3 style="color: #17a2b8;">📊 Real-Time Monitoring</h3>
            <div style="background: #e0f7fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Live Platform Statistics:</strong></p>
                <ul>
                    <li><strong>Block Creation:</strong> Monitor new blocks being added to the chain</li>
                    <li><strong>Validator Activity:</strong> See which elected officials are actively validating</li>
                    <li><strong>Network Health:</strong> Real-time blockchain integrity status</li>
                    <li><strong>Participation Metrics:</strong> Citizen engagement and voting statistics</li>
                    <li><strong>Governance Activity:</strong> Live feed of democratic actions and decisions</li>
                </ul>
            </div>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        return widget
    
    def getting_started_section(self) -> QWidget:
        """Step-by-step guide for new users"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        content = QTextEdit()
        content.setReadOnly(True)
        content.setHtml("""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db;">🚀 Getting Started Guide</h2>
            
            <h3 style="color: #27ae60;">📝 Step 1: Account Registration</h3>
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Go to the "Register" tab and provide:</strong></p>
                <ul>
                    <li><strong>Identity Information:</strong> Real first and last name</li>
                    <li><strong>Location Details:</strong> City, State/Province, Country (determines voting jurisdiction)</li>
                    <li><strong>Contact Information:</strong> Valid email address (becomes your unique identifier)</li>
                    <li><strong>Security Credentials:</strong> Strong password (automatically hashed with bcrypt)</li>
                    <li><strong>Terms Agreement:</strong> Accept platform governance contracts</li>
                </ul>
                <p><strong>What Happens Next:</strong></p>
                <ul>
                    <li>RSA cryptographic key pair automatically generated for blockchain participation</li>
                    <li>Account registered on blockchain for transparency</li>
                    <li>Contract Citizen status automatically granted</li>
                    <li>You're now eligible to participate in all democratic activities</li>
                </ul>
            </div>
            
            <h3 style="color: #007bff;">🔑 Step 2: First Login</h3>
            <div style="background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Login Process:</strong></p>
                <ol>
                    <li>Go to the "Log In" tab</li>
                    <li>Enter your email and password</li>
                    <li>System verifies your cryptographic keys</li>
                    <li>Session begins with 30-minute timeout for security</li>
                </ol>
                <p><strong>Dashboard Overview:</strong></p>
                <ul>
                    <li>View your current role and titles</li>
                    <li>Check upcoming elections and voting opportunities</li>
                    <li>See recent platform activity and notifications</li>
                    <li>Access your participation history and statistics</li>
                </ul>
            </div>
            
            <h3 style="color: #6f42c1;">🗳️ Step 3: First Vote</h3>
            <div style="background: #f4f1fb; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Participating in Elections:</strong></p>
                <ol>
                    <li>Check "Users" tab during election periods</li>
                    <li>Review candidate information and platforms</li>
                    <li>Cast your vote using the secure voting system</li>
                    <li>Receive confirmation that your vote was recorded on blockchain</li>
                </ol>
                <p><strong>Your vote is:</strong></p>
                <ul>
                    <li><strong>Secret:</strong> Your identity is not linked to your vote choice</li>
                    <li><strong>Verifiable:</strong> You can confirm your vote was counted correctly</li>
                    <li><strong>Permanent:</strong> Recorded on blockchain for historical verification</li>
                </ul>
            </div>
            
            <h3 style="color: #dc3545;">💬 Step 4: Join a Debate</h3>
            <div style="background: #fdf2f2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Engaging in Policy Discussions:</strong></p>
                <ol>
                    <li>Go to "Debates" tab and browse active topics</li>
                    <li>Read existing arguments and positions</li>
                    <li>Click "Add Argument" to contribute your perspective</li>
                    <li>Choose FOR, AGAINST, or NEUTRAL position</li>
                    <li>Write thoughtful argument with supporting evidence</li>
                    <li>Submit for community discussion</li>
                </ol>
                <p><strong>Debate Guidelines:</strong></p>
                <ul>
                    <li>Focus on issues, not personal attacks</li>
                    <li>Provide evidence and reasoning for your positions</li>
                    <li>Respect constitutional rights and democratic principles</li>
                    <li>Report any content that violates community standards</li>
                </ul>
            </div>
            
            <h3 style="color: #f39c12;">📈 Step 5: Advance Your Role</h3>
            <div style="background: #fef9e7; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Pathways to Greater Civic Engagement:</strong></p>
                
                <h4>🗳️ Run for Representative (2-year terms)</h4>
                <ul>
                    <li>Build reputation through quality debate participation</li>
                    <li>Develop policy platform and campaign materials</li>
                    <li>File candidacy during election periods</li>
                    <li>Campaign within your geographic jurisdiction</li>
                </ul>
                
                <h4>🏛️ Advance to Senator (6-year terms)</h4>
                <ul>
                    <li>Serve successfully as Representative</li>
                    <li>Demonstrate legislative experience and judgment</li>
                    <li>Gain support from Representatives, Citizens, and Elders</li>
                    <li>Win mixed-selection process election</li>
                </ul>
                
                <h4>👴 Become an Elder (4-year terms)</h4>
                <ul>
                    <li>Extensive experience in Representative or Senator roles</li>
                    <li>Deep understanding of constitutional principles</li>
                    <li>Reputation for wisdom and fair judgment</li>
                    <li>Election by combined legislative vote</li>
                </ul>
            </div>
            
            <h3 style="color: #17a2b8;">🛠️ Step 6: Explore Advanced Features</h3>
            <div style="background: #e0f7fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Platform Deep Dive:</strong></p>
                
                <h4>⛓️ Blockchain Explorer</h4>
                <ul>
                    <li>Visit "Blockchain" tab to explore governance records</li>
                    <li>Verify your own actions and votes</li>
                    <li>Research historical decisions and their outcomes</li>
                    <li>Download data for independent analysis</li>
                </ul>
                
                <h4>🛡️ Moderation System</h4>
                <ul>
                    <li>Learn to identify and report constitutional violations</li>
                    <li>Understand the multi-branch review process</li>
                    <li>Exercise your appeal rights if needed</li>
                    <li>Contribute to maintaining platform integrity</li>
                </ul>
                
                <h4>📋 Contract System</h4>
                <ul>
                    <li>Explore governance contracts and their terms</li>
                    <li>Understand how rules are enforced technologically</li>
                    <li>Participate in contract amendment processes</li>
                    <li>Propose improvements to governance structure</li>
                </ul>
            </div>
            
            <h3 style="color: #e74c3c;">❓ Getting Help</h3>
            <div style="background: #fdf2f2; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <p><strong>Support Resources:</strong></p>
                <ul>
                    <li><strong>System Guide:</strong> This comprehensive guide (bookmark it!)</li>
                    <li><strong>Platform Documentation:</strong> Technical details and specifications</li>
                    <li><strong>Community Forums:</strong> Ask questions and get help from experienced users</li>
                    <li><strong>Constitutional Questions:</strong> Contact Contract Elders for constitutional interpretation</li>
                    <li><strong>Technical Support:</strong> Report bugs or technical issues to platform administrators</li>
                </ul>
                
                <p><strong>Remember:</strong> This platform is designed to be user-friendly, but democratic governance is complex. Take time to understand the system, and don't hesitate to ask questions. Your informed participation strengthens democracy for everyone.</p>
            </div>
        </div>
        """)
        
        layout.addWidget(content)
        widget.setLayout(layout)
        return widget