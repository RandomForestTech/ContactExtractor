import fitz
import spacy
import re

# nlp = spacy.load("en_core_web_sm")
nlp = spacy.load("en_core_web_lg")

EMAIL_PATTERN = r'\b[\w\.-]+@[\w\.-]+\.\w+\b'
PHONE_PATTERN = r'(\+?\d[\d\s\-\(\)]{8,})'


ROLE_KEYWORDS = ['ceo', 'cto', 'vp', 'president', 'officer', 'cfo', 'chief', 'head', 'executive', 'director', 'manager', 'coo', 'cmo',
 'cio', 'consultant', 'leader', 'operations', 'digital', 'marketing', 'development', 'business', 'finance', 'sales',
 'it', 'security', 'legal', 'hr', 'hrd', 'hrp', 'recruitment', 'recruiters', 'recruiting', 'recruitment', 'recruiters',
 'recruiting', 'recruitment', 'recruiters', 'marketing', 'development', 'nominating', 'business', 'committee',
 'finance', 'sales', 'it', 'security', 'legal', 'hr', 'hrd', 'hrp', 'minister', 'secretary', 'senate', 'senator',
 'commissioner', 'chairman', 'writer', 'producer', 'editor', 'journalist', 'author', 'co-founder', 'founder',
 'founder & chairman', 'entrepreneur', 'advisor', 'investment', 'global', 'banking', 'transaction', 'legal', 'finance',
 'it', 'security', 'marketing', 'sales', 'operations', 'audit', 'brand', 'communications', 'strategy', 'office',
 'group brand and communications', 'global corporate banking', 'group audit', 'group legal and compliance',
 'group operations and technology', 'group strategy and transformation', "group", "human", "resources", "delivery",
 'taxation', 'corporate', "facilities", "infrastructure", "co-founder", "co-head", "co-director", "co-chair"]


def extract_text_from_pdf(pdf_path, page_numbers):
    print(pdf_path, "pdf_path")
    doc = fitz.open(pdf_path)
    text = ""
    for num in page_numbers:
        if 0 <= num < len(doc):
            text += doc[num].get_text()
    return text


def extract_entities_with_spacy_working_fine_basic(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    people = []
    i = 0
    print(lines, "lines123444")
    while i < len(lines):
        block_lines = []

        # Try to collect 2 consecutive lines as a name block if they look like a name
        if i < len(lines) - 1:
            doc1 = nlp(lines[i])
            doc2 = nlp(lines[i + 1])
            persons1 = [ent.text for ent in doc1.ents if ent.label_ == "PERSON"]
            persons2 = [ent.text for ent in doc2.ents if ent.label_ == "PERSON"]

            if persons1 and persons2:
                name = f"{persons1[0]} {persons2[0]}"
                i += 2
            elif persons1:
                name = persons1[0]
                i += 1
            else:
                i += 1
                continue
        else:
            i += 1
            continue

        # Now collect next 1–3 lines as potential role
        role_lines = []
        for j in range(3):
            if i + j < len(lines):
                if any(word in lines[i + j].lower() for word in ROLE_KEYWORDS):
                    role_lines.append(lines[i + j])
        role = " ".join(role_lines)

        # Try detecting company on name or role lines
        company = ""
        doc_context = nlp(" ".join(role_lines))
        orgs = [ent.text for ent in doc_context.ents if ent.label_ == "ORG"]
        if orgs:
            company = orgs[0]
        else:
            company = "COMPANY NAME "  # fallback default

        people.append({
            "name": name.strip(),
            "role": role.strip(),
            "company": company
        })

        i += len(role_lines)

    return people

def extract_entities_with_spacy_and_contacts(text, used_indices=None, company_name=None):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    print(lines, "lines123444")
    if used_indices is None:
        used_indices = set()

    people = []
    new_used_indices = set()
    i = 0

    while i < len(lines):
        line = lines[i]
        doc = nlp(line)
        persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

        if not persons:
            i += 1
            continue

        for person in persons:
            name = person
            block_indices = [i]

            # Role detection after this line
            role_lines = []
            role_line_indices = []
            for j in range(1, 4):  # Look ahead
                if i + j < len(lines):
                    role_line = lines[i + j]
                    print(role_line, "role_line")
                    role_words = role_line.split()
                    role_words = [word.lower() for word in role_words]
                    print(role_words, "role_words")
                    if any(word in role_words for word in ROLE_KEYWORDS):
                        print(role_line, "role_line1111")
                        role_lines.append(role_line)
                        role_line_indices.append(i + j)
                    else:
                        break  # Stop at unrelated line

            role = " ".join(role_lines)

            # Company detection
            doc_context = nlp(role)
            orgs = [ent.text for ent in doc_context.ents if ent.label_ == "ORG"]
            company = company_name if company_name else orgs[0] if orgs else "COMPANY NAME"

            # Extract contact details (phone & email) from nearby lines
            contact_lines = lines[i:i + 4]  # Check current and next 3 lines
            emails = [email.group() for email in (re.search(EMAIL_PATTERN, l) for l in contact_lines) if email]
            phones = [phone.group() for phone in (re.search(PHONE_PATTERN, l) for l in contact_lines) if phone]

            email = emails[0] if emails else "N/A"
            phone = phones[0] if phones else "N/A"

            new_used_indices.update(block_indices + role_line_indices)
            people.append({
                "name": name.strip(),
                "role": role.strip(),
                "company": company,
                "email": email.strip(),
                "phone": phone.strip()
            })

        i += 1

    used_indices.update(new_used_indices)

    # Retry logic
    remaining_lines = [line for idx, line in enumerate(lines) if idx not in used_indices]
    if new_used_indices and remaining_lines:
        print("\n Running second pass on remaining lines...\n")
        remaining_text = "\n".join(remaining_lines)
        extra_people = extract_entities_with_spacy_and_contacts(remaining_text, used_indices=used_indices,
                                                                company_name=company_name)
        people.extend(extra_people)

    return people


if __name__ == "__main__":

    text = extract_text_from_pdf("/home/jai/Downloads/infosys-ar-24-14-15.pdf", [0])  # First 2 pages
    results = extract_entities_with_spacy_and_contacts(text)
    for r in results:
        print(r)