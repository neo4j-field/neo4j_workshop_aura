import time
import argparse
import logging

import pandas as pd
from os import path

from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))

logger = logging.getLogger(__name__)
logging.basicConfig(level='INFO')


# configure spacing
startx = 4.25*inch
starty = 9.5*inch
tab = cm
linedist = 25

# file contents
header = "Neo4j Workshop"
subheader = "Building Smarter GenAI Apps with Knowledge Graphs"
line1 = "1. Login at:  https://workspace.neo4j.io/connection/connect"
line1a = "Your Personal Credentials"
paragraph1 = '''Connection URL: <b>{0}</b> <BR/> \
                Database user: <b>neo4j</b> <BR/> \
                Password: <b>{1}</b>'''
line2 = "2. Open genai-workshop.ipynb on GitHub"
line2a =  "github.com/neo4j-product-examples/genai-workshop/"
line3 ="3. Click the Colab link towards the top of the file to open in Colab"
line4 = "Post-Workshop References"
paragraph2 = '''Learning Resources: <font color="blue"> <u>neo4j.com/generativeai/#resources</u> </font> <BR/> \
                Tools & Integrations: <font color="blue"> <u>neo4j.com/labs/genai-ecosystem/</u></font> <BR/> \
                Upcoming Events: <font color="blue"> <u>neo4j.com/generativeai/#h-upcoming-events</u></font> <BR/>'''

# images
logo = './handout_images/logo.jpg'
qrcode = './handout_images/qr_code.jpg'
colab = './handout_images/colab.jpg'

my_Style = ParagraphStyle('My Para style',
                            fontName='Vera',
                            # backColor='#F1F1F1',
                            fontSize=12,
                            # borderColor='#FFFF00',
                            # borderWidth=2,
                            borderPadding=(20,20,20),
                            leading=20,
                            alignment=0
                            )


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str, help="filename of csv with readable passwords")
    return parser.parse_args()


def create_handouts(filename):
    df = pd.read_csv(filename, dtype=object)
    nameroot = path.splitext(filename)[0]
    c = canvas.Canvas('handouts_' + nameroot + '.pdf', pagesize=letter)

    # create one page per login
    for ix, ival in df.iterrows():
        """Yes, this is janky/brittle to content changes in the positioning.
        If we use this more I will spend more time iterating/improving to make
        positions relative or error if things overlap / go off page."""

        # draw header, subheader and item 1 lines
        c.setFont('VeraBd', 20)
        c.drawCentredString(startx, starty, header)
        c.setFont('VeraBd', 14)
        c.drawCentredString(startx,starty-linedist, subheader)
        c.setFont('Vera', 12)
        c.drawString(1*inch, starty-linedist*3, line1)
        c.drawString(1.2*inch, starty-linedist*4, line1a)

        # connection details as indented paragraph block
        p1=Paragraph(paragraph1.format(ival['connection_url'], ival['newpassword']),my_Style)
        p1.wrapOn(c,600,50)
        p1.drawOn(c, 1.5*inch, starty-linedist*7)

        # item 2
        c.drawString(1*inch, starty-linedist*8, line2)
        c.drawString(1.2*inch, starty-linedist*10, line2a)
        c.drawImage(qrcode, 6*inch,6*inch, width=100,height=100,mask=None)

        # item 3
        c.drawString(1*inch, starty-linedist*12, line3)
        c.drawImage(colab, 2*inch,3.75*inch, width=300,height=86,mask=None)

        # item 4
        c.setFont('VeraBd', 14)
        c.drawCentredString(startx, 3*inch, line4)
        c.setFont('VeraIt', 12)

        # resources paragraph
        p2=Paragraph(paragraph2,my_Style)
        p2.wrapOn(c,600,50)
        p2.drawOn(c, 1.2*inch, inch + 60)
        c.drawImage(logo, 3.25*inch,1*inch, width=150,height=53,mask=None)

        # add page numbers
        page_num = c.getPageNumber()
        c.setFont('Vera', 12)
        c.drawRightString(7.5*inch, 1*inch, str(page_num))

        # this saves / ends the page
        c.showPage()

    # save the file
    c.save()


if __name__ == '__main__':
    args = cli()
    filename = args.filename

    start = time.time()
    create_handouts(filename)
    logger.info("Time to create handouts: {}s".format(time.time()-start))
