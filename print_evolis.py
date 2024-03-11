#!/usr/bin/env python3
#
# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

import os
import sys
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from flask_cors import CORS
import evolis
import utils
from flask import Flask, request, jsonify
import requests
import win32print
import win32ui
from PIL import Image, ImageWin
import fitz  # Import PyMuPDF



EXIT_OK = '0'
EXIT_FAILURE = '1'


app = Flask(__name__)
CORS(app)


def main():
    """
    This function prints a card with KO ribbon.
    In this function, we use a custom bitmap for the overlay panel.
    If we hadn't used a custom bitmap then the overlay panel would have been fully printed.
    """
  

@app.route('/print_card', methods=['POST'])
def print_card():
    if request.method == 'POST':
        # Call the function to print the card
        try:
            # Get PDF link from request
            link_pdf = request.json.get('card')
            print("Imprimindo a sua cartao "+ link_pdf)
            if link_pdf is None:
                return jsonify({'error': 'Link do PDF não fornecido'}), 400

       
            response = requests.get(link_pdf)
            pdf_data = response.content

           # Get original file name with extension
            file_name_with_extension = os.path.basename(link_pdf)
            
            # Caminho completo do arquivo na pasta "examples"
            file_path = os.path.join(folder_path, file_name_with_extension)
            
            # Save PDF temporarily na pasta "examples"
            with open(file_path, "wb") as f:
                f.write(pdf_data)
            

            # Especificando o caminho completo para a pasta "examples"
          
            # Verificando se a pasta "examples" existe, senão, criando-a
            
            print("clicado")
           
            name = utils.get_printer_name()
            co = evolis.Connection(name, False)

            if not co.is_open():
                print("> Error: can't open printer context.")
                return EXIT_FAILURE

            ps = evolis.PrintSession(co)

            # Set main image:
           
            if not ps.set_image(evolis.CardFace.FRONT, file_path):
                print("> Error: can't load file" + file_path)
                return EXIT_FAILURE


            # Set Overlay image:
            
            """
            
            if not ps.set_overlay(evolis.CardFace.FRONT, "resources/overlay.bmp"):
                        print("> Error: can't load file resources/overlay.bmp")
                        return EXIT_FAILURE

            """
                
            # Print:
            print("> Start printing...")
            r = ps.print()
            print(f"> Print result {str(r)}")
            print(file_name)

            co.close()
            return EXIT_OK
            #else:
            #  return "Only POST requests are allowed."
        except Exception as e:
            print(e)
            return jsonify({'error': str(e)}), 500

@app.route('/imprimir_declaracao', methods=['POST'])
def imprimir_declaracao():
    try:
        # Get PDF link from request
        link_pdf = request.json.get('link')
        print("Imprimindo a sua declaração ")
        if link_pdf is None:
            return jsonify({'error': 'Link do PDF não fornecido'}), 400

        # Download the PDF
        response = requests.get(link_pdf)
        pdf_data = response.content

        # Save PDF temporarily
        file_name = "pdf_temp.pdf"
        with open(file_name, "wb") as f:
            f.write(pdf_data)

        # Get default printer
        printer_name = win32print.GetDefaultPrinter()

        # Create printing context
        hDC = win32ui.CreateDC()
        hDC.CreatePrinterDC(printer_name)

        # Open the PDF with PyMuPDF
        pdf_document = fitz.open(file_name)

        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            width, height = pix.width, pix.height

            # **Scale factor (adjust as needed)**
            scale = 8  # Example: halves the size

            # Calculate scaled image dimensions
            scaled_width = int(width * scale)
            scaled_height = int(height * scale)

            # Create and resize image from PDF page
            img = Image.frombytes("RGB", [width, height], pix.samples)
            img = img.resize((scaled_width, scaled_height))

            # Print the scaled image
            dib = ImageWin.Dib(img)
            hDC.StartDoc(file_name)
            hDC.StartPage()
            dib.draw(hDC.GetHandleOutput(), (0, 0, scaled_width, scaled_height))
            hDC.EndPage()

        hDC.EndDoc()
        hDC.DeleteDC()

        # Close and delete temporary PDF
        del pdf_document
        os.unlink(file_name)

        return jsonify({'message': 'PDF impresso com sucesso'}), 200

    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
