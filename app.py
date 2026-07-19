import streamlit as st
from fpdf import FPDF
from datetime import datetime, timedelta
import re

st.set_page_config(page_title="Taurus RFQ Generator", page_icon="📄", layout="centered")

st.title("📄 Taurus Procurement RFQ Generator")
st.write("Paste your raw Purchase Requisition (PR) text below to instantly generate a standardized RFQ PDF.")

pr_text = str(st.text_area("Paste PR Text Here:", height=250))

def parse_pr(text):
    """Smarter parser to extract relevant fields from the PR text"""
    data = {"unit": "Taurus", "pr_num": "UNKNOWN", "items": [], "email": "", "phone": ""}
    
    if "Bezhan" in text or "BPC" in text:
        data["unit"] = "BPC"
    elif "QTT" in text:
        data["unit"] = "QTT"
    elif "SHO" in text:
        data["unit"] = "SHO"
        
    pr_match = re.search(r'(BPC-)?PR\d*-\d+-\w+', text)
    if pr_match:
        data["pr_num"] = pr_match.group(0)
        
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    data["email"] = email_match.group(0) if email_match else "procurement@taurusenergy.com"
    
    phone_match = re.search(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', text)
    data["phone"] = phone_match.group(0) if phone_match else "+964 XXX XXX XXXX"

    lines = text.split('\n')
    for line in lines:
        if "|" in line and any(char.isdigit() for char in line):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) > 5 and parts[0].replace('.', '').isdigit():
                data["items"].append({
                    "code": parts[1] if len(parts) > 1 else "",
                    "short_desc": parts[2] if len(parts) > 2 else "Item",
                    "long_desc": parts[3] if len(parts) > 3 else "",
                    "uom": parts[-2] if len(parts) >= 3 else "Each",
                    "qty": parts[-3] if len(parts) >= 3 else "1"
                })
                
    if not data["items"]:
        data["items"].append({
            "code": "000000",
            "short_desc": "MANUAL ENTRY REQUIRED",
            "long_desc": "Could not parse items. Please check PR formatting.",
            "uom": "Each",
            "qty": "0"
        })
    return data

if st.button("Generate RFQ PDF", type="primary"):
    if not pr_text.strip():
        st.warning("Please paste some PR text first.")
    else:
        parsed = parse_pr(pr_text)
        b_unit = parsed["unit"]
        pr_num = parsed["pr_num"]
        items_list = parsed["items"]
        contact_email = parsed["email"]
        contact_phone = parsed["phone"]
        
        today = datetime.now()
        rfq_date = today.strftime("%B %d, %Y")
        return_by = (today + timedelta(days=5)).strftime("%B %d, %Y")
        
        if pr_num.startswith("BPC-"):
            rfq_number = f"SCED-{pr_num}"
        else:
            rfq_number = f"SCED-BPC-{pr_num}" if b_unit == "BPC" else f"SCED-{pr_num}"
        
        if b_unit == "BPC":
            contact_name = "Ayar Nadhm Ghafour"
            company_name = "Bezhan Pet Co. for Oil Refining LTD."
            delivery_address = "Bezhan Pet Co. for Oil Refining Ltd, Onex Holding Ltd.\nSulaymaniyah, Postal code 46001, Iraq"
        else:
            contact_name = "Ayar Ghafour"
            company_name = "Taurus Arm Company for Power Generation Ltd."
            delivery_address = "Taurus Arm Company for Power Generation Ltd.\nBazian Power Plant/Kani Shaetan/Sulaymaniyah, Iraq"

        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.set_text_color(26, 54, 93)
                self.cell(0, 10, 'RFQ - Request for Quotation', 0, 1, 'C')
                self.ln(5)

        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'RFQ Date:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(50, 6, rfq_date, 0, 0)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'Ref No:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, rfq_number, 0, 1)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'Return by:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(50, 6, return_by, 0, 0)
        
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'From:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, contact_name, 0, 1)
        
        pdf.cell(90, 6, '', 0, 0)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'Email:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, contact_email, 0, 1)

        pdf.cell(90, 6, '', 0, 0)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 6, 'Phone:', 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, contact_phone, 0, 1)
        pdf.ln(5)
        
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'Delivery Address:', 0, 1, 'L', fill=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 6, delivery_address, 0, 'L', fill=True)
        pdf.ln(5)
        
        pdf.cell(0, 6, f'This Purchase/Service is subject to {company_name} Terms and Conditions.', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 9)
        pdf.set_fill_color(26, 54, 93)
        pdf.set_text_color(255, 255, 255)
        cols = [10, 80, 20, 20, 30, 30]
        headers = ['Sr.', 'Description', 'UOM', 'Qty', 'Unit Price', 'Total Price']
        for i in range(len(headers)):
            pdf.cell(cols[i], 8, headers[i], 1, 0, 'C', fill=True)
        pdf.ln()
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(0, 0, 0)
        for index, item in enumerate(items_list, 1):
            desc_text = f"{item.get('code', '')} {item['short_desc']}\n{item['long_desc']}"
            lines = pdf.get_string_width(desc_text) / (cols[1] - 2)
            row_height = max(6, 5 * (int(lines) + 1))
            
            x_start = pdf.get_x()
            y_start = pdf.get_y()
            
            pdf.cell(cols[0], row_height, str(index), 1, 0, 'C')
            pdf.set_xy(x_start + cols[0], y_start)
            pdf.multi_cell(cols[1], 5, desc_text, 1, 'L')
            
            pdf.set_xy(x_start + cols[0] + cols[1], y_start)
            pdf.cell(cols[2], row_height, item['uom'], 1, 0, 'C')
            pdf.cell(cols[3], row_height, item['qty'], 1, 0, 'C')
            pdf.cell(cols[4], row_height, '', 1, 0, 'C')
            pdf.cell(cols[5], row_height, '', 1, 1, 'C')
            
            if pdf.get_y() < y_start + row_height:
                pdf.set_y(y_start + row_height)
                
        # --- NEW SECTION: TERMS AND CONDITIONS ---
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(26, 54, 93)
        pdf.cell(0, 10, f'Terms and Conditions - {company_name}', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(0, 0, 0)
        tc_text = (
            "1. ACCEPTANCE: This Request for Quotation (RFQ) does not constitute a binding offer to buy. "
            "A formal Purchase Order must be issued for any agreement to be valid.\n\n"
            "2. PRICING: All prices must be quoted in the specified currency, be inclusive of applicable taxes unless "
            "stated otherwise, and remain valid for a minimum of 30 days.\n\n"
            "3. DELIVERY: Time is of the essence. Please clearly specify lead times and delivery schedules in your quotation.\n\n"
            "4. QUALITY: All goods and services must meet the exact specifications outlined in this RFQ and be free from defects.\n\n"
            "5. COMPLIANCE: The vendor agrees to comply with all applicable local laws, regulations, and industry standards "
            "while fulfilling this request."
        )
        pdf.multi_cell(0, 5, tc_text)
        # -----------------------------------------
                
        pdf_output = pdf.output(dest='S').encode('latin-1')
        
        st.success("🎉 RFQ Document compiled successfully!")
        st.download_button(
            label="📥 Download RFQ PDF",
            data=pdf_output,
            file_name=f"{rfq_number}.pdf",
            mime="application/pdf"
        )
