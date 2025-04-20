from django.shortcuts import render
from nameextractor.models import UploadedFile, PersonDetails, Company, Role
from nameextractor.services import extract_text_from_pdf, extract_entities_with_spacy_and_contacts
from django.contrib.auth.decorators import login_required


@login_required
def upload_view(request):
    if request.method == 'POST':
        # Retrieve the uploaded file
        uploaded_file = request.FILES.get('pdf_file')
        if not uploaded_file:
            return render(request, 'upload.html', {'error': 'Please upload a file.'})

        # Save the uploaded file into the UploadedFile model
        uploaded_instance = UploadedFile.objects.create(
            file=uploaded_file,
            original_name=uploaded_file.name
        )

        # Retrieve form inputs
        company_name = request.POST.get('company', '')  # Optional company name from form
        pages = request.POST.get('pages', '').strip()  # Example: "1,2,3"
        
        if not pages:
            return render(request, 'upload.html', {'error': 'Please provide the page numbers.'})
        
        try:
            # Convert the provided page numbers into a list of integers
            page_numbers = list(map(int, pages.split(',')))
            page_numbers = [int(page)-1  for page in page_numbers]
            # Get the file path for the uploaded file
            file_path = uploaded_instance.file.path  # Full physical path of the uploaded file
            # Extract text from the file using the specified pages
            text = extract_text_from_pdf(file_path, page_numbers)  # Assuming service returns text on specific pages
            # Extract entities (names, roles, companies, etc.) from the extracted text
            extracted_people = extract_entities_with_spacy_and_contacts(text, company_name=company_name)
            # Save extracted data to PersonDetails, linking it to the UploadedFile
            for person in extracted_people:
                # Create or update Role object
                role_title = person.get('role', '').strip()
                if role_title:
                    role_obj, _ = Role.objects.get_or_create(title=role_title)
                else:
                    role_obj = None  # Handle cases where role is not available

                # Create or update Company object
                company_name = person.get('company', '').strip()
                if company_name:
                    company_obj, _ = Company.objects.get_or_create(name=company_name)
                else:
                    company_obj = None  # Handle cases where company is not available

                # Create PersonDetails and link to Role and Company
                PersonDetails.objects.create(
                    name=person.get('name'),
                    role=role_obj,  # Link to Role object
                    company=company_obj,  # Link to Company object
                    email=person.get('email', None),
                    phone=person.get('phone', None),
                    source_file=uploaded_instance,  # Link to the uploaded file
                    page_numbers=pages  # Save the page numbers the person was extracted from
                )

        except Exception as e:
            print(e, "rrrrrrrrrrrrrrrrr")
            # Handle errors during file processing or text extraction
            return render(request, 'upload.html', {'error': f'An error occurred: {str(e)}'})
        print(extracted_people, "extracted_people")
        # If successful, display the extracted people in the template
        return render(request, 'upload.html', {'people': extracted_people})

    # For GET request, display the upload form
    return render(request, 'upload.html')

@login_required
def filter_people_view(request):
    # Fetch filters from the request
    company_filter = request.GET.get('company', '')
    role_filter = request.GET.get('role', '')
    name_filter = request.GET.get('name', '')

    # Retrieve unique company and role values for dropdowns
    companies = Company.objects.all()
    roles = Role.objects.all()

    # Start with all PersonDetails objects and apply filters
    people = PersonDetails.objects.all()

    if company_filter:
        people = people.filter(company__name__icontains=company_filter)

    if role_filter:
        people = people.filter(role__title__icontains=role_filter)

    if name_filter:
        people = people.filter(name__icontains=name_filter)

    # Render the new filter page
    return render(request, 'filter_people.html', {
        'people': people,
        'companies': companies,
        'roles': roles,
        'company_filter': company_filter,
        'role_filter': role_filter,
        'name_filter': name_filter,
    })
