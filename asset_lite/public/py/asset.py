# import frappe
# import qrcode
# from io import BytesIO
# import base64
# from PIL import Image
# import traceback

# def generate_asset_qr(doc, method):
#     try:
#         # Debugging: Log that function was called
#         frappe.logger().debug(f"QR Generation started for asset {doc.name}")
        
#         # Check if QR code already exists
#         if doc.custom_asset_image:
#             frappe.logger().debug(f"Asset {doc.name} already has a QR code: {doc.custom_asset_image}")
#             return
        
#         # Generate QR code for the asset ID
#         qr = qrcode.QRCode(
#             version=1,
#             error_correction=qrcode.constants.ERROR_CORRECT_L,
#             box_size=10,
#             border=4,
#         )
#         qr.add_data(doc.name)  # Use asset ID as QR code data
#         qr.make(fit=True)
        
#         # Create an image from the QR Code
#         img = qr.make_image(fill_color="black", back_color="white")
        
#         # Save the image to a buffer
#         buffer = BytesIO()
#         img.save(buffer, format="PNG")
#         buffer.seek(0)
        
#         # Save QR code as a file attachment
#         file_name = f"asset_qr_{doc.name}.png"
        
#         # Create a file in ERPNext using the file_data method
#         file_doc = frappe.new_doc("File")
#         file_doc.file_name = file_name
#         file_doc.attached_to_doctype = "Asset"
#         file_doc.attached_to_name = doc.name
#         file_doc.attached_to_field = "custom_asset_image"  # Specify the field
#         file_doc.is_private = 0
        
#         # Save the file content
#         file_doc.save_file(buffer.getvalue(), file_name, is_private=0)
        
#         # Log the file URL
#         frappe.logger().debug(f"File created with URL: {file_doc.file_url}")
        
#         # Update the asset with the QR code image - using direct SQL for reliability
#         frappe.db.sql("""
#             UPDATE `tabAsset` 
#             SET custom_asset_image = %s 
#             WHERE name = %s
#         """, (file_doc.file_url, doc.name))
        
#         # Force a commit to ensure data is saved
#         frappe.db.commit()
        
#         frappe.logger().debug(f"QR Code generation complete for asset {doc.name}")
        
#     except Exception as e:
#         frappe.db.rollback()
#         err_msg = f"Error generating QR code for asset {doc.name}: {str(e)}\n{traceback.format_exc()}"
#         frappe.logger().error(err_msg)
#         frappe.log_error(err_msg, "Asset QR Code Generation Error")


# import frappe
# import requests
# from frappe.utils.file_manager import save_file

# def generate_asset_qr(doc, method):
#     docname = doc.name
#     if not docname:
#         return

#     qr_url = f"https://quickchart.io/qr?text={frappe.utils.encode(docname)}"
    
#     # Fetch QR image
#     response = requests.get(qr_url)
#     if response.status_code != 200:
#         frappe.throw("Failed to generate QR Code")

#     # Save file
#     file_name = f"{docname}-qr.png"
#     file_doc = save_file(
#         file_name,
#         content=response.content,
#         dt="Asset",
#         attached_to_field="custom_asset_image",
#         dn=docname,
#         decode=False,
#         is_private=False
#     )

#     # Attach file path to the custom image field
#     frappe.db.set_value("Asset", docname, "custom_asset_image", file_doc.file_url)
#     # return True

import frappe
import pyqrcode
import io
import base64
import urllib.parse

def generate_asset_qr(doc, method):
    docname = doc.name
    if not docname:
        frappe.throw("Document name is required.")

    # Check if a file is already attached
    existing_file = frappe.db.exists(
        "File",
        {
            "attached_to_doctype": "Asset",
            "attached_to_name": docname,
            "attached_to_field": "custom_attach_image"
        }
    )

    if existing_file:
        return  # QR already attached

    try:
        # Get full ERPNext site URL
        site_url = frappe.utils.get_url()

        # Build asset detail page URL
        asset_url = f"{site_url}/app/asset/{urllib.parse.quote(docname)}"

        # Log for debugging
        frappe.logger().debug(f"Generating offline QR for: {asset_url}")

        # --- Generate QR Code Offline ---
        qr_obj = pyqrcode.create(asset_url, error='H')  # High error correction

        buffer = io.BytesIO()
        qr_obj.png(buffer, scale=8)  # Scale 8 gives 500×500-ish resolution
        qr_png = buffer.getvalue()

        # Base64 encode
        encoded_content = base64.b64encode(qr_png).decode("utf-8")

        # Create File document
        file_doc = frappe.get_doc({
            "doctype": "File",
            "file_name": f"{docname}-qr.png",
            "attached_to_doctype": "Asset",
            "attached_to_name": docname,
            "attached_to_field": "custom_attach_image",
            "content": encoded_content,
            "decode": True,  # decode base64 back into file
            "is_private": 0
        })
        file_doc.insert(ignore_permissions=True)

        # Set link to Asset field
        frappe.db.set_value("Asset", docname, "custom_attach_image", file_doc.file_url)
        frappe.db.commit()

        frappe.logger().debug(f"QR code generated successfully for Asset: {docname}")

    except Exception as e:
        frappe.log_error(f"Error generating QR for asset {docname}: {str(e)}", "QR Code Error")
        raise


#import frappe
#import requests
#import base64
#import urllib.parse

#def generate_asset_qr(doc, method):
#    docname = doc.name
#    if not docname:
#        frappe.throw("Document name is required.")

#    # Check if a file is already attached
#    existing_file = frappe.db.exists(
#        "File",
#        {
#            "attached_to_doctype": "Asset",
#            "attached_to_name": docname,
#            "attached_to_field": "custom_attach_image"
#        }
#    )

#    if existing_file:
#        return  # Exit early if file already exists

#    try:
#        # Get the site URL from the configuration
#        site_url = frappe.utils.get_url()
        
#        # Create a direct link to the asset - ensure proper URL format
#        asset_url = f"{site_url}/app/asset/{urllib.parse.quote(docname)}"
        
#        # Log the URL for debugging
#        frappe.logger().debug(f"Asset URL for QR code: {asset_url}")
        
#        # Generate QR Code with the full URL - using higher resolution and error correction
#        qr_url = f"https://quickchart.io/qr?text={urllib.parse.quote(asset_url)}&size=500&margin=10&ecLevel=H"
#        response = requests.get(qr_url)
#        frappe.logger().debug(response.url)

#        if response.status_code != 200:
#            frappe.throw(f"Failed to generate QR code. Status code: {response.status_code}")

#        # Base64-encode the image content
#        encoded_content = base64.b64encode(response.content).decode("utf-8")

#        # Create new File document
#        file_doc = frappe.get_doc({
#            "doctype": "File",
#            "file_name": f"{docname}-qr.png",
#            "attached_to_doctype": "Asset",
#            "attached_to_name": docname,
#            "attached_to_field": "custom_attach_image",
#            "content": encoded_content,
#            "decode": True,
#            "is_private": 0
#        })
#        file_doc.insert(ignore_permissions=True)

 #       # Set file URL to the image field
#        frappe.db.set_value("Asset", docname, "custom_attach_image", file_doc.file_url)
#        frappe.db.commit()
        
#        # Log success
#        frappe.logger().debug(f"QR code generated successfully for asset {docname}")
        
#    except Exception as e:
#       frappe.log_error(f"Error generating QR code for asset {docname}: {str(e)}", "QR Code Error")
