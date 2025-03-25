from tkinter import filedialog
from tkinter import messagebox as msg  # Temporary fallback
import customtkinter as ctk
from customtkinter import CTk, CTkTabview, CTkEntry, CTkButton, CTkLabel, CTkFrame, CTkTextbox
from CTkMessagebox import CTkMessagebox
from PIL import Image, ImageTk
import os
import pandas as pd
from GlucoScholar import randomForest, ImageProcessor, InformationFetcher
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import time
from tkinter import scrolledtext
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import sqlite3
from datetime import datetime
from tkcalendar import DateEntry 
import csv

class DiabetesPredictorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GlucoScholar Diabetes Predictor")
        self.root.geometry("800x600")
        
        ctk.set_appearance_mode("Light")  # "Light" or "Dark"
        ctk.set_default_color_theme("dark-blue")  # Other options: green, dark-blue
        
        # Initialize components
        self.radFor = randomForest()
        self.image_processor = ImageProcessor()
        self.info_fetcher = InformationFetcher()
        
        # Create notebook for tabs
        self.notebook = ctk.CTkTabview(self.root)
        self.notebook.pack(fill='both', expand=True)
        
        # Create frames with consistent styling
        self._create_frames()
        
        # Initialize components for each tab
        self.create_dataset_tab()
        self.create_image_tab()
        self.create_predict_tab()
        self.create_medical_tab()
        self.create_report_tab() 
        
        # Database initialization
        self.conn = sqlite3.connect('diabetes_predictions.db')
        self.create_prediction_table()
        
        # Add this to handle database closure on exit
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_prediction_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS predictions
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        gender TEXT,
                        age REAL,
                        hypertension INTEGER,
                        heart_disease INTEGER,
                        smoking_history TEXT,
                        bmi REAL,
                        HbA1c_level REAL,
                        blood_glucose_level REAL,
                        prediction_result TEXT,
                        timestamp DATETIME)''')
        self.conn.commit()

    def on_closing(self):
        """Handle database connection closure when app exits"""
        # self.conn.close()
        # self.root.destroy()
        try:
            # Close database connection
            if hasattr(self, 'conn'):
                self.conn.close()
            
            # Clear any pending tasks
            self.root.after_cancel("all")
            
            # Destroy the main window
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            self.root.destroy()
        
    def save_prediction(self, input_data, prediction_result):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO predictions 
                            (gender, age, hypertension, heart_disease, smoking_history,
                            bmi, HbA1c_level, blood_glucose_level, prediction_result, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (input_data['gender'],
                            input_data['age'],
                            input_data['hypertension'],
                            input_data['heart_disease'],
                            input_data['smoking_history'],
                            input_data['bmi'],
                            input_data['HbA1c_level'],
                            input_data['blood_glucose_level'],
                            prediction_result,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            self.conn.commit()
        except sqlite3.Error as e:
            CTkMessagebox(
                title="Database Error",
                message=f"Failed to save prediction: {str(e)}",
                icon="cancel",
                parent=self.root  # Ensure parent is set to CTk window
            )
     
    def _create_frames(self):
        # Create notebook tabs using CTkTabview
        self.notebook.add("Dataset Analysis")
        self.notebook.add("Image Analysis")
        self.notebook.add("Diabetes Prediction")
        self.notebook.add("Medical Support")
        self.notebook.add("Generate Reports")
        
        # Configure the segmented button font after creation
        self.notebook._segmented_button.configure(font=("Arial", 18, "bold"))
        
        # Get the frames from the tabs
        self.dataset_frame = self.notebook.tab("Dataset Analysis")
        self.image_frame = self.notebook.tab("Image Analysis")
        self.predict_frame = self.notebook.tab("Diabetes Prediction")
        self.medical_frame = self.notebook.tab("Medical Support")
        self.report_frame = self.notebook.tab("Generate Reports")

        # Configure frames appearance (CustomTkinter doesn't use ttk styles)
        for frame in [self.dataset_frame, self.image_frame, self.predict_frame, 
                    self.medical_frame, self.report_frame]:
            frame.configure(
                fg_color="#7fbbe3",  # Background color
                corner_radius=6    # Rounded corners
            )
    
    def create_dataset_tab(self):
        # Dataset upload section
        ctk.CTkLabel(self.dataset_frame, text="Upload Dataset:", text_color="white", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.dataset_path = ctk.StringVar()
        entry = ctk.CTkEntry(self.dataset_frame, textvariable=self.dataset_path, width=400, height=32, font=("Arial", 14), placeholder_text="Select dataset file...")
        entry.grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.dataset_frame, text="Upload", command=self.load_dataset, width = 150, height = 32, font=("Arial", 16, "bold"), fg_color="#005f87", hover_color="#2980b9").grid(row=0, column=2, padx=10)
        
        # Style for text widget
        self.results_text = ctk.CTkTextbox(self.dataset_frame, height=200, width=600, 
                                  font=('Arial', 18),
                                  fg_color="white",
                                    text_color="black",
                                    border_width=1,
                                    border_color="#E0E0E0",
                                    corner_radius=6)
        self.results_text.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="nsew")
    
        # Configure grid weights for better resizing
        self.dataset_frame.grid_columnconfigure(1, weight=1)
        self.dataset_frame.grid_rowconfigure(1, weight=1)
    
    def create_report_tab(self):
        self.report_frame = self.notebook.tab("Generate Reports")
        
        # Date selection
        ctk.CTkLabel(self.report_frame, text="Start Date:", text_color="white",font=("Arial", 20, "bold")).grid(row=0, column=0, padx=(100,50), pady=10)
        self.start_date = DateEntry(self.report_frame, width=12, height=10,
                                    background='#3498db',
                                    foreground='white',
                                    font=("Arial", 16),
                                    selectbackground='#2980b9',
                                    selectforeground='white',
                                    justify='center',
                                    relief="solid",
                                    borderwidth=5)
        self.start_date.grid(row=0, column=1, padx=(100,450), pady=30, ipadx=10, ipady=10)
        
        ctk.CTkLabel(self.report_frame, text="End Date:", text_color="white", font=("Arial", 20, "bold")).grid(row=1, column=0, padx=(100,50), pady=10)
        self.end_date = DateEntry(self.report_frame,
                                  width=12,
                                  height=10,
                                  font=("Arial", 16),
                                  background='#3498db',
                                  foreground='white',
                                  selectbackground='#2980b9',
                                  selectforeground='white',
                                  justify='center',
                                  relief="solid",
                                  borderwidth=5)
        self.end_date.grid(row=1, column=1, padx=(100, 450), ipadx=10, pady=30, ipady=10)
        
        # Generate report button
        ctk.CTkButton(self.report_frame, 
                text="Generate CSV Report", 
                command=self.generate_csv_report,
                width=300,
                height=50,
                fg_color="#005f87",
                hover_color="#3498db",
                font=("Arial", 16, "bold")).grid(row=2, column=0, columnspan=2, pady=20)
        
        # Status label
        self.report_status = ctk.CTkLabel(self.report_frame, text="", text_color='#120f40', font=("Arial", 16, "bold"))
        self.report_status.grid(row=3, column=0, columnspan=2, pady=10)

        # Configure grid weights for better layout
        self.report_frame.grid_columnconfigure(1, weight=1)
        for i in range(4):
            self.report_frame.grid_rowconfigure(i, weight=1)
            
            
    def create_image_tab(self):
        # Image upload section
        ctk.CTkLabel(self.image_frame, text="Upload Image:", text_color="white", font=("Arial", 16, "bold")).grid(row=0, column=0, padx=10, pady=10)
        self.image_path = ctk.StringVar()
        ctk.CTkEntry(self.image_frame, textvariable=self.image_path, width=600, font=("Arial", 14), height = 32, placeholder_text="Select image file...").grid(row=0, column=1, padx=10)
        ctk.CTkButton(self.image_frame, text="Upload", command=self.load_image, width=150,
                                    height=32,
                                    font=("Arial", 16, "bold"),
                                    fg_color="#005f87",
                                    hover_color="#2980b9").grid(row=0, column=2)
        
        # Style buttons
        # self.style.configure('TButton', padding=6, relief='flat', background='#3498db', foreground='white')
        ctk.CTkButton(self.image_frame, text="Extract Text", command=self.process_image, 
                        width=150,
                        height=32,
                        font=("Arial", 14, "bold"),
                        fg_color="#005f87",
                        hover_color="#2980b9").grid(row=1, column=0, pady=10, padx=10)
        ctk.CTkButton(self.image_frame, text="Search Online", command=self.search_online,
                        width=150,
                        height=32,
                        font=("Arial", 14, "bold"),
                        fg_color="#005f87",
                        hover_color="#2980b9").grid(row=1, column=1, pady=10, padx=5)
        
        # Configure scrolled text
        self.image_text = ctk.CTkTextbox(
                self.image_frame,
                height=400,
                width=700,
                font=("Arial", 14),
                text_color="#0a2138",
                fg_color="white",
                border_width=1,
                border_color="#E0E0E0",
                corner_radius=6
            )
        self.image_text.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights for better resizing
        self.image_frame.grid_columnconfigure(1, weight=1)
        self.image_frame.grid_rowconfigure(2, weight=1)
        
        # Create a separate frame for links
        self.links_frame = ctk.CTkFrame(self.image_frame, fg_color="transparent")
        self.links_frame.grid(row=3, column=0, columnspan=3, sticky="nsew", padx=10, pady=5)
    
    def _open_url(self, event):
        """Handle URL clicks in CTkTextbox"""
        try:
            # Get the index of the mouse click
            index = self.image_text.index(f"@{event.x},{event.y}")
            
            # Get the tags at this index
            tags = self.image_text.tag_names(index)
            
            # Find and open URL
            for tag in tags:
                if tag.startswith("url-"):
                    url = tag[4:]  # Remove 'url-' prefix
                    
                    # Ensure URL is properly formatted
                    if not url.startswith(('http://', 'https://')):
                        url = f"https://{url}"
                        
                    # Open URL in default browser
                    webbrowser.open_new_tab(url)
                    break
        except Exception as e:
            print(f"Error opening URL: {str(e)}")
                
    def create_predict_tab(self):
        fields = [
            ('gender', 'Gender (Male/Female)'),
            ('age', 'Age'),
            ('hypertension', 'Hypertension (No: 0/Yes: 1)'),
            ('heart_disease', 'Heart Disease (No: 0/Yes: 1)'),
            ('smoking_history', 'Smoking History (Never/Current/Former/No Info/Ever/Not Current)'),
            ('bmi', 'BMI'),
            ('HbA1c_level', 'HbA1c Level'),
            ('blood_glucose_level', 'Blood Glucose Level')
        ]
        
        self.entries = {}
        self.error_labels = {}

        # Configure grid layout
        self.predict_frame.grid_columnconfigure(1, weight=1)
        
        for i, (field, label) in enumerate(fields):
            # Label
            ctk.CTkLabel(self.predict_frame, 
                        text=label,
                        font=("Arial", 14, "bold"),
                        text_color="black",
                        anchor="w").grid(row=i, column=0, padx=(10,5), pady=2, sticky="w")
            
            # Entry frame with error label
            entry_frame = ctk.CTkFrame(self.predict_frame, fg_color="transparent")
            entry_frame.grid(row=i, column=1, padx=(5,10), pady=2, sticky="ew")
            
            # Entry widget
            self.entries[field] = ctk.CTkEntry(
                entry_frame,
                width=150,
                font=("Arial", 12, "bold"),
                placeholder_text=f"Enter {label.split(':')[0]}"
            )
            # self.entries[field].pack(side="left", fill="x", expand=True)
            self.entries[field].pack(side="left", padx=(2,5), pady=2)  # Added padding
        
            # Error label
            self.error_labels[field] = ctk.CTkLabel(
                entry_frame,
                text="",
                text_color="red",
                font=("Arial", 10, "bold"),
                width=250,  # Increased width from 100 to 250
                wraplength=250,  # Added wraplength to enable text wrapping
                justify="left"
            )
            self.error_labels[field].pack(side="left", padx=2)
            
            # Bind validation
            if field in ['age', 'bmi', 'HbA1c_level', 'blood_glucose_level']:
                self.entries[field].bind("<KeyRelease>", 
                    lambda e, f=field: self.validate_numeric_input(f))
            else:
                self.entries[field].bind("<KeyRelease>", 
                    lambda e, f=field: self.validate_categorical_input(f))

        # Prediction button
        predict_btn = ctk.CTkButton(
            self.predict_frame,
            text="PREDICT DIABETES",
            command=self.predict_diabetes,
            font=("Arial", 16, "bold"),
            fg_color="#005f87",
            hover_color="#238194",
            width=400,
            height=50,
            corner_radius=8
        )
        predict_btn.grid(row=len(fields), column=0, columnspan=2, pady=50, padx=5, sticky="ns")
        
        # Result label
        self.result_label = ctk.CTkLabel(
            self.predict_frame,
            text="",
            font=("Arial", 18, "bold"),
            text_color=["black", "white"]
        )
        self.result_label.grid(row=len(fields)+1, column=0, columnspan=2, pady=10)

    # Add the validate_categorical_input method to your class
    def validate_categorical_input(self, field):
        """Validate categorical input fields"""
        value = self.entries[field].get().strip()
        self.error_labels[field].configure(text="")  # Changed from config to configure for CTk
        
        if not value:
            return
        
        if field == 'gender':
            valid_values = ['Male', 'Female']
            if value not in valid_values:
                self.error_labels[field].configure(
                    text="Enter: Male/Female",
                    text_color="red"  # CTk specific color setting
                )
        
        elif field == 'hypertension':
            if value not in ['0', '1']:
                self.error_labels[field].configure(
                    text="Enter: 0 or 1",
                    text_color="red"
                )
        
        elif field == 'heart_disease':
            if value not in ['0', '1']:
                self.error_labels[field].configure(
                    text="Enter: 0 or 1",
                    text_color="red"
                )
                
        elif field == 'smoking_history':
            valid_values = self.radFor.smoking_history_encoder.classes_
            input_value = value.strip().title()  # Convert input to title case

            matches = [v for v in valid_values if v.lower() == input_value.lower()]
            # Special handling for "No Info" and case-sensitivity
            if not matches:
                allowed = "/".join(valid_values)
                self.error_labels[field].configure(
                    text=f"Enter: {allowed}",
                    text_color="red"
                )
            else:
                # Convert to correct case if valid
                correct_case = matches[0]
                self.entries[field].delete(0, "end")  # CTk syntax
                self.entries[field].insert(0, correct_case)
                # Clear error message when valid
                self.error_labels[field].configure(
                    text="",
                    text_color="red"
                )
    
    def validate_numeric_input(self, field):
        """Wrapper method to handle validation on key release"""
        self.validate_numeric_field(field)
            
    def validate_numeric_field(self, field):
        value = self.entries[field].get().strip()
        self.error_labels[field].configure(text="", text_color="red")  # Clear previous error
        
        if not value:
            return
        
        try:
            num = float(value)
            
            # Field-specific validation with CustomTkinter styling
            if field == 'age' and not (0 < num <= 120):
                self.error_labels[field].configure(
                    text="Age 0-120",
                    text_color="red"
                )
            elif field == 'bmi' and not (10 <= num <= 50):
                self.error_labels[field].configure(
                    text="BMI 10-50",
                    text_color="red"
                )
            elif field == 'HbA1c_level' and not (3 <= num <= 20):
                self.error_labels[field].configure(
                    text="HbA1c 3-20%",
                    text_color="red"
                )
            elif field == 'blood_glucose_level' and not (70 <= num <= 300):
                self.error_labels[field].configure(
                    text="Glucose 70-300",
                    text_color="red"
                )
                
        except ValueError:
            self.error_labels[field].configure(
                text="Numbers only",
                text_color="red"
            )
    

    def create_medical_tab(self):
        # Medical advice display using CTkTextbox
        self.advice_text = ctk.CTkTextbox(
            self.medical_frame,
            height=200,
            width=300,
            font=("Arial", 18, "bold"),
            text_color="#2c3e50",
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=6,
            wrap="word"
        )
        self.advice_text.pack(padx=10, pady=10, fill="both", expand=True)

        # PDF generation button with CTk styling
        ctk.CTkButton(
            self.medical_frame,  # Changed from predict_frame to medical_frame
            text="Generate PDF Report",
            command=self.generate_pdf_report,
            width=200,
            height=35,
            font=("Arial", 16, "bold"),
            fg_color="#005f87",
            hover_color="#2980b9",
            corner_radius=8
        ).pack(pady=10)  # Changed from grid to pack for consistency
    

    def load_dataset(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if file_path:
            self.dataset_path.set(file_path)
            try:
                # Read the dataset
                df = pd.read_csv(file_path)
                
                # Ensure all required columns are present
                required_columns = [
                    'gender', 'age', 'hypertension', 'heart_disease',
                    'smoking_history', 'bmi', 'HbA1c_level', 'blood_glucose_level'
                ]
                
                # Check if all required columns exist
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
                
                # Handle unknown categories for gender
                known_genders = self.radFor.gender_encoder.classes_
                df['gender'] = df['gender'].apply(
                    lambda x: x if x in known_genders else known_genders[0]
                )
                
                # Handle unknown categories for smoking_history
                known_smoking = self.radFor.smoking_history_encoder.classes_
                df['smoking_history'] = df['smoking_history'].apply(
                    lambda x: x if x in known_smoking else known_smoking[0]
                )
                
                # Encode categorical variables
                df['gender'] = self.radFor.gender_encoder.transform(df['gender'])
                df['smoking_history'] = self.radFor.smoking_history_encoder.transform(df['smoking_history'])
                
                # Reorder columns to match training data order
                df = df[required_columns]
                
                # Make predictions
                predictions = self.radFor.model.predict(df)
                diabetic = sum(predictions)
                non_diabetic = len(predictions) - diabetic
                
                # Display results using CTkTextbox
                self.results_text.delete("0.0", "end")  # CTk syntax
                self.results_text.insert("0.0", f"Dataset: {os.path.basename(file_path)}\n")
                self.results_text.insert("end", f"Total Cases: {len(predictions)}\n")
                self.results_text.insert("end", f"Diabetic Cases: {diabetic}\n")
                self.results_text.insert("end", f"Non-Diabetic Cases: {non_diabetic}\n")
                self.results_text.insert("end", f"Diabetic Percentage: {(diabetic/len(predictions))*100:.2f}%\n\n")
                
                # Create pie chart
                fig, ax = plt.subplots(figsize=(5, 4))
                labels = ['Diabetic', 'Non-Diabetic']
                sizes = [diabetic, non_diabetic]
                colors = ['#ff9999', '#66b3ff']
                
                ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%')  # Removed shadow
                ax.axis('equal')
                plt.title('Diabetes Prediction Distribution', fontsize=14, fontweight='bold')
                
                # Embed the plot
                if hasattr(self, 'canvas'):
                    self.canvas.get_tk_widget().destroy()
                self.canvas = FigureCanvasTkAgg(fig, master=self.dataset_frame)
                self.canvas.draw()
                self.canvas.get_tk_widget().grid(
                    row=2, 
                    column=0, 
                    columnspan=3, 
                    padx=10, 
                    pady=10,
                    sticky="nsew"
                )
                
                # Add warning if unknown categories were found
                if df['gender'].isin([known_genders[0]]).any() or df['smoking_history'].isin([known_smoking[0]]).any():
                    warning_msg = "Note: Some records contained unknown categories and were mapped to default values."
                    self.results_text.insert("end", warning_msg)
                    
            except ValueError as ve:
                CTkMessagebox(
                    title="Error",
                    message=str(ve),
                    icon="cancel"
                )
            except Exception as e:
                CTkMessagebox(
                    title="Error",
                    message=f"Error processing dataset: {str(e)}",
                    icon="cancel"
                )
                
    def load_image(self):
        """Handle image file selection"""
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.image_path.set(file_path)
                
    def process_image(self):
        """Process the selected image and extract text"""
        if self.image_path.get():
            try:
                extracted_text = self.image_processor.extract_text(self.image_path.get())
                
                # CustomTkinter text widget operations
                self.image_text.delete("0.0", "end")  # CTk syntax
                self.image_text.insert("0.0", "Extracted Text:\n" + extracted_text)
                
                # Debug print
                # print("Extracted Text: ", self.image_text.get("0.0", "end-1c"))
                
            except Exception as e:
                CTkMessagebox(
                    title="Error",
                    message=f"Error processing image: {str(e)}",
                    icon="cancel"
                )
    
    def search_online(self):
        """Handle online search with CustomTkinter widgets"""
        query = self.image_text.get("0.0", "end-1c")  # CTk syntax
        # print("🔖 Text for search: ", query)
        
        if query:
            try:
                # Show searching status
                self.image_text.insert("end", "\n\nSearching...\n")
                self.root.update()

                # Add initial delay
                time.sleep(2)

                results = self.info_fetcher.google_search(query)
                
                # Clear searching status using CTk syntax
                self.image_text.delete("end-2c linestart", "end-1c lineend")
                
                 # Clear previous links
                for widget in self.links_frame.winfo_children():
                    widget.destroy()
                
                if results:
                    self.image_text.insert("end", "\nSearch Results:\n")
                    for i, url in enumerate(results[:5], 1):
                        # Enhanced URL validation and completion
                        if not url.startswith(('http://', 'https://')):
                            url = f"https://{url}"
                        if 'google.com' in url:
                            continue
                        
                        # Create clickable link button
                        link_btn = ctk.CTkButton(
                            self.links_frame,
                            text=f"{i}. {url}",
                            command=lambda u=url: webbrowser.open_new_tab(u),
                            fg_color="transparent",
                            text_color="#120f40",
                            hover_color="#E0E0E0",
                            anchor="w",
                            height=25
                        )
                        link_btn.pack(fill="x", pady=2)
                        
                else:
                    self._show_default_resources()

            except Exception as e:
                if "429" in str(e):
                    self._show_default_resources()
                else:
                    CTkMessagebox(
                        title="Error",
                        message=f"Search failed: {str(e)}",
                        icon="cancel"
                    )

    def _show_default_resources(self):
        """Helper method to display default resources"""
        self.image_text.insert("end", "\nUsing alternative medical resources:\n")
        
        # Clear previous links
        for widget in self.links_frame.winfo_children():
            widget.destroy()
        
        default_urls = [
            "https://www.diabetes.org/",
            "https://www.niddk.nih.gov/health-information/diabetes",
            "https://www.who.int/health-topics/diabetes"
        ]
        for i, url in enumerate(default_urls, 1):
            link_btn = ctk.CTkButton(
                self.links_frame,
                text=f"{i}. {url}",
                command=lambda u=url: webbrowser.open_new_tab(u),
                fg_color="transparent",
                text_color="#061421",
                hover_color="#E0E0E0",
                anchor="w",
                height=25
            )
            link_btn.pack(fill="x", pady=2)
                
    def predict_diabetes(self):
        # Clear previous errors
        for field in self.error_labels:
            self.error_labels[field].configure(text="")  # Changed from config to configure

        try:
            input_data = {
                'gender': self.entries['gender'].get().strip(),
                'age': float(self.entries['age'].get().strip()),
                'hypertension': int(self.entries['hypertension'].get().strip()),
                'heart_disease': int(self.entries['heart_disease'].get().strip()),
                'smoking_history': self.entries['smoking_history'].get().strip(),
                'bmi': float(self.entries['bmi'].get().strip()),
                'HbA1c_level': float(self.entries['HbA1c_level'].get().strip()),
                'blood_glucose_level': float(self.entries['blood_glucose_level'].get().strip())
            }
            
            # --- Validation Checks ---
            errors = False 
            
            try:
                age = float(input_data['age'])
                if not (0 < age <= 120):
                    self.error_labels['age'].configure(
                        text="Age must be 0-120 years",
                        text_color="red"
                    )
                    errors = True
            except ValueError:
                self.error_labels['age'].configure(
                    text="Invalid age",
                    text_color="red"
                )
                errors = True
                        
            try:
                bmi = float(input_data['bmi'])
                if not (10 <= bmi <= 50):
                    self.error_labels['bmi'].configure(
                        text="BMI must be 10-50",
                        text_color="red"
                    )
                    errors = True
            except ValueError:
                self.error_labels['bmi'].configure(
                    text="Invalid BMI",
                    text_color="red"
                )
                errors = True
            
            try:
                hba1c = float(input_data['HbA1c_level'])
                if not (3 <= hba1c <= 20):
                    self.error_labels['HbA1c_level'].configure(
                        text="HbA1c must be 3-20%",
                        text_color="red"
                    )
                    errors = True
            except ValueError:
                self.error_labels['HbA1c_level'].configure(
                    text="Numbers only",
                    text_color="red"
                )
                errors = True
            
            try:
                glucose = float(input_data['blood_glucose_level'])
                if not (70 <= glucose <= 300):
                    self.error_labels['blood_glucose_level'].configure(
                        text="Glucose must be 70-300 mg/dL",
                        text_color="red"
                    )
                    errors = True
            except ValueError:
                self.error_labels['blood_glucose_level'].configure(
                    text="Numbers only",
                    text_color="red"
                )
                errors = True
                
            if errors:
                return

            # Handle unknown categories with CTkMessagebox
            if input_data['gender'] not in self.radFor.gender_encoder.classes_:
                input_data['gender'] = self.radFor.gender_encoder.classes_[0]
                CTkMessagebox(
                    title="Warning",
                    message=f"Unknown gender category. Using default: {input_data['gender']}",
                    icon="warning"
                )
                
            if input_data['smoking_history'] not in self.radFor.smoking_history_encoder.classes_:
                input_data['smoking_history'] = self.radFor.smoking_history_encoder.classes_[0]
                CTkMessagebox(
                    title="Warning",
                    message=f"Unknown smoking history category. Using default: {input_data['smoking_history']}",
                    icon="warning"
                )
            
            # Convert to DataFrame for prediction
            df = pd.DataFrame([input_data])
            
            # Encode categorical variables
            df['gender'] = self.radFor.gender_encoder.transform(df['gender'])
            df['smoking_history'] = self.radFor.smoking_history_encoder.transform(df['smoking_history'])
            
            # Make prediction
            prediction = self.radFor.model.predict(df)
            result = "Diabetic" if prediction[0] == 1 else "Not Diabetic"
            
            # Update result label with CTk styling
            self.result_label.configure(
                text=f"Prediction Result: {result}",
                text_color="red" if prediction[0] else "green"
            )
            
            # Save to database
            self.save_prediction(input_data, result)
            
            # Update medical recommendations
            self.advice_text.delete("0.0", "end")  # CTk syntax
            
            recommendations = self.get_medical_recommendations(prediction[0], input_data)
            self.advice_text.insert("0.0", "\n\nPersonalized Recommendations:\n\n")
            for rec in recommendations:
                self.advice_text.insert("end", f"• {rec}\n")
                
            # # Add tag configuration for the title
            # self.advice_text.tag_add("title", "0.0", "1.0")
            # self.advice_text.tag_configure("title", font=("Arial", 20, "bold"))  # Even larger font for the title
      
        except ValueError as ve:
            CTkMessagebox(
                title="Invalid Input",
                message=str(ve),
                icon="cancel"
            )
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Invalid input: {str(e)}",
                icon="cancel"
            )
            
    def create_medical_tab(self):
        # Medical advice display using CTkTextbox
        self.advice_text = ctk.CTkTextbox(
            self.medical_frame,
            height=250,
            width=400,
            font=("Arial", 16, "bold"),
            text_color="#2c3e50",
            fg_color="white",
            border_width=1,
            border_color="#E0E0E0",
            corner_radius=6,
            wrap="word"
        )
        self.advice_text.pack(padx=10, pady=10, fill="both", expand=True)

        # PDF generation button with CTk styling
        ctk.CTkButton(
            self.medical_frame,  # Changed from predict_frame to medical_frame
            text="Generate PDF Report",
            command=self.generate_pdf_report,
            width=200,
            height=35,
            font=("Arial", 16, "bold"),
            fg_color="#005f87",
            hover_color="#2980b9",
            corner_radius=8
        ).pack(pady=10)  # Changed from grid to pack for consistency
        
    def get_medical_recommendations(self, prediction, inputs):
        """Generate personalized medical recommendations based on prediction and inputs"""
        recommendations = []
        
        # General recommendations
        if prediction == 1:
            recommendations.extend([
                "🟥 Medical Alert: Predictive results indicate diabetes risk. Please consult a healthcare professional immediately.",
                "🔔 Recommendation: Schedule fasting blood glucose and HbA1c tests with your doctor."
            ])
        else:
            recommendations.append("🟩 Predictive results show no diabetes risk. Maintain regular checkups.")
        
        # BMI-based recommendations
        try:
            bmi = float(inputs.get('bmi', 0))
            if bmi >= 25:
                recommendations.extend([
                    "⚖️ Weight Management: Aim for 5-10% weight loss through diet and exercise",
                    "🏃 Exercise: 150 mins/week moderate activity (brisk walking, cycling)"
                ])
            elif bmi < 18.5:
                recommendations.append("⚖️ Nutrition: Consult dietitian for healthy weight gain strategies")
        except ValueError:
            print("Invalid BMI value")
        
        # Blood glucose specific
        try:
            glucose = float(inputs.get('blood_glucose_level', 0))
            if glucose > 140:
                recommendations.append("🍬 Blood Sugar Management: Monitor fasting and post-meal glucose levels regularly")
        except ValueError:
            print("Invalid glucose value")
        
        # Smoking recommendations
        smoking = str(inputs.get('smoking_history', '')).lower()
        if smoking in ['current', 'former']:
            recommendations.append("🚭 Smoking Cessation: Consider nicotine replacement therapy or counseling")
        
        # Hypertension management
        try:
            if int(inputs.get('hypertension', 0)) == 1:
                recommendations.append("❤️Blood Pressure: Maintain sodium intake <2g/day and monitor BP weekly")
        except ValueError:
            print("Invalid hypertension value")
        
        return recommendations
            
    def generate_pdf_report(self):
        try:
            # Collect patient data
            patient_data = {field: self.entries[field].get() for field in self.entries}
            result_text = self.result_label.cget("text")
            prediction = result_text.split(": ")[-1]
            
            # Get medical recommendations
            recommendations = self.get_medical_recommendations(
                prediction, 
                {k: float(v) if v.replace('.','',1).isdigit() else v 
                for k,v in patient_data.items()}
            )
            
            # Generate automatic filename with timestamp
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"Diabetes_Report_{timestamp}.pdf"
            desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', filename)
            
            # Create PDF
            doc = SimpleDocTemplate(desktop_path, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'Title',
                parent=styles['Heading1'],
                alignment=1,
                spaceAfter=14
            )
            elements.append(Paragraph("Diabetes Risk Assessment Report", title_style))
            
            # Patient Information Table
            patient_table = [
                ["Patient Information", "Value"],
                ["Age", patient_data['age']],
                ["Gender", patient_data['gender']],
                ["BMI", patient_data['bmi']],
                ["HbA1c Level", patient_data['HbA1c_level']],
                ["Blood Glucose", patient_data['blood_glucose_level']],
                ["Prediction Result", prediction]
            ]
            
            table = Table(patient_table)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 12),
                ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                ('GRID', (0,0), (-1,-1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Medical Recommendations
            elements.append(Paragraph("Medical Recommendations:", styles['Heading2']))
            for rec in recommendations:
                elements.append(Paragraph(f"• {rec}", styles['BodyText']))
                elements.append(Spacer(1, 0.1*inch))
            
            # Disclaimer
            disclaimer = """<font color=red><i>Note: This automated report is not a substitute for professional medical advice. 
                        Always consult a qualified healthcare provider for diagnosis and treatment.</i></font>"""
            elements.append(Paragraph(disclaimer, styles['Italic']))
            
            doc.build(elements)
            
            # Open PDF in default browser
            webbrowser.open_new_tab(f"file://{desktop_path}")
            
            # Show success message with CTkMessagebox
            CTkMessagebox(
                title="Success",
                message=f"PDF report saved and opened:\n{desktop_path}",
                icon="info"
            )
                
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Failed to generate PDF: {str(e)}",
                icon="cancel"
            )
            
    def generate_csv_report(self):
        try:
            # Get selected dates
            start = self.start_date.get_date()
            end = self.end_date.get_date()
            
            if start > end:
                self.report_status.configure(
                    text="Error: Start date cannot be after End date",
                    text_color="red"
                )
                return
            else:
                self.report_status.configure(text="")

            # Convert to SQLite compatible format
            start_str = start.strftime('%Y-%m-%d')
            end_str = end.strftime('%Y-%m-%d')
            
            # Query database
            cursor = self.conn.cursor()
            cursor.execute('''SELECT 
                        id, gender, age, hypertension, heart_disease, smoking_history,
                        bmi, HbA1c_level, blood_glucose_level, prediction_result
                        FROM predictions 
                        WHERE date(timestamp) BETWEEN ? AND ?''', 
                        (start_str, end_str))
            data = cursor.fetchall()
            
            if not data:
                self.report_status.configure(
                    text="No records found in selected period",
                    text_color="red"
                )
                return
                
            # CSV headers
            columns = ['ID', 'Gender', 'Age', 'Hypertension', 'Heart Disease',
                    'Smoking History', 'BMI', 'HbA1c Level', 'Blood Glucose Level',
                    'Prediction Result']
            
            # Generate filename with dates
            filename = f"diabetes_report_{start_str}_to_{end_str}.csv"
            file_path = os.path.join(os.path.expanduser('~'), 'Desktop', filename)
            
            # Write to CSV
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(data)
            
            # Show success messages
            self.report_status.configure(
                text=f"Report saved to: {file_path}",
                text_color="#120f40"
            )
            webbrowser.open(file_path)
            
            CTkMessagebox(
                title="Success",
                message=f"CSV report generated successfully:\n{file_path}",
                icon="info"
            )
            
        except Exception as e:
            CTkMessagebox(
                title="Error",
                message=f"Failed to generate report: {str(e)}",
                icon="cancel"
            )

if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        root = ctk.CTk()
        app = DiabetesPredictorApp(root)
        root.mainloop()
    except Exception as e:
        print(f"Application error: {str(e)}")
