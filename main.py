import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import CMYKColor, CMYKColorSep
import math

# Constants
WIDTH_A4 = A4[0]  # Width of A4a page in points (595.2756)
LABEL_HEIGHT = 21 * mm    # Label height: 21mm
SPACE_BETWEEN_LABELS = 4 * mm  # Space between labels: 4mm
MARGIN = 3 * mm           # Margin at edge of page: 3mm
LABELS_PER_ROW = 5        # 5 labels per row
MAGENTA_LINE_WIDTH = 1    # 1px line width for kiss_cut
PREFIX = "SK-"            # Prefix for barcode labels

# Define the ranges of labels to generate
LABEL_RANGES = [
    (1, 400),     # 0001 to 0400
    (801, 1000)   # 0801 to 1000
]

# Calculate label width based on page width and number of labels per row
LABEL_WIDTH = (WIDTH_A4 - 2 * MARGIN - (LABELS_PER_ROW - 1) * SPACE_BETWEEN_LABELS) / LABELS_PER_ROW

def create_barcode_labels_pdf(output_filename):
    # Calculate total number of labels
    total_labels = sum(end - start + 1 for start, end in LABEL_RANGES)
    
    # Calculate the number of rows needed
    rows_needed = math.ceil(total_labels / LABELS_PER_ROW)
    
    # Calculate the height needed for the page
    page_height = 2 * MARGIN + rows_needed * LABEL_HEIGHT + (rows_needed - 1) * SPACE_BETWEEN_LABELS
    
    # Create a new PDF document with custom page size
    custom_page_size = (WIDTH_A4, page_height)
    c = canvas.Canvas(output_filename, pagesize=custom_page_size)
    
    # Define spot color for kiss_cut (100% Magenta in CMYK)
    # Using CMYKColorSep for spot color
    kiss_cut_color = CMYKColorSep(0, 1, 0, 0, spotName='kiss_cut')
    
    # Create a 100% K (black) CMYK color for text and barcodes
    black_cmyk = CMYKColor(0, 0, 0, 1)  # 100% K in CMYK
    
    # Import necessary modules for barcode
    from reportlab.graphics.barcode import code128
    
    row = 0
    col = 0
    
    # Calculate barcode dimensions - 70% of label height
    barcode_height = LABEL_HEIGHT * 0.7
    
    # Process each range of labels
    for start_num, end_num in LABEL_RANGES:
        for i in range(start_num, end_num + 1):
            # Format the barcode text using the PREFIX variable
            code_text = f"{PREFIX}{i:04d}"
            
            # Calculate the position for this label
            x = MARGIN + col * (LABEL_WIDTH + SPACE_BETWEEN_LABELS)
            y = page_height - MARGIN - (row + 1) * LABEL_HEIGHT - row * SPACE_BETWEEN_LABELS
            
            # Draw the kiss cut line using the spot color
            c.setStrokeColor(kiss_cut_color)
            c.setLineWidth(MAGENTA_LINE_WIDTH)
            c.rect(x, y, LABEL_WIDTH, LABEL_HEIGHT, stroke=1, fill=0)
            
            # Set color to 100% black for barcode and text
            c.setFillColor(black_cmyk)
            c.setStrokeColor(black_cmyk)
            
            # Create barcode with increased width but still controlled
            barcode_obj = code128.Code128(code_text, barWidth=0.35*mm, barHeight=barcode_height)
            
            # Get the actual width of the generated barcode
            actual_barcode_width = barcode_obj.width
            
            # Calculate center positions horizontally
            barcode_x = x + (LABEL_WIDTH - actual_barcode_width) / 2
            
            # Position barcode higher in the label
            barcode_y = y + LABEL_HEIGHT - barcode_height - 2*mm
            
            # Draw the barcode
            barcode_obj.drawOn(c, barcode_x, barcode_y)
            
            # Ensure the text is positioned with clear separation from the barcode
            text_y = y + 1*mm  # Position text 2mm from bottom of label
            
            c.setFont("Helvetica", 8)
            c.drawCentredString(x + LABEL_WIDTH/2, text_y, code_text)
            
            # Move to next position
            col += 1
            if col >= LABELS_PER_ROW:
                col = 0
                row += 1
    
    # Save the PDF
    c.save()
    
    # Generate dynamic range descriptions using the PREFIX variable
    range_descriptions = []
    for start_num, end_num in LABEL_RANGES:
        range_descriptions.append(f"{PREFIX}{start_num:04d} to {PREFIX}{end_num:04d}")
    
    # Join the range descriptions with "and" for display
    ranges_text = " and ".join(range_descriptions)
    
    print(f"PDF created with {total_labels} barcode labels on a single page of dimensions {WIDTH_A4/mm:.1f}mm × {page_height/mm:.1f}mm.")
    print(f"Included ranges: {ranges_text}")

if __name__ == "__main__":
    output_file = "barcode_labels.pdf"
    create_barcode_labels_pdf(output_file)
    print(f"Barcode labels saved to {output_file}")
