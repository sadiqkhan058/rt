import streamlit as st
from PIL import Image, ImageOps
import os
import pandas as pd
import openpyxl
from io import BytesIO

# Import your nn.enhancer module (replace this with the actual module)
import nn  # Assuming nn is the module where the enhancer function is located  

# Initialize session state to hold the DataFrame
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame(
        columns=["Student Name", "Student ID", "Image 1", "Image 2", "Image 3"])

# Initialize session state for enhanced images if not present
if 'enhanced_images' not in st.session_state:
    st.session_state.enhanced_images = []  # Initialize it as an empty list

# Set up the input fields
st.title("Fingerprint Enhancer - Batch Entry")

# Function to reset input fields
def reset_fields():
    st.session_state.student_name = ""
    st.session_state.student_id = None
    st.session_state.uploaded_images = None

col1, col2 = st.columns([3, 1])

with col2:
    if st.button('Clear Input Data'):
        reset_fields()  # Clears fields

# Initialize fields in session state if not already present
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

if 'student_id' not in st.session_state:
    st.session_state.student_id = None

if 'uploaded_images' not in st.session_state:
    st.session_state.uploaded_images = None

# Input fields for the current student
student_name = st.text_input("Enter the student's name", value=st.session_state.student_name)
student_id = st.text_input("Enter the student's ID",  value=st.session_state.student_id)

# Image uploader widget for multiple images (up to 3)
uploaded_images = st.file_uploader("Upload up to 3 images", type=["jpg", "jpeg", "png", "bmp"], accept_multiple_files=True)

# Update session state with new inputs
if student_name or student_id or uploaded_images:
    st.session_state.student_name = student_name
    st.session_state.student_id = student_id
    st.session_state.uploaded_images = uploaded_images


# Create an empty list to store enhanced images temporarily for this submission
enhanced_images_temp = []

# Function to enhance images using nn.enhancer and apply a horizontal flip
def enhance_image(image_file):
    try:
        # Save the uploaded image to a temporary path
        image_path = os.path.join("temp", image_file.name)
        os.makedirs("temp", exist_ok=True)
        with open(image_path, "wb") as f:
            f.write(image_file.getbuffer())  # Save file

        # Enhance the image using the external nn.enhancer function
        final_output_path = nn.enhancer(image_path)
        
        # Open the enhanced image
        enhanced_image = Image.open(final_output_path)
        
        # Flip the image horizontally
        enhanced_image = ImageOps.mirror(enhanced_image)

        return enhanced_image
    except Exception as e:
        st.error(f"Error enhancing image: {e}")
        return None

# Process and enhance each uploaded image without displaying them
if uploaded_images:
    if len(uploaded_images) > 3:
        st.warning("Please upload a maximum of 3 images.")
    else:
        # Enhance each image in the background
        for image_file in uploaded_images:
            # Enhance the fingerprint image and flip it horizontally
            enhanced_image = enhance_image(image_file)
            if enhanced_image:
                enhanced_images_temp.append(enhanced_image)
            else:
                enhanced_images_temp.append(None)

# Handle form submission and display entered details
if st.button("Submit and Add Another Student"):
    # Add the student information to the DataFrame
    new_data = pd.DataFrame({
        "Student Name": [student_name],
        "Student ID": [student_id],
        "Image 1": [uploaded_images[0].name if uploaded_images and len(uploaded_images) > 0 else None],
        "Image 2": [uploaded_images[1].name if uploaded_images and len(uploaded_images) > 1 else None],
        "Image 3": [uploaded_images[2].name if uploaded_images and len(uploaded_images) > 2 else None]
    })
    st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
    
    # Store enhanced images in session state for this student
    st.session_state.enhanced_images.append(enhanced_images_temp)
    st.success("Student details added successfully!")
    
    # Reset input fields for the next student
    reset_fields()

# Display DataFrame with images, enhanced images, and a delete button
st.markdown("***____***"*22)
st.markdown("### Student Data with Enhancer Images")
st.markdown("***____***"*22)
header_cols = st.columns(7)
header_cols[0].write("**Sign No**")
header_cols[1].write("**Name**")
header_cols[2].write("**Student ID**")
header_cols[3].write("**Enhance 1**")
header_cols[4].write("**Enhance 2**")
header_cols[5].write("**Enhance 3**")
header_cols[6].write("**Delete**")

# Loop through the DataFrame rows to display each entry and the corresponding images
rows_to_delete = []  # List to store the index of rows to be deleted
for index, row in st.session_state.df.iterrows():
    cols = st.columns(7)  # Create 7 columns for each row
    cols[0].write(f"{index + 1}")  # Row number
    cols[1].write(row['Student Name'])
    cols[2].write(row['Student ID'])

    # Display the enhanced images if they exist
    if index < len(st.session_state.enhanced_images):
        enhanced_row = st.session_state.enhanced_images[index]

        # Conditionally check if enhanced_row has enough images before accessing each index
        if len(enhanced_row) > 0 and enhanced_row[0]:
            cols[3].image(enhanced_row[0], caption="Enhanced Image 1", use_column_width=True)
        else:
            cols[3].warning("No image uploaded.")

        if len(enhanced_row) > 1 and enhanced_row[1]:
            cols[4].image(enhanced_row[1], caption="Enhanced Image 2", use_column_width=True)
        else:
            cols[4].warning("No image uploaded.")

        if len(enhanced_row) > 2 and enhanced_row[2]:
            cols[5].image(enhanced_row[2], caption="Enhanced Image 3", use_column_width=True)
        else:
            cols[5].warning("No image uploaded.")

    # Add a delete button for each row
    if cols[6].button("Delete", key=f"delete_{index}"):
        # Remove the row immediately
        st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
        st.session_state.enhanced_images.pop(index)  # Remove corresponding enhanced images
        st.success("Row deleted successfully!")  # Provide immediate feedback
        break  # Break the loop to avoid re-rendering after deletion

    # Draw a line to separate different student data
    st.markdown("***---***"*47)

# Create an Excel writer
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    # Save the text data
    st.session_state.df.to_excel(writer, sheet_name='Student Data', index=False)

    # Get the worksheet to insert images
    workbook = writer.book
    worksheet = writer.sheets['Student Data']

    # Set column widths
    worksheet.column_dimensions['D'].width = 25
    worksheet.column_dimensions['E'].width = 25
    worksheet.column_dimensions['F'].width = 25

    # Add images for each student in the corresponding columns
    for i, enhanced_row in enumerate(st.session_state.enhanced_images):
        row_num = i + 2  # Adjust for header row

        # Set the row height to fit the image size
        worksheet.row_dimensions[row_num].height = 120  # Adjust as needed

        # Only insert images if they exist
        if len(enhanced_row) > 0 and enhanced_row[0]:  # Check if Image 1 exists
            img_data = BytesIO()
            enhanced_row[0].save(img_data, format="PNG")
            img_data.seek(0)
            img = openpyxl.drawing.image.Image(img_data)
            img.width = 100  # Adjust width
            img.height = 100  # Adjust height
            img.anchor = f'D{row_num}'  # Insert into column D 
            worksheet.add_image(img)

        if len(enhanced_row) > 1 and enhanced_row[1]:  # Check if Image 2 exists
            img_data = BytesIO()
            enhanced_row[1].save(img_data, format="PNG")
            img_data.seek(0)
            img = openpyxl.drawing.image.Image(img_data)
            img.width = 100  # Adjust width
            img.height = 100  # Adjust height
            img.anchor = f'E{row_num}'  # Insert into column E
            worksheet.add_image(img)

        if len(enhanced_row) > 2 and enhanced_row[2]:  # Check if Image 3 exists
            img_data = BytesIO()
            enhanced_row[2].save(img_data, format="PNG")
            img_data.seek(0)
            img = openpyxl.drawing.image.Image(img_data)
            img.width = 100  # Adjust width
            img.height = 100  # Adjust height
            img.anchor = f'F{row_num}'  # Insert into column F
            worksheet.add_image(img)

# Download the Excel file
st.download_button(label="Download Excel File", data=output.getvalue(), file_name="student_data_with_images.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")




