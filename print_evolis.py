
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
        file_name = "pdf_temp_dec.pdf"
        with open(file_name, "wb") as f:
            f.write(pdf_data)

        # Get default printer
        impressoras = listar_impressoras_disponiveis()
        impressora = impressoras[3]
        
        namee = utils.get_printer_name()
        print(namee)
        print(impressora)
        
        printer_name = win32print.SetDefaultPrinterW(impressora)

           
        
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
