import tkinter as tk
from tkinter import filedialog
import PyPDF2
import os
import re
file_path = ""

def browse_file():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    file_name_label.config(text='File: ' + os.path.basename(file_path))

# You will be working on this function.
# Now, it reads the entire pdf file and converts to a large string
# and paste it in the analysis text box

def extract_info():
    global file_path
    if file_path:
        try:
            pdf_file = open(file_path, 'rb')
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            large_string = ""
            
            # this opens the file and extracts the text
            
            for page_num in range(len(pdf_reader.pages)):
                large_string += pdf_reader.pages[page_num].extract_text()

            pdf_file.close()
            
            # find all candidate info with regex pattern
            
            name_match = r'[A-Za-z]{2,20}(  ?[A-Za-z]{2,20}){1,2}'
            name = re.search(name_match, large_string)
            
            # first match the entire address, then use a second regex to find each specific component of the address 
            
            address_match = r'\d+\s+[\w\s]+[,.]?\s*\w+\s*[,.]?\s*\w+\s*[,.]?\s+\d{5}(-\d{4})?'
            address = re.search(address_match, large_string)
            house_match = r'^([^,\.]+)'
            house = re.search(house_match, address.group())
            city_match = r'(?<=[,.]\s)(\w+)'
            city = re.search(city_match, address.group())
            state_match = r'(\w+)(?=\s*[,.]?\s*\d{5}(-\d{4})?$)'
            state = re.search(state_match, address.group())
            zip_match = r'(\d{5}(-\d{4})?)$'
            zip = re.search(zip_match, address.group())
            
            phone_number_match = r'\s*(\+1\s*)?(?:\(\d{3}\)|\d{3})[-\s]*\d{3}[-\s]*\d{4}[-\s]*'
            phone_number = re.search(phone_number_match, large_string)
            
            email_match = r'[A-Za-z][A-Za-z0-9._%+-]* ?\.? ?[A-Za-z0-9._%+-]* ?@ ?[A-Za-z0-9.-]+ ?\.[A-Za-z]{2,}'
            email = re.search(email_match, large_string)
            
            local_match = r'(MN|Minnesota)(?=\s*[,.]?\s*\d{5}(-\d{4})?)'
            local = re.search(local_match, address.group())
            
            python_match = r'(?i)python'
            python = re.search(python_match, large_string)
            
            degree_match = r'Bachelors? of Science in Computer Science|Bachelor of Science: Computer Science'
            degree = re.search(degree_match, large_string)
            
            project_match = r'(?i:project|projects)'
            project = re.search(project_match, large_string)
            
            web_match = r'(Web)\s(Developer|Programmer|programming)'
            web = re.search(web_match, large_string)

            # insert the info into each textbox
            
            name_entry.delete(0, tk.END)
            name_entry.insert(tk.END, name.group())
            address_entry.delete(0, tk.END)
            address_entry.insert(tk.END, house.group())
            city_entry.delete(0, tk.END)
            city_entry.insert(tk.END, city.group())
            state_entry.delete(0, tk.END)
            state_entry.insert(tk.END, state.group())
            zip_entry.delete(0, tk.END)
            zip_entry.insert(tk.END, zip.group())
            phone_entry.delete(0, tk.END)
            phone_entry.insert(tk.END, phone_number.group())
            email_entry.delete(0, tk.END)
            email_entry.insert(tk.END, email.group())
            
            analysis_box.delete("1.0", tk.END)
            count = 0
            
            # the file application.txt contains the phone number of each candidate. It will search through this file to determine if candidate has applied
            
            with open("application.txt", "r") as file: 
                file_content = file.read()
            
            if phone_number.group() in file_content:
                analysis_box.insert("1.0", "Previously Applied: Yes")
            else:
                analysis_box.insert("1.0", "Previously Applied: No")
                with open("application.txt", "a") as file: 
                    file.write(phone_number.group())   
                    file.write("\n")

            # a qualified candidate must be local (MN), know Python, have a BS in Comp Sci, have side projects, and have web dev experience 
            # a candidate needs a score of at least 5 to be accepted. candidate gets a point for possessing each requirement

            analysis_box.insert(tk.END, "\n\n\n\n" )
            if local:
                count += 1
                analysis_box.insert(tk.END, "Local Resident\n")
            else:
                analysis_box.insert(tk.END, "Non-Local\n")
            if python:
                count += 1
                analysis_box.insert(tk.END, "Background Knowledge of Python\n")
            else:
                analysis_box.insert(tk.END, "No Python Skills\n")
            if degree:
                count += 1
                analysis_box.insert(tk.END, degree.group())
                analysis_box.insert(tk.END, "\n")
            else:
                analysis_box.insert(tk.END, "No Comp Sci Degree\n")
            if project:
                count += 1
                analysis_box.insert(tk.END, "Repository of Side Projects\n")
            else:
                analysis_box.insert(tk.END, "Lacks Project Portfolio\n")
            if web:
                count += 1
                analysis_box.insert(tk.END, "Professional Web Dev Experience\n")
            else:
                analysis_box.insert(tk.END, "No Web Dev Experience\n")
            if count >= 5:
                analysis_box.insert("3.0", "Candidate Accepted!")
            else: 
                analysis_box.insert("3.0", "Candidate Rejected.")
            
        except Exception as e:
            analysis_box.delete("1.0", tk.END)
            analysis_box.insert(tk.END, f"Error: {str(e)}")

# reset mmemory will erase all the displayed info and erase the file containing each candidate's phone number
def reset_memory():
    open("application.txt", "w").close()
    name_entry.delete(0, tk.END)
    address_entry.delete(0, tk.END)
    city_entry.delete(0, tk.END)
    state_entry.delete(0, tk.END)
    zip_entry.delete(0, tk.END)
    phone_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    analysis_box.delete("1.0", "end")

# Create the main window
root = tk.Tk()
root.title("Smart Resume reader")
root.geometry("650x580")
# First row: File browse button
file_button = tk.Button(root, text="Browse", command=browse_file)
file_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")
file_name_label = tk.Label(root, text="File:")
file_name_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
# Second row: Read button
extract_btn = tk.Button(root, text="Extract", command=extract_info)
extract_btn.grid(row=1, column=0, padx=10, pady=5, sticky="w")
reset_btn = tk.Button(root, text="Reset Memory", command=reset_memory)
reset_btn.grid(row=1, column=4, padx=10, pady=5, sticky="w")
# Third row: Name label and text box
name_label = tk.Label(root, text="Name:")
name_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
name_entry = tk.Entry(root, width=25)
name_entry.grid(row=2, column=1, padx=10, pady=5)
# Fourth row: Address label and text box
address_label = tk.Label(root, text="Address:")
address_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
address_entry = tk.Entry(root, width=25)
address_entry.grid(row=3, column=1, padx=10, pady=5)
# Fifth row: City label and text box
city_label = tk.Label(root, text="City:")
city_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
city_entry = tk.Entry(root, width=25)
city_entry.grid(row=4, column=1, padx=10, pady=5)
# Sixth row: State label and text box
state_label = tk.Label(root, text="State:")
state_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
state_entry = tk.Entry(root, width=25)
state_entry.grid(row=5, column=1, padx=10, pady=5)
# Seventh row: Zip code label and text box
zip_label = tk.Label(root, text="Zip Code:")
zip_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
zip_entry = tk.Entry(root, width=25)
zip_entry.grid(row=6, column=1, padx=10, pady=5)
# Eighth row: Phone number label and text box
phone_label = tk.Label(root, text="Phone Number:")
phone_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
phone_entry = tk.Entry(root, width=25)
phone_entry.grid(row=7, column=1, padx=10, pady=5)
# Ninth row: Email address label and text box
email_label = tk.Label(root, text="Email Address:")
email_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
email_entry = tk.Entry(root, width=25)
email_entry.grid(row=8, column=1, padx=10, pady=5)
# Tenth row: Multiline text box
text_label = tk.Label(root, text="Analysis:")
text_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
analysis_box = tk.Text(root, width=40, height=12)
analysis_box.grid(row=9, column=1, padx=10, pady=5)
root.mainloop()

