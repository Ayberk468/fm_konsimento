
from flask import Flask, render_template, request, send_file
import qrcode
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
import io
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        shipper = request.form.get("shipper")
        consignee = request.form.get("consignee")
        notify = request.form.get("notify")
        blno = request.form.get("blno")
        container = request.form.get("container")
        goods = request.form.get("goods")

        qr_path = "static/qr_temp.png"
        qr = qrcode.make(f"https://fmlojistik.com/konşimento/{blno}")
        qr.save(qr_path)

        def draw_overlay():
            packet = io.BytesIO()
            c = canvas.Canvas(packet, pagesize=A4)
            c.setFont("Helvetica", 10)
            c.drawString(20 * mm, 265 * mm, shipper)
            c.drawString(110 * mm, 265 * mm, consignee)
            c.drawString(20 * mm, 255 * mm, notify)
            c.drawString(20 * mm, 245 * mm, f"BL No: {blno}")
            c.drawString(110 * mm, 245 * mm, f"Container: {container}")
            c.drawString(20 * mm, 235 * mm, goods)
            c.drawImage(qr_path, 170 * mm, 250 * mm, width=25 * mm, height=25 * mm)
            c.save()
            packet.seek(0)
            return PdfReader(packet)

        template_pdf = "MNSEA605.pdf"
        output_pdf = f"cikti_{blno}.pdf"
        existing_pdf = PdfReader(template_pdf)
        output = PdfWriter()
        overlay_pdf = draw_overlay()
        page = existing_pdf.pages[0]
        page.merge_page(overlay_pdf.pages[0])
        output.add_page(page)

        with open(output_pdf, "wb") as f:
            output.write(f)

        return send_file(output_pdf, as_attachment=True)

    return render_template("form.html")
