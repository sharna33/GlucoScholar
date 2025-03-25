## **GlucoScholar: Diabetes Risk Prediction Tool 🩺**

GlucoScholar is a comprehensive AI-powered application designed to assist in predicting diabetes risks using advanced machine learning techniques. With an intuitive GUI and diverse functionalities, this tool is perfect for individuals, researchers, and medical practitioners.

## **Features**

1. **Diabetes Risk Prediction**: Utilizes a Random Forest Classifier for accurate predictions.
2. **Bulk Data Analysis**: Accepts CSV files for analyzing multiple records at once.
3. **Image-Based Text Extraction**: Extracts text from medical images using Tesseract OCR.
4. **Real-Time Online Search**: Fetches medical information from reliable sources.
5. **Data Visualization**: Generates pie and bar charts for result interpretation.
6. **Comprehensive Reporting**:
   - Generates PDF reports for personalized recommendations.
   - Creates CSV reports for bulk analysis.
7. **User-Friendly GUI**: Built with CustomTkinter for an easy and seamless user experience.

---

## **Installation and Environment Setup** 

Follow these steps to set up the environment and run the application:

### 1. Clone the Repository
```bash
git clone https://github.com/sharna33/GlucoScholar.git
cd GlucoScholar
```
### 2. Install Dependencies
Ensure you have Python 3.8+ installed. Use `pip` to install the required dependencies:

```bash
pip install -r requirements.txt
```
### 3. Install Tesseract OCR
- Download and install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) for your platform.
- Update the Tesseract path in the `GlucoScholar.py` file:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
```
### 4. Additional Libraries
Ensure the following libraries are installed in your environment:
- `sqlite3`: Usually pre-installed with Python.
- `custom tkinter`: If not installed, run:
```bash
pip install customtkinter
```

---

## **Running the Application**

Start the GUI application:
```bash
python GlucoScholar_UI.py
```

---

## **Common Terminal Issues & Fixes** 

### 1. **`ModuleNotFoundError`**
If you encounter a missing module error:
- Run:
  ```bash
  pip install <module_name>
  ```

### 2. **Tesseract OCR Path Issue**
- Ensure the Tesseract OCR installation path is correctly specified in the code.

### 3. **GUI Not Displaying Properly**
- Ensure `tkinter` is installed:
  ```bash
  sudo apt-get install python3-tk
  ```

### 4. **Permission Errors on Mac/Linux**
- If permissions are denied while accessing files, run:
  ```bash
  chmod +x <file_name>
  ```

### 5. **Pillow (PIL) Errors**
- Upgrade `Pillow`:
  ```bash
  pip install --upgrade Pillow
  ```

### 6. **Matplotlib Errors**
- If `matplotlib` backends cause issues, add this code before importing:
  ```python
  import matplotlib
  matplotlib.use('Agg')
  ```

---

## **Project Structure**
`├── data   # save datasets and images`  
`├── GlucoScholar.py`   
`├── GlucoScholar_UI.py`   
`├── requirements.txt`

## **Contributors**
Sadia Rahman Sharna - https://github.com/sharna33   
Mst. meher Niger - https://github.com/Niger49  
Ania - https://github.com/ania48  

## **License**
This project is licensed under the MIT License.
