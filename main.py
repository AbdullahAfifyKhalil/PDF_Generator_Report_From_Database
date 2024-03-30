import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from database import Database

# Configure Jinja2 environment for HTML templates
env = Environment(
    loader=FileSystemLoader(searchpath="./"),
    autoescape=select_autoescape(['html', 'xml'])
)

# Load the HTML template
template = env.get_template('template.html')
def process_incident_data(incident, db):
    """Process incident data to include dynamic sections for fields and separate sections for media."""
    incident_data = incident[1]  # incident[1] contains structured incident data.
    sections_info = []

    # Initialize variables for Google Maps URL and GPS coordinates
    google_maps_url = None
    gps_coordinates = None
    map_image_url = None

    # Function to generate Google Maps URL
    if incident_data:
        # Iterate over each section in the incident data
        for section in incident_data.get('sections', []):
            for field in section.get('fields', []):
                if field.get('fieldType', '') == 'gps':
                    latitude = field.get('lat', None)
                    longitude = field.get('lng', None)

                    # Check if both latitude and longitude are available
                    if latitude is not None and longitude is not None:
                        gps_coordinates = f"{latitude},{longitude}"
                        break 

            # Construct the URL for Google Maps Static API if GPS coordinates are available
            if gps_coordinates:
                google_maps_api_key = "Google_Maps_API_Key"
                google_maps_url = f"https://www.google.com/maps/?q={latitude},{longitude}"
                map_image_url = f"https://maps.googleapis.com/maps/api/staticmap?center={latitude},{longitude}&zoom=15&size=600x300&maptype=roadmap&markers=color:red%7C{latitude},{longitude}&key={google_maps_api_key}"

    # Process non-media sections
    for section in incident_data.get('sections', []):
        # a list to hold all fields, including images and standard text fields
        fields = []

        # Function to process individual fields
        def process_field(field):
            if field.get('fieldValue', '').strip():
                field_value = field.get('fieldValue', '').strip()
                if field_value.startswith("image:"):
                    uuid = field_value.split(":")[1]
                    q = f"SELECT path, type, \"mimeType\" FROM media_items WHERE uuid = '{uuid}'"
                    db.cur.execute(q)
                    media_item = db.cur.fetchone()
                    if media_item:
                        media_url = media_item[0]
                        return {
                            'fieldTitle': field.get('fieldTitle', ''),
                            'value': f'<img src="{media_url}" alt="Image">',
                            'isImage': True
                        }
                else:
                    return {
                        'fieldTitle': field.get('fieldTitle', ''),
                        'value': field_value,
                        'isImage': False
                    }

        # Process standard fields in the section
        for field in section.get('fields', []):
            processed_field = process_field(field)
            if processed_field:
                fields.append(processed_field)
        if fields:  # Check if the main section has any fields to display
            sections_info.append({
                'title': section.get('title', ''),
                'fields': fields,
                'type': 'fields'  # Indicating this is a standard field section
            })

        # Additional logic for processing sub-sections such as 'injuries', 'damages', etc.
        sub_sections = ['injuries', 'damages', 'witnesses', 'vehicles']
        for sub_section_name in sub_sections:
            sub_section_data = section.get(sub_section_name, [])
            sub_section_fields = []
            for item in sub_section_data:
                for field in item.get('fields', []):
                    processed_field = process_field(field)
                    if processed_field:
                        sub_section_fields.append(processed_field)
            if sub_section_fields:
                sections_info.append({
                    'title': sub_section_name.capitalize(), 
                    'fields': sub_section_fields,
                    'type': 'fields'  # Maintaining consistent section type for simplicity
                })

    # Process media sections
    media_section = {'title': 'Media', 'media': [], 'type': 'media'}
    for section in incident_data.get('sections', []):
        for media in section.get('media', []):
            if 'type' in media and 'uuid' in media:
                q = f"SELECT path, type, \"mimeType\" FROM media_items WHERE uuid = '{media['uuid']}'"
                db.cur.execute(q)
                media_item = db.cur.fetchone()
                if media_item:
                    media_url = media_item[0]
                    media_section['media'].append({
                        'type': media_item[1],
                        'url': media_url,
                        'mimeType': media_item[2]
                    })

    if media_section['media']:
        sections_info.append(media_section)

    return sections_info, google_maps_url, gps_coordinates, map_image_url


def generate_pdf(html_content, pdf_path):
    """Generate PDF using WeasyPrint."""
    HTML(string=html_content).write_pdf(pdf_path, stylesheets=[CSS(filename='styles.css')])
    print(f"PDF generated: {pdf_path}")

def main():
    db = Database()

    # Example incident ID
    incident_id = 45823



 #46048  
    incident = db.fetch_incident(incident_id)

    if not incident:
        print("Incident not found.")
        db.close()
        return

    user_group_id = incident[3]
    groups = db.fetch_groups(user_group_id) if user_group_id is not None else []

    # Pass the db instance as the second argument to process_incident_data
    sections_info, google_maps_url, gps_coordinates, map_image_url = process_incident_data(incident, db)

    # Prepare data for the template
    data = {
        'incident': incident,
        'groups': groups,
        'sections_info': sections_info,
        'google_maps_url': google_maps_url,
        'gps_coordinates': gps_coordinates,
        'map_image_url': map_image_url,
    }
    
    # Render the HTML content
    html_content = template.render(data=data)

    # Generate PDF using WeasyPrint
    pdf_path = "incident_report.pdf"
    generate_pdf(html_content, pdf_path)

    db.close()

if __name__ == "__main__":
    main()
